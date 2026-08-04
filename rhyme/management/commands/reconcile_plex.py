from django.core.management.base import BaseCommand

import os
import re
import shutil

from Levenshtein import distance

from rhyme.plex import add_plex_ids, missing_songs, plex_library, plex_options


class Command(BaseCommand):
    @property
    def help(self):
        return "Identify songs not present in plex, and search for them"

    def add_arguments(self, parser):
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
        quiet = options.get('quiet', False)

        # Use reconcile_filenames with a playlist that was exported to metroplex (typically /Volumes/Music) and flavors as --root
        if not input(f"Have files all been copied to metroplex using reconcile_filenames? (y/n) ").lower() == "y":
            exit(0)

        songs = missing_songs()

        if not songs:
            print("All songs are in plex!")
            return

        print(f"{len(songs)} missing songs found. Getting plex library (this is slow)...")
        library = plex_library()
        add_plex_ids(library, songs)

        if not songs:
            print("All songs are in plex!")
            return

        songs = missing_songs()
        current_artist = None
        plex_artist_key = None
        for song in songs:
            if not quiet and input(f"Search for '{song.name}' ({song.artist.name})? (y/n) ").lower() != "y":
                continue
            if song.artist != current_artist:
                artist = input(f"Artist? (press enter to use '{song.artist}') ") or song.artist
                artists = library.search(artist)
                if not artists:
                    print("No artists found")
                    continue
                artist = self.input_choice(artists)
                plex_artist_key = artist.key if artist else None
            options = plex_options(library, song, plex_artist_key)
            if options:
                track = self.input_choice(options)
                if track:
                    song.plex_guid = track.guid
                    song.plex_key = track.key
                    song.save()

        songs = missing_songs()
        print("Finished. Remaining missing songs: {len(songs)}")
