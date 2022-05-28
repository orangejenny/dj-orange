from django.core.management.base import BaseCommand

from rhyme.models import Tag


class Command(BaseCommand):
    @property
    def help(self):
        return "Assign categories to tags"

    def handle(self, *args, **options):
        categories = Tag.objects.filter(category__isnull=False).values_list("category", flat=True).distinct()
        categories = sorted(categories)
        tags = Tag.objects.filter(category__isnull=True).order_by('?')

        print(f"{tags.count()} tags are missing a category")
        for i, tag in enumerate(tags):
            if i % 5 == 0:
                for category in categories:
                    print(category)

            saved = False
            while not saved:
                choice = input(f"{tag.name} (q to skip): ").lower()
                if choice == "q":
                    saved = True
                else:
                    matches = [c for c in categories if c.startswith(choice)]
                    if len(matches) == 1:
                        tag.category = matches[0]
                        tag.save()
                        saved = True
                    else:
                        print(f"Ambigous choice: {' '.join(matches)}")

        print("Done!")
