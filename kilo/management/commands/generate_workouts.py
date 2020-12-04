from datetime import datetime, timedelta
import lorem
import random

from django.core.management.base import BaseCommand, CommandError

from kilo.models import Day, Workout


class Command(BaseCommand):
    @property
    def help(self):
        return '''
            Generate semi-realistic random workouts.
        '''

    def add_arguments(self, parser):
        parser.add_argument('start', help="Approximate YYYY-MM-DD date to start generating workouts")
        parser.add_argument('end', help="Approximate YYYY-MM-DD date to finish generating workouts")

    def handle(self, *args, **options):
        start = self._parse_date(options['start'])
        end = self._parse_date(options['end'])

        today = end
        while today >= start:
            today -= timedelta(days=random.choice([1, 1, 2]))
            if Day.objects.filter(day=today).exists():
                print(f"Skipping {today} because it already exists")
                continue
            day = Day(day=today, notes=lorem.sentence())
            day.save()
            try:
                workout = random.choice([
                   self._generate_erg,
                   self._generate_erg,
                   self._generate_run,
                   self._generate_run,
                   self._generate_other,
                ])(day)
                workout.save()
            except Exception:
                day.delete()
            print(f"Saved day: {day.day}: {workout.activity}")

    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
           print(f"Bad date {date_str}")
           exit(1)

    def _generate_erg(self, day):
        distance = random.choice([2, 6])
        time = random.randint(470, 490) if distance == 2 else random.randint(1480, 1550)
        return Workout(
            day=day,
            activity='erging',
            distance_unit=Workout.KILOMETERS,
            distance=distance,
            seconds=time,
        )

    def _generate_run(self, day):
        distance = random.choice([4, 4, 5, 5, 10])
        pace = random.randint(480, 600)
        return Workout(
            day=day,
            activity='running',
            distance_unit=Workout.MILES,
            distance=distance,
            seconds=distance * pace,
        )

    def _generate_other(self, day):
        return Workout(
            day=day,
            activity=random.choice(['crossfit', 'stairs']),
        )
