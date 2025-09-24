from django.core.management.base import BaseCommand
from django.conf import settings
from decimal import Decimal

from fence_calculator.models import Material


class Command(BaseCommand):
    help = "Ensure the Staples Material exists with the configured defaults"

    def handle(self, *args, **options):
        name = getattr(settings, 'STAPLES_MATERIAL_NAME', 'U Staples (Box of 2000)')
        default_price = Decimal(str(getattr(settings, 'STAPLES_DEFAULT_PRICE', 183.99)))

        mat, created = Material.objects.get_or_create(
            name=name,
            defaults={
                'description': 'Fence staples',
                'unit': 'box',
                'default_price': default_price,
                'current_price': default_price,
                'is_active': True,
            }
        )

        if not created:
            updated = False
            if mat.unit != 'box':
                mat.unit = 'box'
                updated = True
            # If no current_price set, or zero, apply default
            if not mat.current_price or Decimal(mat.current_price) == Decimal('0'):
                mat.current_price = default_price
                updated = True
            if not mat.default_price or Decimal(mat.default_price) == Decimal('0'):
                mat.default_price = default_price
                updated = True
            if not mat.is_active:
                mat.is_active = True
                updated = True
            if updated:
                mat.save()
                self.stdout.write(self.style.SUCCESS(f"Updated existing material: {mat.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Material already up to date: {mat.name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created material: {mat.name}"))
