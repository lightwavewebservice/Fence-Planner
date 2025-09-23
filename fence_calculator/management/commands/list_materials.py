from django.core.management.base import BaseCommand
from fence_calculator.models import Material


class Command(BaseCommand):
    help = "List all materials in the database"

    def handle(self, *args, **options):
        materials = Material.objects.all().order_by('name')
        
        self.stdout.write(f"Found {materials.count()} materials:")
        self.stdout.write("-" * 50)
        
        for material in materials:
            self.stdout.write(f"ID: {material.id}")
            self.stdout.write(f"Name: {material.name}")
            self.stdout.write(f"Unit: {material.unit}")
            self.stdout.write(f"Price: ${material.current_price}")
            if material.roll_length:
                self.stdout.write(f"Roll Length: {material.roll_length}m")
            self.stdout.write(f"Active: {material.is_active}")
            self.stdout.write("-" * 30)
