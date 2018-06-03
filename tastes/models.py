from django.db import models

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
    def list(cls):
        return cls.objects.all()[:20]



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
