from django.core.management.base import BaseCommand

import os
from shutil import copy


class Command(BaseCommand):
    @property
    def help(self):
        return "Copy files from a playlist to a disk location"

    def add_arguments(self, parser):
        parser.add_argument('location', help="Disk location")
        parser.add_argument('playlists', help="M3U playlist locations", nargs="*")
        parser.add_argument('--force', action='store_true')

    def check_path(self, path):
        if not os.path.exists(path):
            print(f"{path} does not exist")
            exit(1)

    def handle(self, *args, **options):
        self.force = options.get('force', False)

        self.location = options.get("location")
        self.check_path(self.location)
        location_files = os.listdir(self.location)
        if len(location_files) and input(f"Remove {len(location_files)} files from {self.location}? (y/n) ").lower() == "y":
            for f in location_files:
                f = os.path.join(self.location, f)
                if os.path.exists(f):
                    print(f"Removing {f}")
                    os.remove(f)
                else:
                    print(f"Could not find {f}")


        playlists = options.get("playlists")
        for p in playlists:
            self.handle_playlist(p)

    def handle_playlist(self, playlist_file):
        self.check_path(playlist_file)

        with open(playlist_file, 'r', encoding='utf-8') as f:
            song_files = f.readlines()
        playlist_file_count = len(song_files)

        song_files = [path.strip() for path in song_files]
        song_files = [path for path in song_files if os.path.exists(path)]
        print(f"Found {len(song_files)} of {playlist_file_count} song files")

        for i, f in enumerate(song_files):
            print(f"Copying {i + 1} of {len(song_files)}: {f}")
            if self.force or not os.path.exists(os.path.join(self.location, os.path.basename(f))):
                copy(f, self.location)
