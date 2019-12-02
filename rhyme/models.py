from django.conf import settings
from django.db import models

import os
import re

class Song(models.Model):
    name = models.CharField(max_length=127)
    artist = models.CharField(max_length=63)
    filename = models.CharField(max_length=255, null=True)
    rating = models.IntegerField(null=True)
    mood = models.IntegerField(null=True)
    energy = models.IntegerField(null=True)
    starred = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    @property
    def albums(self):
        return [t.album.name for t in Track.objects.filter(song=self.id)]

    @property
    def tags(self):
        return [t.tag.name for t in SongTag.objects.filter(song=self.id)]

    def __str__(self):
        return "{} ({})".format(self.name, self.artist)

    @classmethod
    def list(cls, filters=None):
        kwargs = {}
        if filters:
            for condition in filters.split("&&"):
                (lhs, op, rhs) = re.match(r'(\w+)\s*([<>=*]*)\s*(\S.*)', condition).groups()
                if lhs in ['starred']:
                    kwargs[lhs] = rhs
                elif lhs in ['rating', 'energy', 'mood']:
                    if op == '>=':
                        lhs = lhs + "__gte"
                    elif op == '<=':
                        lhs = lhs + "__lte"
                    elif op != '=':
                        raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                    kwargs[lhs] = rhs
                elif lhs in ['name', 'artist']:
                    if op == '=*':
                        lhs = lhs + "__icontains"
                    elif op == '=':
                        lhs = lhs + "__iexact"
                    else:
                        raise Exception("Unrecognized op for {}: {}".format(lhs, op))
                    kwargs[lhs] = rhs
                elif lhs == 'tag':
                    # TODO
                    pass
                else:
                    raise Exception("Unrecognized lhs {}".format(lhs))
        return cls.objects.filter(**kwargs)


class Album(models.Model):
    name = models.CharField(max_length=255)
    date_acquired = models.DateTimeField(null=True)
    starred = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @classmethod
    def list(cls):
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

    @property
    def artist(self):
        artists = [song.artist for song in self.songs]
        if len(set(artists)) == 1:
            return artists[0]
        return "Various Artists"

    @property
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

    @property
    def songs(self):
        return [track.song for track in self.track_set.all()]


class Track(models.Model):
    ordinal = models.IntegerField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "album")

    def __str__(self):
        return "{}: {}. {}".format(str(self.album), self.ordinal, str(self.song))


class Tag(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class SongTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("song", "tag")

    def __str__(self):
        return "{} => {}".format(self.song, self.tag)
