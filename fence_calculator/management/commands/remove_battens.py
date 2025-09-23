from django.core.management.base import BaseCommand
from fence_calculator.models import Material, FenceType


class Command(BaseCommand):
    help = "Remove battens from materials and update fence types"

    def handle(self, *args, **options):
        try:
            # First, update fence types to remove batten requirements
            fence_types = FenceType.objects.filter(requires_battens=True)
            fence_type_count = fence_types.count()
            
            if fence_type_count > 0:
                self.stdout.write(f"Found {fence_type_count} fence types requiring battens:")
                for fence_type in fence_types:
                    self.stdout.write(f"  - {fence_type.display_name}")
                    fence_type.requires_battens = False
                    fence_type.batten_spacing = None
                    fence_type.batten_material = None
                    fence_type.save()
                
                self.stdout.write(f"Updated {fence_type_count} fence types to remove batten requirements")
            else:
                self.stdout.write("No fence types requiring battens found")
            
            # Also update any fence types that have batten_material set
            fence_types_with_battens = FenceType.objects.filter(batten_material__isnull=False)
            for fence_type in fence_types_with_battens:
                self.stdout.write(f"Removing batten material from: {fence_type.display_name}")
                fence_type.batten_material = None
                fence_type.save()
            
            # Now remove batten materials
            batten_materials = Material.objects.filter(name__icontains='batten')
            batten_count = batten_materials.count()
            
            if batten_count > 0:
                self.stdout.write(f"Found {batten_count} batten materials:")
                for material in batten_materials:
                    self.stdout.write(f"  - {material.name} (ID: {material.id})")
                
                # Remove batten materials
                batten_materials.delete()
                self.stdout.write(f"Deleted {batten_count} batten materials")
            else:
                self.stdout.write("No batten materials found")
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully removed battens from materials and calculations'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error removing battens: {e}')
            )
