import json
import os
import re
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rhyme.models import Album, Artist, Disc, Song, Track


class Command(BaseCommand):
    @property
    def help(self):
        return "Import a new album based on command-line input"

    def add_arguments(self, parser):
        parser.add_argument("--meta", type=str, help="Path to a JSON file produced by parse_mp3_meta")

    def handle(self, *args, **options):
        meta = options.get("meta")
        if meta:
            with open(os.path.expanduser(meta), "r", encoding="utf-8") as f:
                self.track_metadata = json.load(f)
        else:
            self.track_metadata = []

        meta_album = self._most_common(m.get("album") for m in self.track_metadata)
        meta_year = self._most_common(m.get("year") for m in self.track_metadata)

        album_name = self._prompt("Album name", meta_album)
        album_year = input("Album year (blank for multiple)? ")
        album_artist = input("Artist (blank for multiple)? ")
        disc_count = int(self._prompt("Number of discs", 1))
        multidisc = disc_count > 1
        has_disc_names = multidisc and input("Are discs named (y/n)? ").lower() == "y"
        is_mix = input("Is this a mix (y/n)? ").lower() == "y"

        album = Album(
            name=album_name,
            date_acquired=timezone.now(),
            is_mix=is_mix
        )
        album.save()

        discs = []
        songs = []
        tracks = []
        metadata_index = 0
        self.new_artists = []
        for disc_index in range(1, disc_count + 1):
            if has_disc_names:
                discs.append(Disc(
                    name=input(f"Name of disc {disc_index}? "),
                    ordinal=disc_index,
                    album=album,
                ))

            disc_suffix = f" on disc {disc_index}" if multidisc else ""
            track_count = int(self._prompt(f"Number of tracks{disc_suffix}", len(self.track_metadata)))
            for track_index in range(1, track_count + 1):
                print(f"Track {track_index}")
                metadata = self.track_metadata[metadata_index] if self.track_metadata else {}
                name = self._prompt(f"Track {track_index} name", metadata.get("title"))
                song_artist = self._prompt(f"Track {track_index} artist", metadata.get("artist") or album_artist)
                if self._prompt(f"New song (y/n)", "y").lower() == "y":
                    song = self._build_song(
                        track_index,
                        metadata=metadata,
                        name=name,
                        artist=song_artist,
                        album_name=album.name if not is_mix else None,
                        album_year=album_year,
                    )
                else:
                    song = self._find_song(name, song_artist)

                songs.append(song)
                metadata_index = metadata_index + 1

                tracks.append(Track(
                    ordinal=track_index,
                    disc=disc_index,
                    song=song,
                    album=album,
                ))

        print(f"{album.name} by {album_artist}")
        for track in tracks:
            print(f"Disc {track.disc}, Track {track.ordinal}: {track.song.name} by {track.song.artist.name}, {track.song.time}")

        if input("Save tracks (y/n)? ").lower() == "y":
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

    def _find_song(self, name, artist):
        qs = Song.objects.all()
        if name:
            qs = qs.filter(name__icontains=name)
        if artist:
            qs = qs.filter(artist__name__icontains=artist)
        matches = list(qs.select_related("artist")[:20])

        if matches:
            print("Matches:")
            for i, song in enumerate(matches, 1):
                print(f"  {i}. [{song.id}] {song.name} by {song.artist.name} ({song.year})")

        while True:
            choice = input("Enter result number, or song id: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                continue
            if 1 <= idx <= len(matches):
                return matches[idx - 1]
            song = Song.objects.filter(id=idx).first()
            if song:
                return song
            print(f"No song found with id {idx}.")

    def _most_common(self, values):
        filtered = [v for v in values if v]
        return Counter(filtered).most_common(1)[0][0] if filtered else None

    def _prompt(self, label, default=None):
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{label}{suffix}? ").strip()
        return value if value else default

    def _build_song(self, track_index, metadata=None, name=None, artist=None, album_name=None, album_year=None):
        metadata = metadata or {}
        meta_year = metadata.get("year")
        meta_duration = metadata.get("duration")
        if meta_duration:
            meta_time = f"{meta_duration // 60}:{meta_duration % 60:02d}"
        else:
            meta_time = None

        year = self._prompt(f"Track {track_index} year", meta_year or album_year)

        time = None
        while not time:
            try:
                raw = self._prompt(f"Track {track_index} length", meta_time)
                minutes, seconds = re.split(r"\D+", raw)
                minutes = int(minutes)
                seconds = int(seconds)
                time = raw
            except (ValueError, TypeError):
                time = None

        artist_obj = Artist.objects.filter(name=artist).first()
        if not artist_obj:
            artist_obj = Artist(name=artist)
            artist_obj.save()
            self.new_artists.append(artist_obj)

        album_name = album_name or self._prompt("Album name")
        filename = "/".join([x for x in [artist_obj.name, album_name, name] if x]) + ".mp3"

        song = Song(
            name=name,
            artist=artist_obj,
            filename=filename,
            time=minutes * 60 + seconds,
            year=year or self._prompt("Year"),
        )
        song.save()
        return song
