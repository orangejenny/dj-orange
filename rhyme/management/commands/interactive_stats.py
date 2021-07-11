from collections import Counter, defaultdict
from functools import partial

from django.core.management.base import BaseCommand

from rhyme.models import Album, Artist, Song, Tag


class Processor(object):
    ALBUM = 'album'
    ARTIST = 'artist'
    SONG = 'song'

    chunk_size = 1

    def __init__(self):
        pass

    def all(self):
        raise NotImplementedError()

    def songs(self, item):
        raise NotImplementedError()

    def get_results(self, stat):
        results = defaultdict(list)
        items = self.all()
        item_count = 0
        for item in items:
            if item_count % self.chunk_size == 0:
                print(f"Processed {item_count} of {items.count()}")
            (count, detail) = stat(self.songs(item))
            if count:
                results[count].append(f"{item.name}\n\t{detail}")
            item_count += 1
        return results


class SongProcessor(Processor):
    chunk_size = 500

    def all(self):
        return Song.objects.all()

    def songs(self, item):
        return [item]


class AlbumProcessor(Processor):
    chunk_size = 100

    def all(self):
        return Album.objects.all()

    def songs(self, item):
        return item.songs


class ArtistProcessor(Processor):
    chunk_size = 100

    def all(self):
        return Artist.objects.all()

    def songs(self, item):
        return Song.objects.filter(artist=item)


def _year_span(songs):
    # Max difference between oldest and newest year tag
    years = {int(t) for song in songs for t in song.tags() if Tag.objects.get(name=t).category == "years"}
    if len(years) > 1:
        return (max(years) - min(years), f"{min(years)} to {max(years)}")
    return (None, None)


def _distinct_tags(category, songs):
    # Max number of distinct tags in given category
    tags = [t for song in songs for t in song.tags() if category is None or Tag.objects.get(name=t).category == category]
    return (len(set(tags)), ", ".join([key for key, value in Counter(tags).most_common()]))


class Command(BaseCommand):
    @property
    def help(self):
        return "Various stats, try it out"

    models = [Processor.SONG, Processor.ALBUM, Processor.ARTIST]
    stats = [
        ("year span", _year_span),
        ("tag count", partial(_distinct_tags, None)),
        ("tag diversity: years", partial(_distinct_tags, "years")),
        ("tag diversity: people", partial(_distinct_tags, "people")),
    ]

    def handle(self, *args, **options):
        stat = self.get_stat()
        if not stat:
            return

        processor = self.get_processor()
        if not processor:
            return

        results = processor.get_results(stat)
        self.print_results(results)
        key = ''
        while key != "q":
            key = input("View result? (q to quit, r to re-show all) ")
            if key == "r":
                self.print_results(results)
            else:
                try:
                    key = int(key)
                except ValueError:
                    pass
                else:
                    for result in results.get(key, []):
                        print(result)
                    print()

    def get_stat(self):
        for index, stat in enumerate(self.stats):
            (name, func) = stat
            print(f"{index + 1}) {name}")
        try:
            return self.stats[int(input("Select option? (q to quit) ")) - 1][1]
        except (ValueError, IndexError):
            return None

    def get_processor(self):
        model = input(f"Model ({' / '.join(self.models)}, q to quit)? ")
        if model == "q":
            return None
        try:
            return {
                Processor.SONG: SongProcessor,
                Processor.ALBUM: AlbumProcessor,
                Processor.ARTIST: ArtistProcessor,
            }[model]()
        except KeyError:
            return self.get_processor()

    def print_results(self, results):
        print(f"Results: {sorted([(key, len(value)) for key, value in results.items()])}")
