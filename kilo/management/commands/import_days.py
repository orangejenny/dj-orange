from argparse import RawTextHelpFormatter
from datetime import date
import json
import re

from django.core.management.base import BaseCommand, CommandError

from kilo.models import Day


class Command(BaseCommand):
    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    @property
    def help(self):
        return "Import days from a json file. Query: select day, notes from days"

    def add_arguments(self, parser):
        parser.add_argument('filename', help="JSON file of data => [item, item...]")
        parser.add_argument('--save', action='store_true')

    def handle(self, *args, **options):
        filename = options['filename']
        save = options['save']

        with open(filename, encoding='utf-8') as f:
            data = json.load(f)['data']
            for item in data:
                day_parts = [int(part) for part in re.split(r'\D+', item['day'])]
                day = Day(day=date(year=day_parts[0], month=day_parts[1], day=day_parts[2]), notes=item['notes'])
                if save:
                    day.save()
            self.stdout.write("{}Imported {} days".format("" if save else "[DRY RUN] ", len(data)))

