from django.core.management.base import BaseCommand

from rhyme.models import *

from collections import defaultdict
from datetime import datetime
import random


class Command(BaseCommand):
    album_ids = set()

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **options):
        self.quiet = options.get('quiet', False)

        this_year = int(datetime.utcnow().strftime("%Y"))
        this_month = int(datetime.utcnow().strftime("%m"))
        seasons = ["winter"] * 2 + ["spring"] * 3 + ["summer"] * 3 + ["autumn"] * 3 + ["winter"]
        this_season = seasons[this_month - 1]
        last_season = seasons[this_month - 4]
        last_season_year = this_year - 1 if this_season == "winter" else this_year

        # Current
        albums = Album.objects.all()[:3]
        self.album_ids |= {a.id for a in albums}

        self.add_album(song_filters=f"tag={this_year},{this_season}", count=2)
        self.add_album(song_filters=f"starred=1&&tag!={this_year}", count=2)
        self.add_album(song_filters=f"tag={last_season_year},{last_season}", count=2)

        # Nostalgia
        start = 1999
        for end in [2002, 2008, 2013, 2017, 2020, 2023, this_year]:
            tags = ",".join([str(x) for x in range(start, end + 1)])
            self.add_album(song_filters=f"tag*={tags}")
            start = end

        self.add_album(song_filters=f"rating>=3&&tag={this_year},{this_season}", count=2)
        self.add_album(song_filters=f"rating>=3&&tag={this_year - 1},{this_season}", count=2)

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

        print("\n\n")
        for album in sorted(Album.objects.filter(id__in=self.album_ids), key=Album.alternate_sort):
            self.print_album(album)

    def add_album(self, song_filters=None, album_filters=None, count=1):
        print(f"Adding {count} of {song_filters or ''} {album_filters or ''}")
        qualifiers = { a.id: a for a in Album.list(song_filters=song_filters) if a.id not in self.album_ids }
        if len(qualifiers):
            added = 0
            while added < count:
                random_albums = set(random.sample(list(qualifiers.values()), count - added))
                for album in random_albums:
                    self.print_album(album)
                    if self.quiet or input("Keep this one (y/n)? ") not in ['N', 'n']:
                        self.album_ids |= { album.id }
                        added += 1

        else:
            self.add_album(song_filters="rating>=4", count=count)

    def print_album(self, album):
        print(f"{album} ({album.artist})")
