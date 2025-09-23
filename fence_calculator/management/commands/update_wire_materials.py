from django.core.management.base import BaseCommand
from fence_calculator.models import Material, FenceType


class Command(BaseCommand):
    help = "Remove Wire - Hot (500m roll) and update fence types to use correct wire materials"

    def handle(self, *args, **options):
        try:
            # Find the materials
            hot_wire = Material.objects.filter(name="Wire - Hot (500m roll)").first()
            ht_wire = Material.objects.filter(name="Wire - 2.5mm HT").first()
            barb_wire = Material.objects.filter(name="Wire - Barb (500m roll)").first()
            
            if not ht_wire:
                self.stdout.write(
                    self.style.ERROR('Wire - 2.5mm HT material not found!')
                )
                return
                
            if not barb_wire:
                self.stdout.write(
                    self.style.ERROR('Wire - Barb (500m roll) material not found!')
                )
                return
            
            # Update fence types that use hot wire material
            if hot_wire:
                fence_types_updated = 0
                for fence_type in FenceType.objects.all():
                    updated = False
                    
                    # If fence type uses hot wire material, switch to HT wire
                    if fence_type.wire_material == hot_wire:
                        fence_type.wire_material = ht_wire
                        updated = True
                        self.stdout.write(f"Updated {fence_type.display_name} wire_material to Wire - 2.5mm HT")
                    
                    # Update barb wire material reference
                    if fence_type.barb_wire_material == hot_wire:
                        fence_type.barb_wire_material = ht_wire
                        updated = True
                        self.stdout.write(f"Updated {fence_type.display_name} barb_wire_material to Wire - 2.5mm HT")
                    
                    if updated:
                        fence_type.save()
                        fence_types_updated += 1
                
                self.stdout.write(f"Updated {fence_types_updated} fence types")
                
                # Delete the hot wire material
                hot_wire.delete()
                self.stdout.write(f"Deleted 'Wire - Hot (500m roll)' material")
            else:
                self.stdout.write("Wire - Hot (500m roll) material not found")
            
            # Update fence types to set proper barb wire material
            fence_types_with_barb = FenceType.objects.filter(barb_wire_material__isnull=True)
            for fence_type in fence_types_with_barb:
                fence_type.barb_wire_material = barb_wire
                fence_type.save()
                self.stdout.write(f"Set barb wire material for {fence_type.display_name}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully updated wire materials configuration'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating wire materials: {e}')
            )
