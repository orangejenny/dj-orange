from argparse import RawTextHelpFormatter
from datetime import datetime
import json
import pytz

from django.core.management.base import BaseCommand, CommandError

from tastes.models import Album, Song, SongTag, Tag, Track


class Importer(object):
    ALBUM = 'album'
    SONG = 'song'
    SONGTAG = 'songtag'
    TRACK = 'track'

    fields = set()

    @property
    def query(self):
        raise Exception("Subclasses should override this method")

    def __init__(self, out=None):
        self._out = out

    def log(self, message):
        if self._out:
            self._out.write(message)

    def import_item(self, save=False):
        raise Exception("Subclasses should override this method")

    def import_items(self, filename, save=False):
        with open(filename, encoding='utf-8') as f:
            data = json.load(f)['data']
            for item in data:
                if set(item.keys()) != set(self.fields):
                    raise Exception("Mismatched fields, expected [{}] and got [{}]".format(self.fields, item.keys()))
                self.import_item(item, save)
            self.log("{}Imported {} items".format("" if save else "[DRY RUN] ", len(data)))


    @classmethod
    def create(cls, item_type, out=None):
        if item_type == cls.ALBUM:
            return AlbumImporter(out)
        if item_type == cls.SONG:
            return SongImporter(out)
        if item_type == cls.SONGTAG:
            return SongTagImporter(out)
        if item_type == cls.TRACK:
            return TrackImporter(out)
        raise Exception("Unrecognized item_type {}".format(item_type))


class AlbumImporter(Importer):
    fields = set(['id', 'name', 'created'])

    @property
    def query(self):
        return "select {} from flavors_collection".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(AlbumImporter, self).__init__(out)

    def import_item(self, item, save=False):
        album = Album(name=item['name'])
        album.id = item['id']
        self.log("Importing {}".format(album))
        if item['created']:
            album.date_acquired = pytz.utc.localize(datetime.strptime(item['created'], "%Y-%m-%d %H:%M:%S"))
        if save:
            if Album.objects.filter(id=album.id).exists():
                Album.objects.get(id=album.id).delete()
            album.save()


class SongImporter(Importer):
    fields = set(['id', 'name', 'artist', 'rating', 'mood', 'energy', 'isstarred', 'filename'])

    @property
    def query(self):
        return "select {} from flavors_song".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(SongImporter, self).__init__(out)

    def import_item(self, item, save=False):
        song = Song()
        for field in self.fields.difference('isstarred'):
            setattr(song, field, item[field])
        song.isstarred = bool(item['isstarred'])
        self.log("Importing {}".format(song))
        if save:
            if Song.objects.filter(id=song.id).exists():
                Song.objects.get(id=song.id).delete()
            song.save()


class SongTagImporter(Importer):
    fields = set(['songid', 'tag'])

    @property
    def query(self):
        return "select {} from flavors_song, flavors_songtag where flavors_song.id = flavors_songtag.songid".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(SongTagImporter, self).__init__(out)

    def import_item(self, item, save=False):
        try:
            tag = Tag.objects.get(name=item['tag'])
        except Tag.DoesNotExist:
            tag = Tag(name=item['tag'])
            self.log("Importing {}".format(tag))
            if save:
                tag.save()
        song = Song.objects.get(id=item['songid'])
        song_tag = SongTag(song=song, tag=tag)
        self.log("Importing {}".format(song_tag))
        if save:
            if SongTag.objects.filter(song=song, tag=tag).exists():
                SongTag.objects.get(song=song, tag=tag).delete()
            song_tag.save()


class TrackImporter(Importer):
    fields = set(['songid', 'collectionid', 'tracknumber'])

    @property
    def query(self):
        return "select {} from flavors_songcollection".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(TrackImporter, self).__init__(out)

    def import_item(self, item, save=False):
        try:
            album = Album.objects.get(id=item['collectionid'])
            song = Song.objects.get(id=item['songid'])
            track = Track(album=album, song=song, ordinal=item['tracknumber'])
            if not track.ordinal:
                # TODO: fix data issue
                return
            self.log("Importing {}".format(track))
            if save:
                if Track.objects.filter(album=album, song=song).exists():
                    Track.objects.get(album=album, song=song).delete()
                track.save()
        except Album.DoesNotExist as e:
            # TODO: fix data issue
            self.log("FAIL: Track #{}, (tried albumid={}, songid={}))".format(item['tracknumber'], item['collectionid'], item['songid']))
        except Song.DoesNotExist as e:
            # TODO: fix data issue
            self.log("FAIL: Track #{} in {} (tried songid={})".format(item['tracknumber'], album, item['songid']))


class Command(BaseCommand):
    models = [Importer.ALBUM, Importer.SONG, Importer.SONGTAG, Importer.TRACK]

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

        importer = Importer.create(options['model'], out=self.stdout)
        importer.import_items(options['filename'], save=options['save'])
