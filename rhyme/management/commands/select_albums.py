from django.core.management.base import BaseCommand

from rhyme.models import *

from collections import defaultdict
from datetime import datetime
import random


class Command(BaseCommand):
    album_ids = set()

    def handle(self, *args, **options):
        this_year = int(datetime.utcnow().strftime("%Y"))
        this_month = int(datetime.utcnow().strftime("%m"))
        seasons = ["winter"] * 2 + ["spring"] * 3 + ["summer"] * 3 + ["autumn"] * 3 + ["winter"]
        this_season = seasons[this_month - 1]

        # Current
        albums = Album.objects.all()[:3]
        self.album_ids |= {a.id for a in albums}

        self.add_album(song_filters=f"tag={this_year},{this_season}", count=2)
        self.add_album(song_filters=f"starred=1&&tag!={this_year}", count=2)

        # Nostalgia
        start = 1999
        for end in [2002, 2008, 2013, 2017, this_year]:
            tags = ",".join([str(x) for x in range(start, end + 1)])
            self.add_album(song_filters=f"tag*={tags}")
            start = end

        self.add_album(song_filters=f"rating>=3&&tag={this_year},{this_season}")
        self.add_album(song_filters=f"rating>=3&&tag={this_year - 1},{this_season}")

        # Undiscovered
        self.add_album(album_filters="acquired_year>={this_year - 1}", song_filters="rating=?false")
        self.add_album(album_filters="acquired_year<={this_year - 5}", song_filters="rating=?false")

        # Happy
        self.add_album(song_filters=f"rating>=4&&mood>=4", count=2)

        # Extend on artist
        artist_counts = defaultdict(lambda: 0)
        for album_id in self.album_ids:
            for song in Album.objects.get(id=album_id).songs:
                artist_counts[song.artist.name] += 1
        names = ",".join([name for name, count in artist_counts.items() if count > 1])
        self.add_album(song_filters=f"artist*={names}", count=2)

        for album in sorted(Album.objects.filter(id__in=self.album_ids), key=Album.alternate_sort):
            print(f"{album} ({album.artist})")

    def add_album(self, song_filters=None, album_filters=None, count=1):
        ids = Album.list(song_filters=song_filters).values_list("id", flat=True)
        ids = set(ids) - self.album_ids
        if len(ids):
            self.album_ids |= set(random.sample(list(ids), count))
        else:
            self.add_album(song_filters="rating>=4", count=count)
