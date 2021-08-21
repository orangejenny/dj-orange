import os
import re

from datetime import datetime, timezone
from random import shuffle

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property


class FilterMixin():
    bool_fields = []
    numeric_fields = []
    text_fields = []

    @classmethod
    def filter_queryset(cls, objects, filters='', omni_filter=''):
        if omni_filter and cls.omni_fields:
            for value in re.split(r'\s+', omni_filter):
                fields = [cls.related_fields[f] if f in cls.related_fields else f for f in cls.omni_fields]
                qcondition = models.Q(**{f"{fields[0]}__icontains": value})
                for field in fields[1:]:
                    qcondition = qcondition | models.Q(**{f"{field}__icontains": value})
                objects = objects.filter(qcondition)

        if not filters:
            return objects.distinct()

        qconditions = []
        conjunction = "||" if "||" in filters else "&&"
        for condition in filters.split(conjunction):
            (lhs, op, rhs) = re.match(r'(\w+)\s*([<>=*!?]*)\s*(\S.*)', condition).groups()
            action = None
            qcondition = None
            if op == '=?':
                action = (f"{lhs}__isnull", bool(rhs != "true"))
            elif lhs in cls.bool_fields:
                action = (lhs, rhs)
            elif lhs in cls.numeric_fields:
                if op == '>=':
                    lhs = lhs + "__gte"
                elif op == '<=':
                    lhs = lhs + "__lte"
                elif op != '=':
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                action = (lhs, rhs)
            elif lhs in cls.text_fields:
                if op == '*=':
                    lhs = lhs + "__icontains"
                elif op == '=':
                    lhs = lhs + "__iexact"
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                action = (lhs, rhs)
            elif lhs in cls.related_fields:
                field = cls.related_fields[lhs]
                if op == '=':       # all
                    for value in rhs.split(","):
                        action = (f"{field}__iexact", value)
                elif op == '!=':    # none
                    for value in rhs.split(","):
                        action = (f"{field}__iexact", value)    # TODO: exclude
                elif op == '*=':    # any
                    values = rhs.split(",")
                    qcondition = models.Q(**{f"{field}__iexact": values[0]})
                    for value in values[1:]:
                        qcondition = qcondition | models.Q(**{f"{field}__iexact": value})
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            elif lhs == 'tag_year':
                rhs = int(rhs)
                year_tags = [int(tag.name) for tag in Tag.objects.filter(category="years")]
                if op == '>=':
                    year_tags = [tag for tag in year_tags if tag >= rhs]
                elif op == '<=':
                    year_tags = [tag for tag in year_tags if tag <= rhs]
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                qcondition = models.Q(**{"tag__name__exact": year_tags[0]})
                for value in year_tags[1:]:
                    qcondition = qcondition | models.Q(**{"tag__name__exact": value})
            elif lhs == "acquired_year":
                lhs = "date_acquired"
                rhs = int(rhs)
                if op == '>=':
                    lhs = lhs + "__gte"
                    rhs = f"{rhs}-01-01"
                elif op == '<=':
                    lhs = lhs + "__lte"
                    rhs = f"{rhs}-12-31"
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                action = (lhs, rhs)
            elif lhs == "playlist":
                song_ids = set()
                for value in rhs.split(","):
                    playlist = Playlist.objects.filter(name=rhs).first()
                    if playlist is None:
                        raise Exception("Could not find playlist: {}".format(rhs))
                    if op == '=':   # all
                        song_ids = song_ids & {s.id for s in playlist.songs}
                    else:           # any, none
                        song_ids = song_ids | {s.id for s in playlist.songs}

                if op == '!=':    # none
                    action = ("id__in", song_ids)   # TODO: exclude
                elif op == '=' or op == '*=':             # any, all (will have different values for song_ids)
                    action = ("id__in", song_ids)
                else:
                    raise Exception("Unrecognized op for {}: {}".format(lhs, op))
            else:
                raise Exception("Unrecognized lhs {}".format(lhs))

            if conjunction == "&&":
                if action:
                    objects = objects.filter(**{action[0]: action[1]})
                elif qcondition:
                    objects = objects.filter(qcondition)
            else:
                if action:
                    qconditions.append(models.Q(**{action[0]: action[1]}))
                elif qcondition:
                    qconditions.append(qcondition)

        if qconditions and conjunction == "||":
            qcondition = qconditions.pop()
            for q in qconditions:
                qcondition = qcondition | q
            objects = objects.filter(qcondition)

        return objects.distinct()


