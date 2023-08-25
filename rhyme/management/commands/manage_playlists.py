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
            key = input("What to do? (R)ename, (D)elete, (S)kip, (Q)uit? ").lower()
            if key == "r":
                selected.name = input("New name? ")
                selected.save()
            elif key == "d":
                selected.delete()
            selected = None

    def get_processor(self):
        model = input(f"Model ({' / '.join(self.models)}, q to quit)? ")
        if model == "q":
            return None
        try:
            return {
                Processor.SONG: SongProcessor,
                Processor.ALBUM: AlbumProcessor,
                Processor.ARTIST: ArtistProcessor,
            }[model]()
        except KeyError:
            return self.get_processor()

    def select_playlist(self):
        playlists = Playlist.objects.all().order_by("name")
        key = None
        while key is None:
            for index, playlist in enumerate(playlists):
                print(f"{index + 1}) {playlist.name}")
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
            key = input("Playlist? ")
            try:
                key = int(key) - 1
                return playlists[key]
            except (IndexError, ValueError):
                pass
            key = None
