from collections import Counter, defaultdict
from functools import partial

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Playlist, PlaylistSong


class Command(RhymeCommand):
    @property
    def help(self):
        return "Command-line playlist management"

    def handle(self, *args, **options):
        key = None
        selected = None
        while key != "q":
            if selected is None:
                selected = self.select_playlist()
            self.print_details(selected)
            key = input("What to do? (S)elect a different playlist, (L)ist, (R)ename, (D)elete, (C)reate, (Q)uit? ").lower()
            if key == "s":
                selected = self.select_playlist()
            elif key == "l":
                for index, song in enumerate(selected.songs):
                    print(f"{index + 1}) {song}")
            elif key == "r":
                selected.name = input("New name? ")
                selected.save()
            elif key == "d":
                selected.delete()
                selected = None
            elif key == "c":
                selected = Playlist.empty_playlist()
                selected.name = input("New name? ")
                selected.save()

    def print_details(self, playlist):
        print(playlist.name)
        print(f"    {len(playlist.songs)} song(s)")
        if playlist.song_filters:
            print(f"        {playlist.song_filters}")
        if playlist.album_filters:
            print(f"        {playlist.album_filters}")
        if playlist.omni_filter:
            print(f"        [{playlist.omni_filter}]")
        playlist_songs = PlaylistSong.objects.filter(playlist_id=playlist.id)
        if playlist_songs.count():
            inclusions = playlist_songs.filter(inclusion=True)
            exclusions = playlist_songs.filter(inclusion=False)
            print(f"        +{inclusions.count()} songs(s), -{exclusions.count()} songs")

    def select_playlist(self):
        playlists = Playlist.objects.all().order_by("name")
        key = None
        while key is None:
            self.print_numbered_list(playlists)
            key = input("Playlist? ")
            try:
                key = int(key) - 1
                return playlists[key]
            except (IndexError, ValueError):
                pass
            key = None
