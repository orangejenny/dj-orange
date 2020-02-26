
from django.core.management.base import BaseCommand, CommandError

from rhyme.models import Song
from rhyme.views import filenames


class Command(BaseCommand):
    rating_help = "An individual rating or range, e.g., 4 or 3-4"

    def add_arguments(self, parser):
        parser.add_argument('config', help="Name of config")
        parser.add_argument('--rating', help=self.rating_help)
        parser.add_argument('--energy', help=self.rating_help)
        parser.add_argument('--mood', help=self.rating_help)

    def handle(self, *args, **options):
        attrs = ["rating", "energy", "mood"]
        start_values = {}
        end_values = {}
        ranges = {}
        for attr in attrs:
            arg = options.get(attr)
            if arg:
                if "-" in arg:
                    start_values[attr] = int(arg.split("-")[0])
                    end_values[attr] = int(arg.split("-")[1])
                else:
                    start_values[attr] = int(arg)
                    end_values[attr] = int(arg)
                ranges[attr] = end_values[attr] - start_values[attr]
                
        total_time = 60 * 60
        accumulated_time = 0
        songs = set()
        stop = False
        while not stop and accumulated_time < total_time:
            kwargs = {}
            for attr in attrs:
                if attr not in start_values:
                    continue

                ratio = accumulated_time / total_time
                filter_value = round(start_values[attr] + ratio * ranges[attr])
                kwargs[attr] = filter_value
            candidates = Song.objects.filter(time__isnull=False, **kwargs).order_by('?')
            candidates = candidates.exclude(id__in=[song.id for song in songs])
            #print(f"{accumulated_time}, {kwargs}")
            song = candidates.first()
            if song:
                songs.add(song)
                accumulated_time += song.time
            else:
                stop = True

        print(f"Found {len(songs)} songs:")
        for filename in filenames(options.get("config"), songs):
            print(filename)
