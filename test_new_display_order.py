#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_fence_planner.settings')
django.setup()

from fence_calculator.models import FenceType
from fence_calculator.utils import calculate_fence_requirements
from decimal import Decimal

print('=== Testing New Display Order with Stay Posts and Triplex ===')

# Test standard fence (no netting)
standard_fence = FenceType.objects.filter(name='2_wire_electric', is_active=True).first()
if standard_fence:
    print(f'\n--- Standard Fence (No Netting) ---')
    
    # Test calculation for 1000m fence
    result = calculate_fence_requirements(
        fence_type=standard_fence,
        fence_length=Decimal('1000'),
        labor_rate=Decimal('55')
    )
    
    print(f'Calculation results for 1000m fence:')
    print(f'  Fence type: {standard_fence.display_name}')
    print(f'  Fence length: 1000m')
    
    # Materials
    print(f'\n  MATERIALS:')
    print(f'    Posts required: {result["posts_required"]}')
    print(f'    Wire rolls required: {result["wire_rolls_required"]}')
    
    # Check for stay posts
    if result["material_costs"].get("stay_posts"):
        print(f'    5 inch stay posts: {result["material_costs"]["stay_posts"]["quantity"]}')
    else:
        print(f'    5 inch stay posts: NOT FOUND')
    
    # Check for triplex
    if result["material_costs"].get("triplex"):
        print(f'    Triplex: {result["material_costs"]["triplex"]["quantity"]}')
    else:
        print(f'    Triplex: NOT FOUND')
    
    # Check for strainers
    if result["material_costs"].get("strainers"):
        print(f'    Strainers: {result["material_costs"]["strainers"]["quantity"]}')
    else:
        print(f'    Strainers: NOT FOUND')
    
    # Check for netting
    if result["material_costs"].get("netting"):
        print(f'    Netting rolls: {result["material_costs"]["netting"]["quantity"]}')
    else:
        print(f'    Netting rolls: NOT REQUIRED')
    
    # Check for battens
    if result["material_costs"].get("battens"):
        print(f'    Battens: {result["material_costs"]["battens"]["quantity"]}')
    else:
        print(f'    Battens: NOT REQUIRED')
    
    # Labor
    print(f'\n  LABOR:')
    print(f'    Labor hours: {result["labor_hours"]}')
    print(f'    Labor cost: ${result["labor_cost"]}')
    
    # Totals
    print(f'\n  TOTALS:')
    print(f'    Material total: ${result["total_material_cost"]}')
    print(f'    Total (excl. GST): ${result["total_cost"]}')

print('\nTest completed successfully!')
