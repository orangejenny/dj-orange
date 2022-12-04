from django.core.management.base import BaseCommand

import os
import shutil


class Command(BaseCommand):
    @property
    def help(self):
        return "Identify songs not present on the file system, based on an M3U playlist"

    def add_arguments(self, parser):
        parser.add_argument('playlist_file', help="M3U playlist")
        parser.add_argument('--quiet', action='store_true')

    def input_choice(self, options, message=None, display=None):
        if message:
            print(message)
        if len(options) == 1:
            return options[0]

        if not display:
            display = lambda x: x

        for i, option in enumerate(options):
            print(f"{i + 1}) {display(option)}")
        selection = input("Pick an option (s to skip): ").lower()
        try:
            return options[int(selection) - 1]
        except (IndexError, ValueError):
            return None

    def print_list(self, items, message):
        if items:
            if input(f"{len(items)} {message}. List? (y/n) ").lower() == "y":
                for path in sorted(items):
                    print(path)

    def segments(self, path):
        segments = []
        (path, tail) = os.path.split(path)
        while tail:
            (path, tail) = os.path.split(path)
            if tail:
                segments.append(tail)
        segments.append(path)
        segments.reverse()
        return segments

    def subpaths(self, path):
        segments = self.segments(path)
        return [os.path.join(*segments[:i + 1]) for i in range(1, len(segments))]

    def handle(self, *args, **options):
        playlist_file = options.get("playlist_file")
        quiet = options.get('quiet', False)
        if not os.path.exists(playlist_file):
            print(f"{playlist_file} does not exist")
            exit(1)

        with open(playlist_file, 'r', encoding='utf-8') as f:
            song_files = f.readlines()
        song_files = [path.strip() for path in song_files]

        if not song_files:
            return

        root_options = self.subpaths(song_files[0])
        root_dir = self.input_choice(root_options, "Possible root directories:")
        if not root_dir:
            print("No root directory identified")
            return

        existing_count = 0
        moved = []
        skipped = []
        failures = []
        for i, path in enumerate(song_files):
            exists = os.path.exists(path)
            print(f"Checking if {i + 1} of {len(song_files)}, {path}, exists: {exists}")
            if exists:
                existing_count += 1
                continue

            tail = os.path.split(path)[1]
            options = []
            for root, dirs, files in os.walk(root_dir):
                if tail in files:
                    options.append(os.path.join(root, tail))
            if not options:
                print(f"Could not find any likely candidate files for {tail}")
                failures.append(path)
                continue
            source_path = self.input_choice(options, display=lambda x: x.replace(root_dir, "")[1:])
            if not source_path:
                skipped.append(path)
                continue

            dest_dir = os.path.split(path)[0]
            if not os.path.exists(dest_dir):
                if quiet or input(f"Make directories for {dest_dir}? (y/n) ").lower() == "y":
                    os.makedirs(dest_dir)
                else:
                    continue
            source_path = os.path.join(root_dir, source_path)
            dest_path = os.path.join(root_dir, path)
            if quiet or input(f"Move\n\t{source_path} to\n\t{dest_path}? (y/n) ").lower() == "y":
                moved.append(path)
                shutil.move(source_path, dest_path)

        print("=====================================")
        print(f"Examined {len(song_files)} songs")
        print(f"{existing_count} already existed")
        self.print_list(moved, "moved")
        self.print_list(skipped, "skipped")
        self.print_list(failures, "not found")
