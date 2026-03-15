import os
import re
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rhyme.models import Album, Artist, Disc, Song, Track


def _prompt(label, default=None):
    """Prompt the user, showing [default] if provided. Empty input returns default."""
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}? ").strip()
    if not value and default is not None:
        return str(default)
    return value


def _parse_m3u(path):
    """Return ordered list of absolute audio file paths from an M3U file."""
    path = os.path.expanduser(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith("#")
    ]


def _read_metadata(file_path):
    """Return a dict of metadata for an audio file using mutagen."""
    from mutagen import File as MutagenFile

    audio = MutagenFile(file_path, easy=True)
    if not audio:
        return {}

    def first(key):
        val = audio.get(key)
        return val[0] if val else None

    duration = getattr(audio.info, "length", None)
    if duration:
        duration = int(round(duration))

    return {
        "title": first("title"),
        "artist": first("artist"),
        "album": first("album"),
        "year": first("date"),
        "tracknumber": first("tracknumber"),
        "discnumber": first("discnumber"),
        "duration": duration,
    }


def _most_common(values):
    filtered = [v for v in values if v]
    if not filtered:
        return None
    return Counter(filtered).most_common(1)[0][0]



def _format_time(seconds):
    if seconds is None:
        return None
    return f"{seconds // 60}:{seconds % 60:02d}"


