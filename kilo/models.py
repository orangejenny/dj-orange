import math

from django.db import models


class Day(models.Model):
    day = models.DateField(unique_for_date=True)
    notes = models.CharField(max_length=1024, null=True)

    class Meta:
        ordering = ["-day"]

    def primary_activity(self):
        return self.workout_set.last().activity if self.workout_set.count() else None

    def average_pace_seconds(self):
        first = self.workout_set.first()
        if first is None:
            return None

        if self.workout_set.count() == 1:
            return first.pace_seconds(first.distance, first.distance_unit, first.seconds)

        workouts = self.workout_set.filter(distance=first.distance, distance_unit=first.distance_unit)
        if workouts.count():
            return Workout.pace_seconds(first.distance,
                                        first.distance_unit,
                                        sum([w.seconds for w in workouts if w.seconds]) / workouts.count())

        return None

    def to_json(self):
        return {
            "id": self.id,
            "day": self.day,
            "notes": self.notes,
            "workouts": [w.to_json() for w in self.workout_set.all()],
        }


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

    @classmethod
    def _time(cls, seconds):
        if seconds is None:
            return None

        remaining = float(seconds)
        hours = math.floor(remaining / 3600)
        remaining -= hours * 3600
        minutes = math.floor(remaining / 60)
        remaining -= minutes * 60
        seconds = round(remaining, 1) if int(seconds) != float(seconds) else int(remaining)

        hours = f"{hours}:" if hours else ""
        minutes = f"{cls._pad(minutes) if hours else minutes}:"
        return f"{hours}{minutes}{cls._pad(seconds)}"

    @classmethod
    def _pad(cls, num):
        return f"0{num}" if num < 10 else str(num)

    @classmethod
    def pace_seconds(cls, distance, distance_unit, seconds):
        if not distance or not seconds:
            return None

        if distance_unit == Workout.MILES:
            # Minutes per mile, to the second
            return round(seconds / distance)
        elif distance_unit == Workout.KILOMETERS:
            # Minutes per 500m, to the tenth of a second
            return round(seconds / distance / 2, 1)
        elif distance_unit == Workout.METERS:
            # Minutes per 500m, to the tenth of a second
            return round(seconds / distance * 500, 1)

        return None

    @property
    def pace(self):
        return self._time(self.pace_seconds(self.distance, self.distance_unit, self.seconds))

    def to_json(self):
        return {
            "id": self.id,
            "activity": self.activity,
            "seconds": self.seconds,
            "distance": self.distance,
            "distance_unit": self.distance_unit,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
        }

    def faster_than(self, other):
        if self.pace is None or other.pace is None:
            return None

        return self.seconds / self.m < other.seconds / other.m

    def primary_stat(self):
        if self.activity == "erging":
            return self.pace

        if self.activity == "running":
            return f"{self.mi} mi at {self.pace}"

        return None

    def secondary_stat(self):
        return self.day.day
