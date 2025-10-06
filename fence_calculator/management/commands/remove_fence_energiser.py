from django.core.management.base import BaseCommand

from fence_calculator.models import Material


class Command(BaseCommand):
    help = "Remove the legacy 'Fence Energiser' material from the database"

    def handle(self, *args, **options):
        qs = Material.objects.filter(name__iexact='Fence Energiser')
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No 'Fence Energiser' material found."))
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} 'Fence Energiser' material record(s)."))
