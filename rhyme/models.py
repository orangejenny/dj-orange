import os
import re

from datetime import datetime
from random import shuffle

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property


class FilterMixin():
    bool_fields = []
    numeric_fields = []
    text_fields = []

    @classmethod
    def kwargs_from_filters(cls, filters):
        kwargs = []
        if not filters:
            return kwargs

        for condition in filters.split("&&"):
            (lhs, op, rhs) = re.match(r'(\w+)\s*([<>=*]*)\s*(\S.*)', condition).groups()
            if lhs in cls.bool_fields:
                pass
            elif lhs in cls.numeric_fields:
                if op == '>=':
                    lhs = lhs + "__gte"
                elif op == '<=':
                    lhs = lhs + "__lte"
                elif op != '=':
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            elif lhs in cls.text_fields:
                if op == '=*':
                    lhs = lhs + "__icontains"
                elif op == '=':
                    lhs = lhs + "__iexact"
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            elif lhs == 'tag':
                if op == '=*':
                    lhs = "tag__name__icontains"
                elif op == '=':
                    lhs = "tag__name"
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            elif lhs == 'genre':
                if op == '=':
                    lhs = "artist__genre"
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            else:
                raise Exception("Unrecognized lhs {}".format(lhs))

            kwargs.append((lhs, rhs))

        return kwargs


class ExportableMixin(object):
    def audit_export(self):
        self.last_export = datetime.now()
        self.export_count = self.export_count + 1
        self.save()


class Artist(models.Model):
    name = models.CharField(max_length=63, unique=True)
    genre = models.CharField(max_length=63)

    def __str__(self):
        return self.name

    @classmethod
    def all_genres(cls):
        return sorted(list(set([artist.genre for artist in Artist.objects.all() if artist.genre])))


class Song(models.Model, FilterMixin, ExportableMixin):
    RATING_ATTRIBUTES = ['rating', 'energy', 'mood']

    bool_fields = ['starred']
    numeric_fields = RATING_ATTRIBUTES + ['time', 'year']
    text_fields = ['name', 'artist']

    name = models.CharField(max_length=127)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    filename = models.CharField(max_length=255, null=True)
    rating = models.IntegerField(null=True)
    mood = models.IntegerField(null=True)
    energy = models.IntegerField(null=True)
    starred = models.BooleanField(default=False)
    time = models.IntegerField(null=True)   # in seconds
    year = models.IntegerField(null=True)

    export_count = models.IntegerField(default=0)
    last_export = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-id']

    @property
    def albums(self):
        return [t.album.name for t in Track.objects.filter(song=self.id)]

    def tags(self, category=None):
        tags = [t.name for t in self.tag_set.all()]
        if category:
            tags_for_category = [t.name for t in Tag.objects.filter(category=category)]
            tags = list(set(tags).intersection(set(tags_for_category)))
        return tags

    def __str__(self):
        return "{} ({})".format(self.name, self.artist.name)

    @classmethod
    def list(cls, filters=None):
        objects = cls.objects.all()
        for lhs, rhs in cls.kwargs_from_filters(filters):
            objects = objects.filter(**{lhs: rhs})
        return objects


class Album(models.Model, FilterMixin, ExportableMixin):
    bool_fields = ['is_mix']
    text_fields = ['name']

    name = models.CharField(max_length=255)
    date_acquired = models.DateTimeField(null=True)
    starred = models.BooleanField(default=False)
    is_mix = models.BooleanField(default=False)

    export_count = models.IntegerField(default=0)
    last_export = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    @classmethod
    def list(cls, album_filters=None, song_filters=None):
        if album_filters:
            album_queryset = cls.objects.all()
            for lhs, rhs in cls.kwargs_from_filters(album_filters):
                album_queryset = album_queryset.filter(**{lhs: rhs})
        else:
            album_queryset = None

        if song_filters:
            track_queryset = Track.objects.filter(song__in=Song.list(song_filters))
            album_ids_for_tracks = track_queryset.values_list('album_id', flat=True)
        else:
            album_ids_for_tracks = None

        if album_queryset and album_ids_for_tracks:
            album_ids = set(album_queryset.values_list('id', flat=True))
            return cls.objects.filter(id__in=album_ids.intersection(album_ids_for_tracks))

        if album_queryset:
            return album_queryset

        if album_ids_for_tracks:
            return cls.objects.filter(id__in=album_ids_for_tracks)

        return cls.objects.all()

    @property
    def acronym(self):
        acronym = self.name
        acronym = re.sub(r'[^\w\s]', '', acronym)
        acronym = re.sub(r'\s+', ' ', acronym)
        acronym = "".join([word[0] for word in acronym.split(' ')])
        return acronym

    @property
    def acronym_size(self):
        length = len(self.acronym)
        if length >= 8:
            return "xsmall"
        if length >= 5:
            return "small"
        if length == 4:
            return "medium"
        if length == 3:
            return "large"
        if length == 2:
            return "xlarge"
        return "solo"

    @cached_property
    def color(self):
        colors = self.tags(category='colors')
        if colors:
            return Color.objects.filter(name=colors[0]).first()
        return None

    @property
    def completion(self):
        songs = self.songs
        if not songs:
            return 0

        completion = 0
        for attribute in Song.RATING_ATTRIBUTES:
            completion += sum([1 for s in songs if getattr(s, attribute, None)])

        return completion * 100 / (len(Song.RATING_ATTRIBUTES) * len(songs))

    @property
    def export_html(self):
        if not self.export_count:
            return "Never exported"

        if self.export_count == 1:
            return f"Exported once, on {self.last_export}"

        times = "twice" if self.export_count == 2 else f"{self.export_count} times"
        return f"Exported {times}<br>Last exported {self.last_export}"

    @property
    def artist(self):
        artists = [song.artist for song in self.songs]
        if len(set(artists)) == 1:
            return artists[0].name
        return "Various Artists"

    @cached_property
    def cover_art_filename(self):
        # TODO: standardize handling of static files
        root = os.path.dirname(os.path.abspath(__file__))
        relative = os.path.join("rhyme", "img", "collections", str(self.id))
        directory = os.path.join(root, "static", relative)
        if os.path.isdir(directory):
            files = os.listdir(directory)
            if len(files):
                # TODO: this is crufty, store one file per album instead of a directory
                return os.path.join(settings.STATIC_URL, relative, files[0])
        return None

    @cached_property
    def songs(self):
        return [track.song for track in self.tracks]

    @cached_property
    def tracks(self):
        return self.track_set.order_by("disc", "ordinal")

    def stats(self):
        songs = self.songs
        stats = {}
        for attribute in Song.RATING_ATTRIBUTES:
            values = [getattr(s, attribute) for s in songs if getattr(s, attribute, None)]
            stats.update({
                attribute: {
                    "min": min(values) if values else None,
                    "avg": sum(values) / len(values) if values else None,
                    "max": max(values) if values else None,
                }
            })
        return stats

    def tags(self, category=None):
        tags = list(
            set([tag for song in self.songs for tag in song.tags(category=category)]))
        shuffle(tags)
        return tags


# Only named discs have entries here
class Disc(models.Model):
    ordinal = models.IntegerField(default=1)
    name = models.CharField(max_length=255, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("ordinal", "album")


class Track(models.Model):
    ordinal = models.IntegerField()
    disc = models.IntegerField(default=1)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "album")

    def __str__(self):
        return "{}: {}. {}".format(str(self.album), self.ordinal, str(self.song))


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, null=True)
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=8, default='ffffff')
    white_text = models.BooleanField(default=False)

    def __str__(self):
        return "{} (#{})".format(self.name, self.hex_code)
