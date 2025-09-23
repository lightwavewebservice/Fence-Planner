from django.core.management.base import BaseCommand
from fence_calculator.models import Material


class Command(BaseCommand):
    help = "Update wire material name to remove (500m roll) suffix"

    def handle(self, *args, **options):
        try:
            # Find the material with the old name
            old_material = Material.objects.get(name="Wire - 2.5mm HT (500m roll)")
            
            # Update the name
            old_material.name = "Wire - 2.5mm HT"
            old_material.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully updated wire material name from "Wire - 2.5mm HT (500m roll)" to "Wire - 2.5mm HT"'
                )
            )
            
        except Material.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    'Material "Wire - 2.5mm HT (500m roll)" not found. It may already be updated or not exist.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating material name: {e}')
            )
