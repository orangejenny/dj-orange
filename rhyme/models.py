from django.db import models

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
