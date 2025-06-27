from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rhyme.models import Album, Artist, Disc, Song, Track


class Command(BaseCommand):
    @property
    def help(self):
        return "Import a new album based on command-line input"

    def handle(self, *args, **options):
        album_name = input("Album name? ")
        album_year = input("Album year? ")
        album_artist = input("Artist (blank for multiple)? ")
        disc_count = int(input("Number of discs? "))
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
        self.new_artists = []
        for disc_index in range(1, disc_count + 1):
            if has_disc_names:
                discs.append(Disc(
                    name=input(f"Name of disc {disc_index}? "),
                    ordinal=disc_index,
                    album=album,
                ))

            disc_suffix = f" on disc {disc_index}" if multidisc else ""
            track_count = int(input(f"Number of tracks{disc_suffix}? "))
            for track_index in range(1, track_count + 1):
                song_id = input(f"Track {track_index} name or id? ")
                try:
                    song = Song.objects.get(id=int(song_id))
                except ValueError:
                    song = self._build_song(
                        song_id,
                        track_index,
                        artist=album_artist,
                        album_name=album.name if not is_mix else None,
                        album_year=album_year
                    )

                songs.append(song)

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

    def _build_song(self, name, track_index, artist=None, album_name=None, album_year=None):
        song_artist = artist or input(f"Track {track_index} artist? ")
        time = None
        while not time:
            try:
                time = input(f"Track {track_index} length? ")
                minutes, seconds = time.split(":")
                minutes = int(minutes)
                seconds = int(seconds)
            except ValueError:
                time = None

        artist = Artist.objects.filter(name=song_artist).first()
        if not artist:
            artist = Artist(name=song_artist)
            artist.save()
            self.new_artists.append(artist)

        album_name = album_name or input("Album name? ")
        filename = "/".join([x for x in [artist.name, album_name, name] if x]) + ".mp3"

        song = Song(
            name=name,
            artist=artist,
            filename=filename,
            time=minutes * 60 + seconds,
            year=album_year or input("Year? "),
        )
        song.save()
        return song
