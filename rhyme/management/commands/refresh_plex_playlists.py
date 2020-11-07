from django.core.management.base import BaseCommand

from plexapi.exceptions import NotFound

from rhyme.models import Playlist
from rhyme.views import create_plex_playlist    # TODO: move to helpers/utils
from rhyme.plex import plex_server, plex_library


class Command(BaseCommand):
    @property
    def help(self):
        return "Update song list for all plex-based playlists"

    def add_arguments(self, parser):
        parser.add_argument('--playlist-id', help="Update only this playlist")
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        self.server = plex_server()
        self.library = plex_library(self.server)

        if options.get('playlist_id'):
            playlists = Playlist.objects.filter(id=options.get('playlist_id'))
        else:
            playlists = Playlist.objects.all()

        for playlist in playlists:
            self.refresh_playlist(playlist, force=options.get('force', False))

    def refresh_playlist(self, playlist, force=False):
        print(f"Refreshing {playlist.name} ({playlist.id}) which has {playlist.plex_count} songs")

        rhyme_keys = {song.plex_key for song in playlist.songs if song.plex_key}

        if not force and len(rhyme_keys) == playlist.plex_count:
            print("This looks fairly up to date, returning early")
            return

        try:
            plex_playlist = self.server.playlist(playlist.name)
        except NotFound:
            if input(f"Could not find {playlist.name}. Delete (y/n)? ") == "y":
                playlist.delete()
            elif input(f"Recreate on plex (y/n) ?") == "y":
                create_plex_playlist(playlist.name, Song.list(song_filters=playlist.song_filters,
                                                              album_filters=playlist.album_filters,
                                                              omni_filer=playlist.omni_filer))
            return

        plex_items = {item.key: item for item in plex_playlist.items()}

        keys_to_remove = plex_items.keys() - rhyme_keys
        for key in keys_to_remove:
            plex_playlist.removeItem(plex_items[key])

        keys_to_add = rhyme_keys - plex_items.keys()
        items_to_add = [self.library.fetchItem(key) for key in keys_to_add]
        if items_to_add:
            plex_playlist.addItems(items_to_add)

        if playlist.plex_count != len(rhyme_keys):
            playlist.plex_count = len(rhyme_keys)
            playlist.save()

        print(f"Refreshed {playlist} which now has {playlist.plex_count} songs")