class Command(BaseCommand):
    @property
    def help(self):
        return "Import a new album based on command-line input"

    def add_arguments(self, parser):
        parser.add_argument("--playlist", type=str, help="Path to an M3U file")

    def handle(self, *args, **options):
        playlist_path = options.get("playlist")
        track_metadata = []

        if playlist_path:
            file_paths = _parse_m3u(playlist_path)
            track_metadata = [_read_metadata(p) for p in file_paths]

        # Derive album-level defaults from metadata
        meta_album = _most_common([m.get("album") for m in track_metadata])
        meta_year = _most_common([m.get("year") for m in track_metadata])
        meta_artist = _most_common([m.get("artist") for m in track_metadata])

        album_name = _prompt("Album name", meta_album)
        album_year = _prompt("Album year", meta_year)
        album_artist = _prompt("Artist (blank for multiple)", meta_artist or "")
        disc_count = int(_prompt("Number of discs", 1 if playlist_path else None))
        if playlist_path and disc_count > 1:
            raise ValueError("Playlist import only supports single-disc albums.")
        multidisc = disc_count > 1
        has_disc_names = multidisc and _prompt("Are discs named (y/n)", "n").lower() == "y"
        is_mix = _prompt("Is this a mix (y/n)", "n").lower() == "y"

        album = Album(
            name=album_name,
            date_acquired=timezone.now(),
            is_mix=is_mix,
        )
        album.save()


        discs = []
        songs = []
        tracks = []
        self.new_artists = []

        for disc_index in range(1, disc_count + 1):
            if has_disc_names:
                discs.append(Disc(
                    name=input(f"Name of disc {disc_index}? "),
                    ordinal=disc_index,
                    album=album,
                ))

            disc_suffix = f" on disc {disc_index}" if multidisc else ""
            meta_track_count = len(track_metadata) or None
            track_count = int(_prompt(f"Number of tracks{disc_suffix}", meta_track_count))

            for track_index in range(1, track_count + 1):
                track_meta = track_metadata[track_index - 1] if track_index <= len(track_metadata) else {}
                song = self._get_or_build_song(
                    track_index,
                    track_meta,
                    album_artist=album_artist,
                    album_name=album.name if not is_mix else None,
                    album_year=album_year,
                )
                songs.append(song)
                tracks.append(Track(
                    ordinal=track_index,
                    disc=disc_index,
                    song=song,
                    album=album,
                ))

        print(f"\n{album.name} by {album_artist or 'Various'}")
        for track in tracks:
            print(f"Disc {track.disc}, Track {track.ordinal}: {track.song.name} by {track.song.artist.name}, {track.song.time}")

        if input("\nSave tracks (y/n)? ").lower() == "y":
            with transaction.atomic():
                for disc in discs:
                    disc.save()
                for track in tracks:
                    track.save()
            print(f"Created {album.name} with {disc_count} disc(s), {len(tracks)} tracks.")
        else:
            album.delete()
            for artist in self.new_artists:
                artist.delete()
            for song in songs:
                song.delete()

    def _get_or_build_song(self, track_index, track_meta, album_artist, album_name, album_year):
        meta_name = track_meta.get("title")
        meta_artist = track_meta.get("artist") or album_artist or None
        meta_duration = track_meta.get("duration")
        meta_year = track_meta.get("year") or album_year

        if meta_name:
            print(f"\nTrack {track_index}: \"{meta_name}\" by {meta_artist or '?'}, {_format_time(meta_duration) or '?'}")
        else:
            print(f"\nTrack {track_index}:")

        if _prompt("Does this song already exist in the database (y/n)", "n").lower() == "y":
            return self._find_existing_song(track_index, meta_name, meta_artist)

        return self._build_song(
            track_index,
            meta_name=meta_name,
            meta_artist=meta_artist,
            meta_duration=meta_duration,
            meta_year=meta_year,
            album_name=album_name,
            album_year=album_year,
            album_artist=album_artist,
        )

    def _find_existing_song(self, track_index, meta_name, meta_artist):
        search_name = _prompt(f"Track {track_index} song name to search", meta_name)
        search_artist = _prompt(f"Track {track_index} artist to search", meta_artist)

        qs = Song.objects.all()
        if search_name:
            qs = qs.filter(name__icontains=search_name)
        if search_artist:
            qs = qs.filter(artist__name__icontains=search_artist)
        matches = list(qs.select_related("artist")[:20])

        if not matches:
            print("No matches found. Creating a new song instead.")
            return self._build_song(
                track_index,
                meta_name=meta_name,
                meta_artist=meta_artist,
                album_name=None,
                album_year=None,
                album_artist=None,
            )

        print("Matches:")
        for i, song in enumerate(matches, 1):
            print(f"  {i}. {song.name} by {song.artist.name} ({song.year}) — {_format_time(song.time)}")

        while True:
            choice = input("Pick a number (or blank to create new instead): ").strip()
            if not choice:
                return self._build_song(
                    track_index,
                    meta_name=meta_name,
                    meta_artist=meta_artist,
                    album_name=None,
                    album_year=None,
                    album_artist=None,
                )
            try:
                idx = int(choice)
                if 1 <= idx <= len(matches):
                    return matches[idx - 1]
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(matches)}, or leave blank.")

    def _build_song(self, track_index, meta_name=None, meta_artist=None, meta_duration=None,
                    meta_year=None, album_name=None, album_year=None, album_artist=None):
        name = _prompt(f"Track {track_index} name", meta_name)
        song_artist_name = _prompt(f"Track {track_index} artist", meta_artist or album_artist)

        time = None
        default_time = _format_time(meta_duration)
        while not time:
            try:
                raw = _prompt(f"Track {track_index} length (M:SS)", default_time)
                minutes, seconds = re.split(r"\D+", raw)
                minutes = int(minutes)
                seconds = int(seconds)
                time = raw
            except ValueError:
                time = None

        artist = Artist.objects.filter(name=song_artist_name).first()
        if not artist:
            artist = Artist(name=song_artist_name)
            artist.save()
            self.new_artists.append(artist)

        resolved_album_name = album_name or _prompt("Album name")
        filename = "/".join([x for x in [artist.name, resolved_album_name, name] if x]) + ".mp3"

        song = Song(
            name=name,
            artist=artist,
            filename=filename,
            time=minutes * 60 + seconds,
            year=meta_year or album_year or _prompt("Year"),
        )
        song.save()
        return song
