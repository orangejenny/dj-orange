from django.db.models import Q

from rhyme.management.commands.rhyme_command import Command as RhymeCommand
from rhyme.models import Song, Tag, Track

from datetime import datetime
import random


class Command(RhymeCommand):
    length = 25

    @property
    def help(self):
        return '''
Return a playlist of {} songs similar to a seed song, based on tag sets.
        '''.format(self.length)

    def handle(self, *args, **options):
        seed = self.get_song()
        print(f"Seed: {seed}")

        if not seed.tags():
            print("No tags found for given song")
            exit(1)

        pairs = [(self.jaccard(s, seed), s) for s in Song.objects.exclude(id=seed.id)
                 if s.tags() and len(set(s.tags()).intersection(set(seed.tags())))]

        pairs.sort(key=lambda result: result[0])
        pairs.reverse()

        song_ids = [p[1].id for p in pairs[:self.length]]

        self.export_playlist(song_ids, display=True)

    def jaccard(self, song1, song2):
        set1 = set(song1.tags())
        set2 = set(song2.tags())
        return len(set1.intersection(set2)) / len(set1.union(set2))
