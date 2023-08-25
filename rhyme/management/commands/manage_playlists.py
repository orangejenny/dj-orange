from collections import Counter, defaultdict
from functools import partial

from django.core.management.base import BaseCommand

from rhyme.models import Playlist, PlaylistSong


class Command(BaseCommand):
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
            key = input("What to do? (S)elect, (R)ename, (D)elete, (Q)uit? ").lower()
            if key == "s":
                selected = self.select_playlist()
            elif key == "r":
                selected.name = input("New name? ")
                selected.save()
            elif key == "d":
                selected.delete()
                selected = None

        def print_details(self, playlist):
            print(selected.name)
            print(f"    {len(selected.songs)} song(s)")
            if selected.song_filters:
                print(f"        {selected.song_filters}")
            if selected.album_filters:
                print(f"        {selected.album_filters}")
            if selected.omni_filter:
                print(f"        [{selected.omni_filter}]")
            playlist_songs = PlaylistSong.objects.filter(playlist_id=selected.id)
            if playlist_songs.count():
                inclusions = playlist_songs.filter(inclusion=True)
                exclusions = playlist_songs.filter(inclusion=False)
                print(f"        +{inclusions.count()} songs(s), -{exclusions.count()} songs")

    def select_playlist(self):
        playlists = Playlist.objects.all().order_by("name")
        key = None
        while key is None:
            for index, playlist in enumerate(playlists):
                print(f"{index + 1}) {playlist.name}")
            key = input("Playlist? ")
            try:
                key = int(key) - 1
                return playlists[key]
            except (IndexError, ValueError):
                pass
            key = None
