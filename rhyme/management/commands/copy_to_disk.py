from django.core.management.base import BaseCommand

import os
from shutil import copy


class Command(BaseCommand):
    @property
    def help(self):
        return "Copy files from a playlist to a disk location"

    def add_arguments(self, parser):
        parser.add_argument('playlist_file', help="M3U playlist")
        parser.add_argument('location', help="Disk location")

    def check_path(self, path):
        if not os.path.exists(path):
            print(f"{path} does not exist")
            exit(1)

    def handle(self, *args, **options):
        playlist_file = options.get("playlist_file")
        location = options.get("location")

        self.check_path(playlist_file)
        self.check_path(location)

        with open(playlist_file, 'r', encoding='utf-8') as f:
            song_files = f.readlines()
        playlist_file_count = len(song_files)

        song_files = [path.strip() for path in song_files]
        song_files = [path for path in song_files if os.path.exists(path)]
        print(f"Found {len(song_files)} of {playlist_file_count} song files")

        location_files = os.listdir(location)
        if input(f"Remove {len(location_files)} files from {location}? (y/n) ").lower() == "y":
            for f in location_files:
                f = os.path.join(location, f)
                if os.path.exists(f):
                    print(f"Removing {f}")
                    os.remove(f)
                else:
                    print(f"could not find {f}")

        for i, f in enumerate(song_files):
            print(f"Copying {i + 1} of {len(song_files)}: {f}")
            copy(f, location)
