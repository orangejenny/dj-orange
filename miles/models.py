from django.db import models

class Day(models.Model):
    day = models.DateField(unique_for_date=True)
    notes = models.CharField(max_length=1024, null=True)

class Workout(models.Model):
    MILES = 'mi'
    METERS = 'm'
    KILOMETERS = 'km'
    DISTANCE_UNITS = [
        (MILES, MILES),
        (KILOMETERS, KILOMETERS),
        (METERS, METERS),
    ]

    activity = models.CharField(max_length=32)
    time = models.SmallIntegerField(null=True)
    distance = models.FloatField(null=True)
    distance_unit = models.CharField(null=True, max_length=3, choices=DISTANCE_UNITS, default=MILES)
    sets = models.SmallIntegerField(null=True)
    reps = models.SmallIntegerField(null=True)
    weight = models.SmallIntegerField(null=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
