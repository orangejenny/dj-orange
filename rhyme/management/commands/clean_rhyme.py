from collections import defaultdict
from functools import partial

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Playlist, Tag


class Command(RhymeCommand):
    @property
    def help(self):
        return "Command-line playlist management"

    def handle(self, *args, **options):
        print("Searching for tags without any songs attached...")
        tags = Tag.objects.filter(songs__isnull=True)
        for tag in tags:
            print(f"Deleting {tag}")
            tag.delete()

        print("Fetching playlists...")
        lengths = defaultdict(list)
        for playlist in Playlist.objects.all():
            lengths[len(playlist.songs)].append(playlist)

        if lengths[0]:
            for playlist in lengths[0]:
                if input(f"Playlist '{playlist.name}' ({playlist.all_filters}) is empty. Delete? (y/n) ").lower() == "y":
                    playlist.delete()
        else:
            print("All playlists contain songs")

        for length, playlists in lengths.items():
            first_playlist = playlists[0]
            for p in playlists[1:]:
                print(f"The following playlists both have {length} songs:")
                print(f"{first_playlist.name} ({first_playlist.all_filters})")
                print(f"{p.name} ({p.all_filters})")
                if input(f"Delete '{p.name}' ({p.all_filters}) ? (y/n) ").lower() == "y":
                    p.delete()

        print("Done")
