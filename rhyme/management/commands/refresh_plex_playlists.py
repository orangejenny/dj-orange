from plexapi.exceptions import NotFound

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Playlist, Song
from rhyme.plex import create_plex_playlist, plex_server, plex_library


class Command(RhymeCommand):
    @property
    def help(self):
        return "Update song list for all plex-based playlists"

    def add_arguments(self, parser):
        parser.add_argument('--playlist-id', help="Update only this playlist")
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--playlist', action='store_true', help="Select a playlist")
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **options):
        if options.get('playlist_id'):
            playlists = Playlist.objects.filter(id=options.get('playlist_id'))
        elif options.get('playlist', False):
            playlists = [self.get_playlist()]
        else:
            playlists = Playlist.objects.all().reverse()

        print(f"Found {len(playlists)} playlists")

        # These are slow, so do them after the potential user input
        self.server = plex_server()
        self.library = plex_library(self.server)

        for index, playlist in enumerate(playlists):
            print(f"({index} of {len(playlists)}) Refreshing {playlist.name} ({playlist.id}) which has {playlist.plex_count} songs")
            self.refresh_playlist(playlist, force=options.get('force', False), quiet=options.get('quiet', False))

    def refresh_playlist(self, playlist, force=False, quiet=False):
        rhyme_keys = {song.plex_key for song in playlist.songs if song.plex_key}

        if not force and len(rhyme_keys) == playlist.plex_count:
            print("This looks fairly up to date, returning early")
            return

        try:
            plex_playlist = self.server.playlist(playlist.name)
        except NotFound:
            print(f"Could not find \"{playlist.name}\" on plex.")
            print(f"\"{playlist.name}\" has {len(playlist.songs)} songs and these filters: {playlist.all_filters}")
            command = "i" if quiet else None
            while command not in ['d', 'c', 'r', 'i']:
                command = input(f"Ignore (i), create on plex (c), delete from rhyme (d), or rename in rhyme (r)? ")
            if command == "d":
                playlist.delete()
            elif command == "c":
                create_plex_playlist(playlist.name, playlist.songs)
            elif command == "r":
                playlist.name = input("New name? ")
                playlist.save()
                return self.refresh_playlist(playlist, force=force)
            return

        plex_items = {item.key: item for item in plex_playlist.items()}

        keys_to_remove = plex_items.keys() - rhyme_keys
        for key in keys_to_remove:
            plex_playlist.removeItem(plex_items[key])

        keys_to_add = rhyme_keys - plex_items.keys()
        items_to_add = []
        for key in keys_to_add:
            try:
                items_to_add.append(self.library.fetchItem(key))
            except NotFound:
                pass
        if items_to_add:
            plex_playlist.addItems(items_to_add)

        if playlist.plex_count != len(rhyme_keys):
            playlist.plex_count = len(rhyme_keys)
            playlist.save()

        print(f"Refreshed {playlist} which now has {playlist.plex_count} songs")
