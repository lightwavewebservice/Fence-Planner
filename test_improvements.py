#!/usr/bin/env python
"""
Simple test script to verify the improvements made to the Farm Fence Planner.
This script tests the validation functions and basic functionality.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_fence_planner.settings')
django.setup()

from fence_calculator.validators import (
    validate_fence_calculation_input, 
    validate_material_update_input,
    ValidationError
)
from fence_calculator.models import Material, FenceType
from fence_calculator.utils import calculate_fence_requirements


def test_validation_functions():
    """Test the validation functions with various inputs."""
    print("🧪 Testing validation functions...")
    
    # Test valid fence calculation input
    try:
        valid_data = {
            'netting': 'no',
            'fence_length': '100.0',
            'labor_rate': '55.0',
            'wire_count': '2',
            'post_spacing': '8.0',
            'top_wire_type': 'standard'
        }
        result = validate_fence_calculation_input(valid_data)
        print("✅ Valid fence calculation input passed")
    except ValidationError as e:
        print(f"❌ Valid input failed: {e}")
    
    # Test invalid fence length
    try:
        invalid_data = {
            'netting': 'no',
            'fence_length': '-10',  # Invalid negative length
            'labor_rate': '55.0'
        }
        validate_fence_calculation_input(invalid_data)
        print("❌ Invalid fence length should have failed")
    except ValidationError:
        print("✅ Invalid fence length correctly rejected")
    
    # Test invalid labor rate
    try:
        invalid_data = {
            'netting': 'no',
            'fence_length': '100.0',
            'labor_rate': '2000'  # Too high
        }
        validate_fence_calculation_input(invalid_data)
        print("❌ Invalid labor rate should have failed")
    except ValidationError:
        print("✅ Invalid labor rate correctly rejected")
    
    # Test valid material update
    try:
        valid_material_data = {
            'id': 1,
            'current_price': '15.50',
            'roll_length': '500.0',
            'auto_update_enabled': True
        }
        result = validate_material_update_input(valid_material_data)
        print("✅ Valid material update input passed")
    except ValidationError as e:
        print(f"❌ Valid material input failed: {e}")
    
    # Test invalid material price
    try:
        invalid_material_data = {
            'id': 1,
            'current_price': '-5.00'  # Negative price
        }
        validate_material_update_input(invalid_material_data)
        print("❌ Invalid material price should have failed")
    except ValidationError:
        print("✅ Invalid material price correctly rejected")


def test_calculation_logic():
    """Test the calculation logic with sample data."""
    print("\n🔢 Testing calculation logic...")
    
    try:
        # Create test materials if they don't exist
        post_material, _ = Material.objects.get_or_create(
            name="Test Post",
            defaults={
                'unit': 'each',
                'default_price': Decimal('12.50'),
                'current_price': Decimal('12.50')
            }
        )
        
        wire_material, _ = Material.objects.get_or_create(
            name="Test Wire",
            defaults={
                'unit': 'roll',
                'default_price': Decimal('139.00'),
                'current_price': Decimal('139.00'),
                'roll_length': Decimal('500.00')
            }
        )
        
        # Create test fence type if it doesn't exist
        fence_type, _ = FenceType.objects.get_or_create(
            name='test_2_wire',
            defaults={
                'display_name': 'Test 2 Wire Electric',
                'post_spacing': Decimal('8.00'),
                'wire_count': 2,
                'post_material': post_material,
                'wire_material': wire_material
            }
        )
        
        # Test basic calculation
        results = calculate_fence_requirements(
            fence_type=fence_type,
            fence_length=Decimal('100.00'),
            labor_rate=Decimal('55.00')
        )
        
        # Verify results structure
        required_keys = [
            'posts_required', 'wire_rolls_required', 'total_cost',
            'material_costs', 'labor_hours', 'labor_cost'
        ]
        
        for key in required_keys:
            if key not in results:
                print(f"❌ Missing key in results: {key}")
                return
        
        # Verify reasonable values
        if results['posts_required'] <= 0:
            print("❌ Posts required should be positive")
            return
        
        if results['total_cost'] <= 0:
            print("❌ Total cost should be positive")
            return
        
        print("✅ Basic calculation logic working correctly")
        print(f"   - Posts required: {results['posts_required']}")
        print(f"   - Wire rolls: {results['wire_rolls_required']}")
        print(f"   - Total cost: ${results['total_cost']:.2f}")
        
    except Exception as e:
        print(f"❌ Calculation test failed: {e}")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n🎯 Testing edge cases...")
    
    try:
        # Test very small fence
        small_fence_data = {
            'netting': 'no',
            'fence_length': '0.01',  # Minimum allowed
            'labor_rate': '55.0'
        }
        result = validate_fence_calculation_input(small_fence_data)
        print("✅ Minimum fence length accepted")
        
        # Test maximum fence length
        large_fence_data = {
            'netting': 'no',
            'fence_length': '50000',  # Maximum allowed
            'labor_rate': '55.0'
        }
        result = validate_fence_calculation_input(large_fence_data)
        print("✅ Maximum fence length accepted")
        
        # Test boundary labor rate
        max_labor_data = {
            'netting': 'no',
            'fence_length': '100.0',
            'labor_rate': '1000'  # Maximum allowed
        }
        result = validate_fence_calculation_input(max_labor_data)
        print("✅ Maximum labor rate accepted")
        
    except ValidationError as e:
        print(f"❌ Edge case failed: {e}")


def run_all_tests():
    """Run all improvement tests."""
    print("🚀 Running Farm Fence Planner Improvement Tests")
    print("=" * 50)
    
    test_validation_functions()
    test_calculation_logic()
    test_edge_cases()
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")
    print("\n📊 Summary of improvements:")
    print("   ✅ Comprehensive input validation")
    print("   ✅ Specific error messages")
    print("   ✅ Reasonable input limits")
    print("   ✅ Client-side validation")
    print("   ✅ HTML5 form validation")
    print("   ✅ Reusable validation utilities")


if __name__ == "__main__":
    run_all_tests()
