from argparse import RawTextHelpFormatter
from datetime import datetime
import json
import pytz

from django.core.management.base import BaseCommand, CommandError

from rhyme.models import Album, Artist, Color, Disc, Song, Tag, Track


class Importer(object):
    ALBUM = 'album'
    ARTIST = 'artist'
    COLOR = 'color'
    DISC = 'disc'
    SONG = 'song'
    TAG = 'tag'
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
            data = json.load(f)
            for item in data:
                if set(item.keys()) != set([f.split(".")[-1] for f in self.fields]):    # de-namespace fields
                    raise Exception("Mismatched fields, expected [{}] and got [{}]".format(self.fields, item.keys()))
                self.import_item(item, save)
            self.log("{}Imported {} items".format("" if save else "[DRY RUN] ", len(data)))


    @classmethod
    def create(cls, item_type, out=None):
        if item_type == cls.ALBUM:
            return AlbumImporter(out)
        if item_type == cls.ARTIST:
            return ArtistImporter(out)
        if item_type == cls.COLOR:
            return ColorImporter(out)
        if item_type == cls.DISC:
            return DiscImporter(out)
        if item_type == cls.SONG:
            return SongImporter(out)
        if item_type == cls.TAG:
            return TagImporter(out)
        if item_type == cls.TRACK:
            return TrackImporter(out)
        raise Exception("Unrecognized item_type {}".format(item_type))


class AlbumImporter(Importer):
    fields = Album.import_fields

    @property
    def query(self):
        return "select {} from collection".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(AlbumImporter, self).__init__(out)

    def import_item(self, item, save=False):
        (album, created) = Album.objects.get_or_create(id=item['id'])
        album.name = item['name']
        if item['date_acquired']:
            album.date_acquired = pytz.utc.localize(datetime.strptime(item['date_acquired'], "%Y-%m-%d %H:%M:%S %Z"))
        if item['is_mix']:
            album.is_mix = True

        self.log("Importing {}".format(album))
        if save:
            album.save()
        elif created:
            album.delete()


class ArtistImporter(Importer):
    fields = Artist.import_fields

    @property
    def query(self):
        return "select {} from artistgenre".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(ArtistImporter, self).__init__(out)

    def import_item(self, item, save=False):
        (artist, created) = Artist.objects.get_or_create(name=item['name'])
        artist.genre = item['genre']
        self.log("Importing {}".format(artist.name))
        if save:
            artist.save()
        elif created:
            artist.delete()


class ColorImporter(Importer):
    fields = Color.import_fields

    @property
    def query(self):
        return "select {} from color".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(ColorImporter, self).__init__(out)

    def import_item(self, item, save=False):
        (color, created) = Color.objects.get_or_create(name=item['name'])
        color.hex_code = item['hex_code']
        color.white_text = bool(int(item['white_text'] or 0))
        if save:
            color.save()
        elif created:
            color.delete()


class DiscImporter(Importer):
    fields = Disc.import_fields

    @property
    def query(self):
        return "select {} from collectiondisc".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(DiscImporter, self).__init__(out)

    def import_item(self, item, save=False):
        try:
            album = Album.objects.get(id=item['album_id'])
            (disc, created) = Disc.objects.get_or_create(
                album=album, name=item['name'], ordinal=item['ordinal'])
            self.log("Importing {}".format(disc))
            if save:
                disc.save()
            elif created:
                disc.delete()
        except Album.DoesNotExist as e:
            self.log("FAIL: Disc {}, (tried albumid={})".format(
                item['name'], item['album_id']))


class SongImporter(Importer):
    fields = Song.import_fields

    @property
    def query(self):
        return "select {} from song".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(SongImporter, self).__init__(out)

    def import_item(self, item, save=False):
        (song, song_created) = Song.objects.get_or_create(id=item['id'])
        for field in self.fields.difference({'artist', 'starred'}):
            setattr(song, field, item[field])
        (artist, artist_created) = Artist.objects.get_or_create(name=item['artist'])
        song.artist = artist
        song.starred = bool(item['starred'])
        self.log("Importing {}".format(song))
        if save:
            song.save()
            artist.save()
        else:
            if song_created:
                song.delete()
            if artist_created:
                artist.delete()


class TagImporter(Importer):
    fields = Tag.import_fields

    @property
    def query(self):
        return """
            select {} from song
            inner join songtag on song.id = songtag.songid
            left join tagcategory on songtag.tag = tagcategory.tag
        """.format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(TagImporter, self).__init__(out)

    def import_item(self, item, save=False):
        (tag, tag_created) = Tag.objects.get_or_create(name=item['name'])
        tag.category = item['category']
        self.log("Importing {}".format(tag))
        song = Song.objects.get(id=item['song_id'])
        song.tag_set.add(tag)
        if save:
            tag.save()
            song.save()
        else:
            if tag_created:
                tag.delete()


class TrackImporter(Importer):
    fields = Track.import_fields

    @property
    def query(self):
        return "select {} from songcollection".format(", ".join(self.fields))

    def __init__(self, out=None):
        return super(TrackImporter, self).__init__(out)

    def import_item(self, item, save=False):
        try:
            album = Album.objects.get(id=item['album_id'])
            song = Song.objects.get(id=item['song_id'])
            (track, created) = Track.objects.get_or_create(album=album,
                                                           song=song, disc=item['disc_ordinal'], ordinal=item['ordinal'])
            self.log("Importing {}".format(track))
            if save:
                track.save()
            elif created:
                track.delete()
        except Album.DoesNotExist as e:
            self.log("FAIL: Track #{}, (tried album_id={}, song_id={}))".format(
                item['tracknumber'], item['album_id'], item['song_id']))
        except Song.DoesNotExist as e:
            self.log("FAIL: Track #{} in {} (tried song_id={})".format(
                item['ordinal'], album, item['song_id']))


class Command(BaseCommand):
    models = [
        Importer.ALBUM, Importer.ARTIST, Importer.COLOR, Importer.SONG,      # These are indepentdent
        # These depend on songs and/or albums existing
        Importer.DISC, Importer.TAG, Importer.TRACK,
    ]

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
