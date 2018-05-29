from django.core.management.base import BaseCommand, CommandError
import json

from tastes.models import Song, SongTag, Tag

class Command(BaseCommand):
    help = 'Import items from a csv'
    models = ('song', 'songtag')

    def add_arguments(self, parser):
        parser.add_argument('model', help="One of {}".format(", ".join(self.models)))
        parser.add_argument('filename', help="JSON file of data => [item, item...]")
        parser.add_argument('--save', action='store_true')

    def handle(self, *args, **options):
        model = options['model']
        if model not in self.models:
            raise Exception("model {} not found in {}".format(model, ", ".join(self.models)))

        save = options['save']
        counts = {model: {'new': 0, 'existing': 0} for model in ('song', 'songtag', 'tag')}

        with open(options['filename'], encoding='utf-8') as f:
            data = json.load(f)['data']
            for item in data:
                song = self._get_song(name=item['name'], artist=item['artist'])
                if model == 'song':
                    if song:
                        counts['song']['existing'] += 1
                    else:
                        song = Song(name=item['name'], artist=item['artist'], rating=item['rating'], energy=item['energy'], mood=item['mood'], starred=(True if item['isstarred'] else False))
                        counts['song']['new'] += 1
                        if save:
                            song.save()
                elif model == 'songtag':
                    try:
                        tag = Tag.objects.get(name=item['tag'])
                        counts['tag']['existing'] += 1
                    except Tag.DoesNotExist:
                        tag = Tag(name=item['tag'])
                        counts['tag']['new'] += 1
                        if save:
                            tag.save()
                    try:
                        songtag = SongTag.objects.get(song=song, tag=tag)
                        counts['songtag']['existing'] += 1
                    except SongTag.DoesNotExist:
                        songtag = SongTag(song=song, tag=tag)
                        counts['songtag']['new'] += 1
                        if save:
                            songtag.save()

            self.stdout.write(self.style.SUCCESS('Finished, counts: {}'.format(counts)))

    # TODO: there are a few legitimate duplicate name+artist combinations
    def _get_song(self, name, artist):
        try:
            return Song.objects.get(name=name, artist=artist)
        except Song.DoesNotExist:
            return None
