from fence_calculator.models import FenceType
from fence_calculator.utils import calculate_fence_requirements
from decimal import Decimal

# Get the 2 wire electric fence type
fence_type = FenceType.objects.get(name='2_wire_electric')

print(f"Fence type: {fence_type.display_name}")
print(f"Wire material: {fence_type.wire_material} (ID: {fence_type.wire_material.id})")
print(f"Barb wire material: {fence_type.barb_wire_material} (ID: {fence_type.barb_wire_material.id if fence_type.barb_wire_material else None})")

# Test calculation with hot top wire
results = calculate_fence_requirements(
    fence_type=fence_type,
    fence_length=Decimal('100.00'),
    labor_rate=Decimal('55.00'),
    top_wire_type='hot',
    top_wire_count=1
)

print("\nMaterial costs:")
for key, value in results['material_costs'].items():
    if 'wire' in key.lower():
        print(f"  {key}: {value}")
