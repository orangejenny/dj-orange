from django.db import models

class Day(models.Model):
    day = models.DateField(unique_for_date=True)
    notes = models.CharField(max_length=1024, null=True)

    class Meta:
        ordering = ["-day"]


class Workout(models.Model):
    MILES = 'mi'
    METERS = 'm'
    KILOMETERS = 'km'
    DISTANCE_UNITS = [
        (MILES, MILES),
        (KILOMETERS, KILOMETERS),
        (METERS, METERS),
    ]

    class Meta:
        ordering = ["ordering"]

    activity = models.CharField(max_length=32)
    time = models.SmallIntegerField(null=True)
    distance = models.FloatField(null=True)
    distance_unit = models.CharField(null=True, max_length=3, choices=DISTANCE_UNITS, default=MILES)
    sets = models.SmallIntegerField(null=True)
    reps = models.SmallIntegerField(null=True)
    weight = models.SmallIntegerField(null=True)
    ordering = models.SmallIntegerField(default=1)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
