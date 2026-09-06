import os

from django.conf import settings
from django.core.management.base import BaseCommand

from tinytag import TinyTag

from rhyme.models import Song


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('config', help="Name of config")

    def handle(self, *args, **options):
        try:
            config = [c for c in settings.RHYME_EXPORT_CONFIGS if c["name"] == options.get("config")][0]
        except IndexError:
            raise ExportConfigNotFoundException(f"Could not find {config_name}, options are: {[c['name'] for c in settings.RHYME_EXPORT_CONFIGS]}")

        self.read_tags(config)

        self.export_bpm("out.csv")

        # ...then parse the file on the proper server and update the db

    def read_tags(self, config):
        songs = Song.objects.filter(bpm__isnull=True).order_by("?")
        count = 0
        print(f"Found {songs.count()} songs")
        for song in songs:
            filename = config["prefix"] + song.filename
            #print(filename)
            if not os.path.exists(filename):
                print(f"Could not find {filename}")
                continue
            tag = TinyTag.get(filename)
            bpm = tag.other.get('bpm')
            if bpm and len(bpm):
                #print(f"{song.name}: {bpm}")
                song.bpm = int(float(bpm[0]))
                song.save()
                count += 1
        print(f"Songs with bpm: {count}")

    def export_bpm(self, filename):
        songs = Song.objects.filter(bpm__isnull=False)

        lines = [f"{song.bpm},{song.filename}" for song in songs]

        # Note this is a terrible CSV because it doesn't escape the filenames, it just puts BPM as the first column
        with open(filename, "w") as fout:
            fout.write("\n".join(lines))
            print(f"Wrote {filename}")
