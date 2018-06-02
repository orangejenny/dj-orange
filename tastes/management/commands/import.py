from argparse import RawTextHelpFormatter
from datetime import datetime
import json
import pytz

from django.core.management.base import BaseCommand, CommandError

from tastes.models import Album, Song, SongTag, Tag


class Importer(object):
    ALBUM = 'album'
    SONG = 'song'
    SONGTAG = 'songtag'

    fields = []

    @property
    def query(self):
        raise Exception("Subclasses should override this method")

    def __init__(self):
        pass


    @classmethod
    def create(cls, item_type):
        if item_type == cls.ALBUM:
            return AlbumImporter()
        if item_type == cls.SONG:
            return SongImporter()
        if item_type == cls.SONGTAG:
            return SongTagImporter()
        raise Exception("Unrecognized item_type {}".format(item_type))


class AlbumImporter(object):
    fields = ['id', 'name', 'created']

    @property
    def query(self):
        return "select {} from flavors_collection".format(", ".join(self.fields))

    def __init__(self):
        return super(AlbumImporter, self).__init__()


class SongImporter(object):
    fields = ['id', 'name', 'artist', 'rating', 'mood', 'energy', 'isstarred', 'filename']

    @property
    def query(self):
        return "select {} from flavors_song".format(", ".join(self.fields))

    def __init__(self):
        return super(SongImporter, self).__init__()


class SongTagImporter(object):
    fields = ['songid', 'name', 'artist', 'tag']

    @property
    def query(self):
        return "select {} from flavors_song, flavors_songtag where flavors_song.id = flavors_songtag.songid".format(", ".join(self.fields))

    def __init__(self):
        return super(SongTagImporter, self).__init__()


class Command(BaseCommand):
    models = [Importer.ALBUM, Importer.SONG, Importer.SONGTAG]

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    @property
    def help(self):
        return '''
Import items from a csv.
Available models: {}
Queries:
{}
        '''.format(", ".join(self.models), "\n".join(["\t{}: {}".format(model, Importer.create(model).query) for model in self.models]))

    def add_arguments(self, parser):
        parser.add_argument('model', help="One of {}".format(", ".join(self.models)))
        parser.add_argument('filename', help="JSON file of data => [item, item...]")
        parser.add_argument('--save', action='store_true')

    def handle(self, *args, **options):
        model = options['model']
        if model not in self.models:
            raise Exception("model {} not found in {}".format(model, ", ".join(self.models)))

        save = options['save']

        with open(options['filename'], encoding='utf-8') as f:
            data = json.load(f)['data']
            for item in data:
                if model == 'song':
                    song = self._get_song(name=item['name'], artist=item['artist'])
                    if not song:
                        song = Song(name=item['name'], artist=item['artist'], rating=item['rating'], energy=item['energy'], mood=item['mood'], starred=(True if item['isstarred'] else False))
                        if save:
                            song.save()
                elif model == 'album':
                    album = Album(name=item['name'])
                    if item['created']:
                        album.date_acquired = pytz.utc.localize(datetime.strptime(item['created'], "%Y-%m-%d %H:%M:%S"))
                    if save:
                        album.save()
                elif model == 'songtag':
                    song = self._get_song(name=item['name'], artist=item['artist'])
                    try:
                        tag = Tag.objects.get(name=item['tag'])
                    except Tag.DoesNotExist:
                        tag = Tag(name=item['tag'])
                        if save:
                            tag.save()
                    try:
                        songtag = SongTag.objects.get(song=song, tag=tag)
                    except SongTag.DoesNotExist:
                        songtag = SongTag(song=song, tag=tag)
                        if save:
                            songtag.save()

            self.stdout.write(self.style.SUCCESS('Finished'))

    # TODO: there are a few legitimate duplicate name+artist combinations
    def _get_song(self, name, artist):
        try:
            return Song.objects.get(name=name, artist=artist)
        except Song.DoesNotExist:
            return None
