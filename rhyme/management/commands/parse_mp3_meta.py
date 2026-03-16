import json
import os

from mutagen import File as MutagenFile

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    @property
    def help(self):
        return "Parse an M3U playlist and write track metadata to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("playlist", type=str, help="Path to an M3U file")

    def handle(self, *args, **options):
        playlist_path = os.path.expanduser(options["playlist"])
        with open(playlist_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        file_paths = [line.strip() for line in lines if line.strip() and not line.startswith("#")]

        track_metadata = []
        for file_path in file_paths:
            audio = MutagenFile(file_path, easy=True)
            if not audio:
                track_metadata.append({})
                continue

            def first(key):
                val = audio.get(key)
                return val[0] if val else None

            duration = int(round(audio.info.length)) if hasattr(audio, "info") and hasattr(audio.info, "length") else None
            track_metadata.append({
                "title": first("title"),
                "artist": first("artist"),
                "album": first("album"),
                "year": first("date"),
                "duration": duration,
            })

        output_path = os.path.splitext(playlist_path)[0] + ".json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(track_metadata, f, indent=2)

        self.stdout.write(f"Wrote {len(track_metadata)} tracks to {output_path}")
