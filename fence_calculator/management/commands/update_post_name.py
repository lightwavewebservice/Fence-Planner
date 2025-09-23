from django.core.management.base import BaseCommand
from fence_calculator.models import Material


class Command(BaseCommand):
    help = "Update post material name to '5inch posts'"

    def handle(self, *args, **options):
        try:
            # Find the post material
            post_material = Material.objects.filter(name__icontains='post').filter(name__icontains='standard').first()
            
            if post_material:
                old_name = post_material.name
                post_material.name = "5inch posts"
                post_material.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated post material name from "{old_name}" to "5inch posts"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Post material not found. Looking for materials containing "post" and "standard".'
                    )
                )
                
                # List all materials containing "post"
                post_materials = Material.objects.filter(name__icontains='post')
                if post_materials.exists():
                    self.stdout.write("Found materials containing 'post':")
                    for material in post_materials:
                        self.stdout.write(f"  - {material.name} (ID: {material.id})")
                else:
                    self.stdout.write("No materials found containing 'post'")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating post material name: {e}')
            )
