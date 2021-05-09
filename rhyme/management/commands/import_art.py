from django.core.management.base import BaseCommand

from rhyme.models import Album


class Command(BaseCommand):
    @property
    def help(self):
        return "Import album art"

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, filename, *args, **options):
        album = None
        while album is None:
            album_name = input("Album name? ")
            candidates = Album.objects.filter(name__icontains=album_name)
            if candidates.count() == 0:
                print("Nothing found.")
                continue
            if candidates.count() == 1:
                album = candidates.first()
            else:
                candidates = list(candidates)
                for i, candidate in enumerate(candidates):
                    print(f"{i + 1}. {candidate.name}")
                try:
                    index = int(input("Which album? "))
                    album = candidates[index - 1]
                except (IndexError, ValueError):
                    pass

        album_dir = "rhyme/static/rhyme/img/collections"
        print(f"mkdir {album_dir}/{album.id}")

        extension = filename.split(".")[-1]
        print(f"scp {filename}
        {settings.DEPLOY_USERNAME}@{settings.DEPLOY_SERVER}:{settings.DEPLOY_BASE_DIR}/{album_dir}/1.{extension}")
