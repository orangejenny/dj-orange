import math

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
    seconds = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    distance_unit = models.CharField(null=True, max_length=3, choices=DISTANCE_UNITS, default=MILES)
    sets = models.SmallIntegerField(null=True)
    reps = models.SmallIntegerField(null=True)
    weight = models.SmallIntegerField(null=True)
    ordering = models.SmallIntegerField(default=1)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        units = set(kwargs.keys()) & {u[0] for u in self.DISTANCE_UNITS}
        if len(units) > 1:
            raise ValueError("May only provide one distance, provided: " + ", ".join(units))
        if len(units) == 1:
            unit = list(units)[0]
            kwargs['distance'] = kwargs.pop(unit)
            kwargs['distance_unit'] = unit
        super().__init__(*args, **kwargs)

    @property
    def m(self):
        if self.distance is None:
            return None

        if self.distance_unit == self.METERS:
            return self.distance

        if self.distance_unit == self.KILOMETERS:
            return self.distance * 1000

        if self.distance_unit == self.MILES:
            return self.distance * 1609

        return None

    @property
    def km(self):
        if self.distance is None:
            return None

        if self.distance_unit == self.KILOMETERS:
            return self.distance

        if self.distance_unit == self.METERS:
            return round(self.distance / 1000, 1)

        if self.distance_unit == self.MILES:
            return round(self.distance * 1.6, 1)

        return None

    @property
    def mi(self):
        if self.distance is None:
            return None

        if self.distance_unit == self.MILES:
            return self.distance

        if self.distance_unit == self.KILOMETERS:
            return round(self.distance / 1.6, 2)

        if self.distance_unit == self.METERS:
            return round(self.distance / 1609, 2)

        return None


    @property
    def time(self):
        return self._time(self.seconds)

    def _time(self, seconds):
        if seconds is None:
            return None

        remaining = float(seconds)
        hours = math.floor(remaining / 3600)
        remaining -= hours * 3600
        minutes = math.floor(remaining / 60)
        remaining -= minutes * 60
        seconds = round(remaining, 1) if int(seconds) != float(seconds) else int(remaining)

        hours = f"{hours}:" if hours else ""
        minutes = f"{self._pad(minutes) if hours else minutes}:"
        return f"{hours}{minutes}{self._pad(seconds)}"

    def _pad(self, num):
        return f"0{num}" if num < 10 else str(num)

    @property
    def pace(self):
        if not self.distance or not self.seconds:
            return None

        if self.distance_unit == Workout.MILES:
            # Minutes per mile, to the second
            return self._time(round(self.seconds / self.distance))
        elif self.distance_unit == Workout.KILOMETERS:
            # Minutes per 500m, to the tenth of a second
            return self._time(self.seconds / self.distance / 2)
        elif self.distance_unit == Workout.METERS:
            # Minutes per 500m, to the tenth of a second
            return self._time(self.seconds / self.distance * 500)

        return None

    def faster_than(self, other):
        if self.pace is None or other.pace is None:
            return None

        return self.seconds / self.m > other.seconds > other.m

    def primary_stat(self):
        if self.activity == "erging":
            return self.pace

        if self.activity == "running":
            return f"{self.mi} mi at {self.pace}"

        return None

    def secondary_stat(self):
        return self.day.day
