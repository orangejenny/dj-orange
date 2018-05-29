from django.core.management.base import BaseCommand, CommandError
import json

from tastes.models import Song

class Command(BaseCommand):
    help = 'Import songs from a csv'

    def add_arguments(self, parser):
        parser.add_argument('filename', help="JSON file of data => [song, song...]")
        parser.add_argument('--save', action='store_true')

    def handle(self, *args, **options):
        (count, count_of_skipped) = (0, 0)
        with open(options['filename'], encoding='utf-8') as f:
            songs = json.load(f)['data']
            for row in songs:
                if Song.objects.filter(name=row['name'], artist=row['artist']).exists():    # TODO: there are a few legitimate duplicate name+artist combinations
                    count_of_skipped = count_of_skipped + 1
                    continue
                song = Song(name=row['name'], artist=row['artist'], rating=row['rating'], energy=row['energy'], mood=row['mood'], starred=(True if row['isstarred'] else False))
                count = count + 1
                if options['save']:
                    song.save()
            self.stdout.write(self.style.SUCCESS('Wrote {} songs, skipped {}'.format(count, count_of_skipped)))
