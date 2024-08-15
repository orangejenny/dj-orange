from django.db.models import Q

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Song, Tag, Track
from rhyme.plex import create_plex_playlist

from datetime import datetime
import random


class Command(RhymeCommand):
    @property
    def help(self):
        return "Edit starred property for songs"

    def handle(self, *args, **options):
        key = None
        while key != "q":
            key = input("What to do? (L)ist, (S)tar, (U)nstar? ").lower()
            if key == "l":
                for song in Song.objects.filter(starred=True).order_by('-id'):
                   print(song)
            elif key in ("s", "u"):
                song = self.get_song()
                new_starred = key == "s"
                action = "starred" if key == "s" else "unstarred"

                if song.starred == new_starred:
                    print(f"{song} is already {action}")
                else:
                    song.starred = not song.starred
                    song.save()
                    print(f"{action} {song}!")
