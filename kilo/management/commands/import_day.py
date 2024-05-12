from datetime import datetime
import math
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError

from kilo.models import Day, Workout


class Command(BaseCommand):
    @property
    def help(self):
        return "Import a day and workouts, interactively"

    def add_arguments(self, parser):
        parser.add_argument('day', help="YYYY-MM-DD")

    def handle(self, *args, **options):
        day = options['day']
        day_is_valid = False
        while not day_is_valid:
            try:
                day = datetime.strptime(day, "%Y-%m-%d").date()
                day_is_valid = True
            except ValueError:
                day = input(f"Bad date {day}, try again (YYYY-MM-DD): ")

        notes = input("Notes? ")
        new_day = Day(day=day, notes=notes)
        new_day.save()

        workouts = []
        while input("Add workout (y/n)? ").lower() == "y":
            sets = None
            reps = None
            weight = None

            activity = input("Activity? ")
            if activity in ['running', 'erging']:
                time_is_valid = False
                try:
                    distance = float(input("Distance? "))
                except ValueError:
                    distance = None
                    seconds = None
                    time_is_valid = True
                while not time_is_valid:
                    time_parts = input("Time? ").split(":")
                    try:
                        seconds = sum([math.pow(60, index) * float(value) for index, value in enumerate(reversed(time_parts))])
                        time_is_valid = True
                    except ValueError:
                        pass
                if activity == "running":
                    distance_unit = "mi"
                elif distance:
                    distance_unit = "km" if distance < 100 else "m"
            elif input("Does this have reps/sets (y/n)? ") == "y":
                sets = int(input("Sets? "))
                reps = int(input("Reps? "))
                weight = int(input("Weight? "))

            workouts.append(Workout(
                activity=activity,
                seconds=seconds,
                distance=distance,
                distance_unit=distance_unit,
                sets=sets,
                reps=reps,
                weight=weight,
                day=new_day,
            ))

        if input("Save (y/n)? ").lower() == "y":
            with transaction.atomic():
                for workout in workouts:
                    workout.save()

            print(f"Created {new_day.day} with {len(workouts)} workout(s): " + ", ".join([w.activity for w in workouts]))
        else:
            new_day.delete()
