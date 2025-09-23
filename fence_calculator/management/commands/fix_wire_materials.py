from django.core.management.base import BaseCommand
from fence_calculator.models import Material, FenceType


class Command(BaseCommand):
    help = "Fix wire material names and update fence types"

    def handle(self, *args, **options):
        try:
            # Find the materials
            old_wire = Material.objects.get(name="Wire - 2.5mm HT (500m roll)")
            
            # Check if there's already a "Wire - 2.5mm HT" material
            try:
                new_wire = Material.objects.get(name="Wire - 2.5mm HT")
                self.stdout.write(f"Found existing 'Wire - 2.5mm HT' material (ID: {new_wire.id})")
                
                # Update the existing material to have the correct properties from the old one
                new_wire.default_price = old_wire.default_price
                new_wire.current_price = old_wire.current_price
                new_wire.roll_length = old_wire.roll_length
                new_wire.save()
                
                self.stdout.write(f"Updated 'Wire - 2.5mm HT' with price ${new_wire.current_price} and roll length {new_wire.roll_length}m")
                
            except Material.DoesNotExist:
                # If no existing material, just rename the old one
                new_wire = old_wire
                new_wire.name = "Wire - 2.5mm HT"
                new_wire.save()
                self.stdout.write(f"Renamed material to 'Wire - 2.5mm HT'")
            
            # Update all fence types that use the old material
            fence_types_updated = 0
            for fence_type in FenceType.objects.all():
                updated = False
                
                if fence_type.wire_material == old_wire:
                    fence_type.wire_material = new_wire
                    updated = True
                
                if fence_type.barb_wire_material == old_wire:
                    fence_type.barb_wire_material = new_wire
                    updated = True
                
                if updated:
                    fence_type.save()
                    fence_types_updated += 1
                    self.stdout.write(f"Updated fence type: {fence_type.display_name}")
            
            # If we had duplicates, delete the old one
            if old_wire.id != new_wire.id:
                old_wire.delete()
                self.stdout.write(f"Deleted duplicate material 'Wire - 2.5mm HT (500m roll)'")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully fixed wire materials. Updated {fence_types_updated} fence types.'
                )
            )
            
        except Material.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    'Material "Wire - 2.5mm HT (500m roll)" not found.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fixing materials: {e}')
            )
