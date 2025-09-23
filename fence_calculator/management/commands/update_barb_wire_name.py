from django.core.management.base import BaseCommand
from fence_calculator.models import Material


class Command(BaseCommand):
    help = "Update Wire - Barb (500m roll) to Wire - Barb"

    def handle(self, *args, **options):
        try:
            # Find the barb wire material with (500m roll) suffix
            barb_wire = Material.objects.filter(name="Wire - Barb (500m roll)").first()
            
            if barb_wire:
                old_name = barb_wire.name
                barb_wire.name = "Wire - Barb"
                barb_wire.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated material name from "{old_name}" to "Wire - Barb"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Material "Wire - Barb (500m roll)" not found.'
                    )
                )
                
                # List barb wire materials for reference
                barb_materials = Material.objects.filter(name__icontains='barb')
                if barb_materials.exists():
                    self.stdout.write("Found materials containing 'barb':")
                    for material in barb_materials:
                        self.stdout.write(f"  - {material.name} (ID: {material.id})")
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating barb wire material name: {e}')
            )
