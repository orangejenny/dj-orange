from django.core.management.base import BaseCommand

from rhyme.models import Song

class Command(BaseCommand):
    def handle(self, *args, **options):
        raise Exception("Subclasses should override this method")

    def get_song(self):
        seed = None
        while seed is None:
            name = input("Song name? ")
            songs = Song.objects.filter(name__icontains=name)
            if songs.count() > 7:
                artist = input("Artist? ")
                songs = songs.filter(artist__name__icontains=artist)
            if songs.count() == 1:
                seed = songs.first()
            elif songs.count() > 1:
                for i, song in enumerate(songs):
                    print(f"{i + 1}) {song}")
                ordinal = input("Which song? ")
                try:
                    seed = songs[int(ordinal) - 1]
                except (ValueError, IndexError):
                    pass
        return seed

    def print_numbered_list(self, things):
        for index, thing in enumerate(things):
            print(f"{index + 1}) {thing}")
