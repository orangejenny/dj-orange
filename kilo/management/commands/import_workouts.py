from argparse import RawTextHelpFormatter
from datetime import date
import json
import re

from django.core.management.base import BaseCommand, CommandError

from kilo.models import Day Workout


class Command(BaseCommand):
    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    @property
    def help(self):
        return '''
            Import workouts from a json file. Associated days must already exist.
            Query: select day, activity, time, distance, sets, reps, weight, unit from days, workouts where workouts.day_id = days.id
        '''

    def add_arguments(self, parser):
        parser.add_argument('filename', help="JSON file of data => [item, item...]")
        parser.add_argument('--save', action='store_true')

    def handle(self, *args, **options):
        filename = options['filename']
        save = options['save']

        with open(filename, encoding='utf-8') as f:
            data = json.load(f)['data']
            for item in data:
                day_parts = re.split(r'\D+', item['day'])
                day = date(year=day_parts[0], month=day_parts[1], day=day_parts[2])
                try:
                    pass
                    # TODO
                    #day = Album.objects.get(id=item['collectionid'])
                except Day.DoesNotExist:
                    # TODO
                    pass
                workout = Workout(
                    activity=item['activity'],
                    seconds=item['time'],
                    distance=item['distance'],
                    distance_unit=item['unit'],
                    sets=item['sets'],
                    reps=item['reps'],
                    weight=item['weight'],
                    day=day,
                )
                if save:
                    workout.save()
                '''
            self.stdout.write("{}Imported {} workouts".format("" if save else "[DRY RUN] ", len(data)))

