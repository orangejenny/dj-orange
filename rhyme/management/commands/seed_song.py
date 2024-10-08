from django.db.models import Q

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Song, Tag, Track
from rhyme.plex import create_plex_playlist

from datetime import datetime
import random


class Command(RhymeCommand):
    def handle(self, *args, **options):
        seed = self.get_song()
        print(f"Seed: {seed}")

        # Basic limits
        ocean = Song.objects.filter(Q(rating__gte=3) | Q(starred=True))
        ocean = ocean.exclude(tag__name="christmas")
        ocean = ocean.exclude(artist__genre="soundtrack", rating__lte=3)

        print(f"Start with {ocean.count()} songs")
        if seed.mood is not None:
            ocean = ocean.filter(mood__in={seed.mood, seed.mood + 1, seed.mood - 1})
        print(f"Mood reduces it to {ocean.count()}")
        if seed.energy is not None:
            ocean = ocean.filter(energy__in={seed.energy, seed.energy + 1, seed.energy - 1})
        print(f"Energy reduces it to {ocean.count()}")
        if seed.artist.genre:
            ocean = ocean.filter(artist__genre=seed.artist.genre)
        print(f"Genre reduces it to {ocean.count()}")

        # Limit to related songs
        lake = {}
        seed_album_ids = self.album_ids(seed)
        seed_tags = seed.tags()
        years = set(Tag.objects.filter(category="years").values_list("name", flat=True))
        for i, song in enumerate(ocean):
            if i % 100 == 0:
                print(f"Processed {i} of {len(ocean)}")
            match = False
            lake[song.id] = 0.9

            if seed_album_ids & self.album_ids(song):
                match = True
            else:
                lake[song.id] *= 0.8

            if song.artist == seed.artist:
                match = True
            elif self.genre_match(seed, song):
                match = True
                lake[song.id] *= 0.8
            else:
                lake[song.id] *= 0.6

            tags = self.common_tags(seed_tags, song)
            if self.tag_match(tags):
                match = True
            else:
                lake[song.id] *= 0.7

            if tags & years:
                match = True
            else:
                lake[song.id] *= 0.7

            if self.matrix_match(seed, song):
                match = True
            else:
                lake[song.id] *= 0.5

            if not match:
                lake.pop(song.id)
        print(f"Lake size: {len(lake)}, {min(lake.values())}-{max(lake.values())}")

        # Limit by odds
        while input("Reduce (y/n)? ").lower() == "y":
            pool = {}
            for song_id, odds in lake.items():
                if random.random() < odds:
                    pool[song_id] = odds
            lake = pool
            print(f"Pool size: {len(pool)}, {min(lake.values())}-{max(lake.values())}")

        # Display and export
        for song_id in lake:
            print(Song.objects.get(id=song_id))

        command = input("\nExport to (r)hyme, (p)lex? ").lower()
        if command == "r":
            playlist = Playlist.empty_playlist()
            playlist.name = input("Name? ")
            playlist.save()
            for song_id in lake.keys():
                PlaylistSong(playlist_id=playlist.id, song_id=song_id, inclusion=True).save()
        elif command == "p":
            playlist_name = input("Name? ")
            create_plex_playlist(playlist_name, Song.objects.filter(id__in=lake.keys()))

    def album_ids(self, song):
        return Track.objects.filter(song=song).values_list("album_id", flat=True)

    def genre_match(self, song1, song2):
        if song1.artist.genre is None or song2.artist.genre is None:
            return None
        return song1.artist.genre == song2.artist.genre

    def matrix_match(self, song1, song2):
        if song1.mood is None or song2.mood is None:
            return False
        if song1.energy is None or song2.energy is None:
            return False
        return song1.mood == song2.mood and song1.energy == song2.energy

    def tag_match(self, tags):
        return len(tags) > 1

    def common_tags(self, tags, song):
        return set(tags) & set(song.tags())
