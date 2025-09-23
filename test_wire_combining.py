#!/usr/bin/env python
"""
Test script to verify wire combining logic is working correctly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_fence_planner.settings')
django.setup()

from fence_calculator.models import FenceType, Material
from fence_calculator.utils import calculate_fence_requirements
from decimal import Decimal

def test_wire_combining():
    print("=== Testing Wire Combining Logic ===\n")
    
    # Get the 2 wire electric fence type
    try:
        fence_type = FenceType.objects.get(name='2_wire_electric')
        print(f"✓ Found fence type: {fence_type.display_name}")
        print(f"  - Wire material: {fence_type.wire_material} (ID: {fence_type.wire_material.id})")
        print(f"  - Barb wire material: {fence_type.barb_wire_material} (ID: {fence_type.barb_wire_material.id if fence_type.barb_wire_material else 'None'})")
    except FenceType.DoesNotExist:
        print("❌ 2 Wire Electric fence type not found!")
        return
    
    print("\n--- Test 1: Standard wire only ---")
    results_standard = calculate_fence_requirements(
        fence_type=fence_type,
        fence_length=Decimal('100.00'),
        labor_rate=Decimal('55.00'),
        top_wire_type='standard'
    )
    
    wire_entries = {k: v for k, v in results_standard['material_costs'].items() if 'wire' in k.lower()}
    print(f"Wire entries: {len(wire_entries)}")
    for key, value in wire_entries.items():
        print(f"  {key}: {value['material']} - Qty: {value['quantity']} - Cost: ${value['cost']}")
    
    print("\n--- Test 2: Hot wire (should combine) ---")
    results_hot = calculate_fence_requirements(
        fence_type=fence_type,
        fence_length=Decimal('100.00'),
        labor_rate=Decimal('55.00'),
        top_wire_type='hot'
    )
    
    wire_entries = {k: v for k, v in results_hot['material_costs'].items() if 'wire' in k.lower()}
    print(f"Wire entries: {len(wire_entries)}")
    for key, value in wire_entries.items():
        print(f"  {key}: {value['material']} - Qty: {value['quantity']} - Cost: ${value['cost']}")
    
    # Check if combining worked
    if len(wire_entries) == 1:
        print("✅ SUCCESS: Hot wire was combined with standard wire!")
    else:
        print("❌ ISSUE: Hot wire was NOT combined - still showing separate entries")
        
        # Debug info
        print("\nDEBUG INFO:")
        if fence_type.wire_material:
            print(f"Standard wire material: {fence_type.wire_material.name} (ID: {fence_type.wire_material.id})")
        else:
            print("No standard wire material set!")
    
    print("\n--- Test 3: Barb wire (should be separate) ---")
    results_barb = calculate_fence_requirements(
        fence_type=fence_type,
        fence_length=Decimal('100.00'),
        labor_rate=Decimal('55.00'),
        top_wire_type='barb'
    )
    
    wire_entries = {k: v for k, v in results_barb['material_costs'].items() if 'wire' in k.lower()}
    print(f"Wire entries: {len(wire_entries)}")
    for key, value in wire_entries.items():
        print(f"  {key}: {value['material']} - Qty: {value['quantity']} - Cost: ${value['cost']}")
    
    if len(wire_entries) == 2:
        print("✅ SUCCESS: Barb wire correctly shows as separate entry!")
    else:
        print("❌ ISSUE: Expected 2 wire entries for barb wire")

if __name__ == "__main__":
    test_wire_combining()
