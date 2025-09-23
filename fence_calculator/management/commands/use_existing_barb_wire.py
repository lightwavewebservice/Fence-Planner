from django.core.management.base import BaseCommand
from fence_calculator.models import Material, FenceType


class Command(BaseCommand):
    help = "Use existing Wire - Barb (ID 8) and remove Wire - Barb (500m roll)"

    def handle(self, *args, **options):
        try:
            # Find both barb wire materials
            existing_barb = Material.objects.filter(id=8, name="Wire - Barb").first()
            duplicate_barb = Material.objects.filter(name="Wire - Barb (500m roll)").first()
            
            if not existing_barb:
                self.stdout.write(
                    self.style.ERROR(
                        'Wire - Barb material (ID 8) not found!'
                    )
                )
                return
            
            self.stdout.write(f"Using existing Wire - Barb (ID: {existing_barb.id})")
            self.stdout.write(f"  - Roll length: {existing_barb.roll_length}m")
            self.stdout.write(f"  - Price: ${existing_barb.current_price}")
            
            if duplicate_barb:
                self.stdout.write(f"Found duplicate: {duplicate_barb.name} (ID: {duplicate_barb.id})")
                
                # Update fence types that use the duplicate to use the existing one
                fence_types_updated = 0
                for fence_type in FenceType.objects.all():
                    updated = False
                    
                    if fence_type.wire_material == duplicate_barb:
                        fence_type.wire_material = existing_barb
                        updated = True
                        self.stdout.write(f"Updated {fence_type.display_name} wire_material to use existing Wire - Barb")
                    
                    if fence_type.barb_wire_material == duplicate_barb:
                        fence_type.barb_wire_material = existing_barb
                        updated = True
                        self.stdout.write(f"Updated {fence_type.display_name} barb_wire_material to use existing Wire - Barb")
                    
                    if updated:
                        fence_type.save()
                        fence_types_updated += 1
                
                # Delete the duplicate
                duplicate_name = duplicate_barb.name
                duplicate_barb.delete()
                self.stdout.write(f"Deleted duplicate '{duplicate_name}' material")
                self.stdout.write(f"Updated {fence_types_updated} fence types")
            else:
                self.stdout.write("No duplicate Wire - Barb (500m roll) found")
            
            # Ensure all fence types have barb_wire_material set to the existing barb wire
            fence_types_without_barb = FenceType.objects.filter(barb_wire_material__isnull=True)
            for fence_type in fence_types_without_barb:
                fence_type.barb_wire_material = existing_barb
                fence_type.save()
                self.stdout.write(f"Set barb wire material for {fence_type.display_name}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully configured to use existing Wire - Barb (ID: {existing_barb.id})'
                )
            )
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error configuring barb wire materials: {e}')
            )