class ExportableMixin(object):
    def audit_export(self):
        self.last_export = datetime.now(timezone.utc)
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
    text_fields = ['name']
    related_fields = {
        'tag': 'tag__name',
        'artist': 'artist__name',
        'genre': 'artist__genre',
    }

    omni_fields = ['name', 'artist', 'tag']

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
    play_count = models.IntegerField(default=0)
    last_play = models.DateTimeField(null=True)

    plex_filename = models.CharField(max_length=255, null=True)
    plex_guid = models.CharField(max_length=255, null=True)
    plex_key = models.CharField(max_length=255, null=True, db_index=True)

    class Meta:
        ordering = ['-id']

    @property
    def albums(self):
        return [t.album for t in Track.objects.filter(song=self.id)]

    def tags(self, category=None):
        tags = [t.name for t in self.tag_set.all()]
        if category:
            tags_for_category = [t.name for t in Tag.objects.filter(category=category)]
            tags = list(set(tags).intersection(set(tags_for_category)))
        return tags

    def add_tag(self, tag_name):
        if self.tag_set.filter(name=tag_name).exists():
            return False
        tag, created = Tag.objects.get_or_create(name=tag_name)
        self.tag_set.add(tag)
        return True

    def remove_tag(self, tag_name):
        if not self.tag_set.filter(name=tag_name).exists():
            return False
        tag = Tag.objects.get(name=tag_name)
        self.tag_set.remove(tag)
        return True

    def __str__(self):
        return "{} ({})".format(self.name, self.artist.name)

    @classmethod
    def list(cls, song_filters=None, album_filters=None, omni_filter=''):
        songs = Song.objects.all()

        if song_filters:
            songs = Song.filter_queryset(songs, song_filters)
        filtered_songs = songs

        if album_filters:
            filtered_albums = Album.filter_queryset(Album.objects.all(), album_filters)
            album_ids = filtered_albums.values_list('id', flat=True)
            songs = songs.filter(track__album__in=album_ids)
        else:
            filtered_albums = Album.objects.all()

        if omni_filter:
            omni_filtered_song_ids = Track.objects.filter(
                models.Q(album__in=Album.filter_queryset(filtered_albums, omni_filter=omni_filter)) |
                models.Q(song__in=Song.filter_queryset(filtered_songs, omni_filter=omni_filter))
            ).values_list('song_id', flat=True)
            songs = songs.filter(id__in=omni_filtered_song_ids)

        return songs.distinct()


class Playlist(models.Model):
    name = models.CharField(max_length=127, null=True)
    plex_guid = models.CharField(max_length=255, null=True)
    plex_key = models.CharField(max_length=255, null=True)
    plex_count = models.IntegerField(default=0)
    song_filters = models.TextField(null=True)
    album_filters = models.TextField(null=True)
    omni_filter = models.TextField(null=True)

    def __str__(self):
        return self.name

    @property
    def songs(self):
        return Song.list(
            song_filters=self.song_filters,
            album_filters=self.album_filters,
            omni_filter=self.omni_filter,
        )


class Album(models.Model, FilterMixin, ExportableMixin):
    bool_fields = ['is_mix']
    text_fields = ['name']
    related_fields = {}

    omni_fields = ['name']

    name = models.CharField(max_length=255)
    date_acquired = models.DateTimeField(null=True)
    starred = models.BooleanField(default=False)
    is_mix = models.BooleanField(default=False)

    export_count = models.IntegerField(default=0)
    last_export = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    @classmethod
    def list(cls, album_filters=None, song_filters=None, omni_filter=''):
        albums = Album.objects.all()

        if album_filters:
            albums = Album.filter_queryset(albums, album_filters)
        filtered_albums = Album.objects.all()

        if song_filters:
            filtered_songs = Song.filter_queryset(Song.objects.all(), song_filters)
            song_ids = filtered_songs.values_list('id', flat=True)
            albums = albums.filter(track__song__in=song_ids)
        else:
            filtered_songs = Song.objects.all()

        if omni_filter:
            omni_filtered_album_ids = Track.objects.filter(
                models.Q(album__in=Album.filter_queryset(filtered_albums, omni_filter=omni_filter)) |
                models.Q(song__in=Song.filter_queryset(filtered_songs, omni_filter=omni_filter))
            ).values_list('album_id', flat=True)
            albums = albums.filter(id__in=omni_filtered_album_ids)

        return albums.distinct()

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
    def completion_text(self):
        if self.completion > 0 and self.completion < 100:
            return "({}% complete)".format(round(self.completion))
        return ""

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

    def to_json(self):
        return {
            "acronym": self.acronym,
            "acronym_size": self.acronym_size,
            "artist": self.artist,
            "cover_art_filename": self.cover_art_filename,
            "export_html": self.export_html,
            "color": self.color.to_json() if self.color else {},
            "completion_text": self.completion_text,
            "stats": self.stats(),
            "id": self.id,
            "name": self.name,
            "date_acquired": self._format_date(self.date_acquired),
            "export_count": self.export_count,
            "last_export": self._format_date(self.last_export),
            "starred": self.starred,
        }

    def _format_date(self, date):
        if not date:
            return ""
        return date.strftime("%b %d, %Y")


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

    @classmethod
    def all_categories(cls):
        return sorted(set(cls.objects.filter(category__isnull=False).values_list("category", flat=True)))


class Color(models.Model):
    name = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=8, default='ffffff')
    white_text = models.BooleanField(default=False)

    def __str__(self):
        return "{} (#{})".format(self.name, self.hex_code)

    def to_json(self):
        return {
            "name": self.name,
            "hex_code": self.hex_code,
            "white_text": self.white_text,
        }
