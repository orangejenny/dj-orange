from django.db import models


ROLE_CHOICES = (
    ('F', 'Follower'),
    ('L', 'Leader'),
)

DIVISION_CHOICES = (
    ('0', 'Newcomer'),
    ('N', 'Novice'),
    ('I', 'Intermediate'),
    ('A', 'Advanced'),
    ('AS', 'All Star'),
    ('C', 'Champion'),
)

AGE_DIVISIONS = ('Masters', 'Sophisticated')

ROUND_CHOICES = (
    ('P', 'Prelim'),
    ('Q', 'Quarter'),
    ('S', 'Semi'),
    ('F', 'Final'),
)


class Person(models.Model):
    name = models.CharField(max_length=63, unique=True)     # duplicate names can be accounted for within but not across competitions

class Event(models.Model):
    name = models.CharField(max_length=63)
    date = models.DateTimeField()

class Competition(models.Model):
    #event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event = models.CharField(max_length=63)
    role = models.CharField(choices=ROLE_CHOICES, max_length=2, null=True)
    division = models.CharField(choices=DIVISION_CHOICES, max_length=2)
    _round = models.CharField(choices=ROUND_CHOICES, max_length=2)
    
class RowScore(models.Model):
    #competitor = models.ForeignKey(Person, on_delete=models.CASCADE)
    competitor = models.CharField(max_length=63)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    promote = models.BooleanField(null=True)

class ColumnScore(models.Model):
    #judge = models.ForeignKey(Person, on_delete=models.CASCADE)
    judge = models.CharField(max_length=63)
    score = models.CharField(max_length=3)     # Y, N, A, or numbered rank
    row_score = models.ForeignKey(RowScore, on_delete=models.CASCADE)
