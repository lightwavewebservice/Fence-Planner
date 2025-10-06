from decimal import Decimal
from typing import Any, Dict
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import json

from .models import Material, FenceType, FenceCalculation
from .utils import calculate_fence_requirements


class MaterialModelTest(TestCase):
    def setUp(self):
        self.material = Material.objects.create(
            name="Test Post",
            unit="each",
            default_price=Decimal('10.00'),
            description="Test material"
        )

    def test_material_creation(self):
        """Test material is created with correct defaults"""
        self.assertEqual(self.material.name, "Test Post")
        self.assertEqual(self.material.current_price, Decimal('10.00'))
        self.assertTrue(self.material.is_active)
        self.assertFalse(self.material.auto_update_enabled)

    def test_current_price_defaults_to_default_price(self):
        """Test current_price is set to default_price when None"""
        material = Material.objects.create(
            name="Test Wire",
            unit="roll",
            default_price=Decimal('100.00')
        )
        self.assertEqual(material.current_price, Decimal('100.00'))


class FenceTypeModelTest(TestCase):
    def setUp(self):
        self.post_material = Material.objects.create(
            name="Standard Post",
            unit="each",
            default_price=Decimal('12.50')
        )
        self.wire_material = Material.objects.create(
            name="HT Wire",
            unit="roll",
            default_price=Decimal('139.00'),
            roll_length=Decimal('500.00')
        )
        
        self.fence_type = FenceType.objects.create(
            name='2_wire_electric',
            display_name='2 Wire Electric',
            post_spacing=Decimal('8.00'),
            wire_count=2,
            post_material=self.post_material,
            wire_material=self.wire_material
        )

    def test_fence_type_creation(self):
        """Test fence type is created correctly"""
        self.assertEqual(self.fence_type.display_name, '2 Wire Electric')
        self.assertEqual(self.fence_type.wire_count, 2)
        self.assertEqual(self.fence_type.post_spacing, Decimal('8.00'))
        self.assertTrue(self.fence_type.is_active)


class FenceCalculationUtilsTest(TestCase):
    def setUp(self):
        self.post_material = Material.objects.create(
            name="Standard Post",
            unit="each",
            default_price=Decimal('12.50')
        )
        self.wire_material = Material.objects.create(
            name="HT Wire",
            unit="roll",
            default_price=Decimal('139.00'),
            roll_length=Decimal('500.00')
        )

        self.electric_fence = FenceType.objects.create(
            name='2_wire_electric',
            display_name='2 Wire Electric',
            post_spacing=Decimal('8.00'),
            wire_count=2,
            post_material=self.post_material,
            wire_material=self.wire_material
        )

        self.deer_netting = Material.objects.create(
            name="Deer Netting 200cm",
            unit="roll",
            default_price=Decimal('310.00'),
            roll_length=Decimal('100.00')
        )
        self.outrigger_wire = Material.objects.create(
            name="Electric Outrigger Wire",
            unit="roll",
            default_price=Decimal('120.00'),
            roll_length=Decimal('400.00')
        )

        self.deer_fence = FenceType.objects.create(
            name='deer',
            display_name='Deer Fence',
            post_spacing=Decimal('6.00'),
            wire_count=0,
            post_material=self.post_material,
            wire_material=self.outrigger_wire,
            netting_material=self.deer_netting
        )

    def test_basic_electric_fence_calculation(self):
        results = calculate_fence_requirements(
            fence_type=self.electric_fence,
            fence_length=Decimal('100.00'),
            labor_rate=Decimal('55.00'),
            netting_type='none'
        )

        expected_posts = 100 // 8 + 1 + 1
        self.assertEqual(results['posts_required'], expected_posts)
        self.assertEqual(results['wire_count_used'], 2)
        self.assertEqual(results['wire_length_meters'], 200.0)
        self.assertEqual(results['wire_rolls_required'], 1.0)
        expected_labor_hours = 100 / 200
        self.assertEqual(results['labor_hours'], expected_labor_hours)
        self.assertIn('posts', results['material_costs'])
        self.assertIn('wire_standard', results['material_costs'])
        self.assertGreater(results['total_material_cost'], 0)
        self.assertGreater(results['total_cost'], 0)

    def test_deer_fence_calculation(self):
        results = calculate_fence_requirements(
            fence_type=self.deer_fence,
            fence_length=Decimal('60.00'),
            labor_rate=Decimal('55.00'),
            netting_type='deer',
            electric_outrigger=False
        )

        expected_posts = 60 // 6 + 1 + 1
        self.assertEqual(results['posts_required'], expected_posts)
        self.assertEqual(results['netting_type'], 'deer')
        self.assertEqual(results['netting_height_cm'], 200.0)
        self.assertIn('netting', results['material_costs'])
        self.assertNotIn('battens', results['material_costs'])

    def test_deer_fence_with_outrigger(self):
        results = calculate_fence_requirements(
            fence_type=self.deer_fence,
            fence_length=Decimal('120.00'),
            labor_rate=Decimal('55.00'),
            netting_type='deer',
            electric_outrigger=True
        )

        self.assertTrue(results['electric_outrigger'])
        self.assertIn('outrigger_wire', results['material_costs'])
        details = results['electric_outrigger_details']
        self.assertIn('wire_rolls', details)
        self.assertGreater(details['wire_rolls'], 0)

    def test_price_overrides(self):
        price_overrides = {
            str(self.post_material.id): Decimal('15.00'),
            str(self.wire_material.id): Decimal('150.00'),
        }

        results = calculate_fence_requirements(
            fence_type=self.electric_fence,
            fence_length=Decimal('100.00'),
            netting_type='none',
            price_overrides=price_overrides
        )

        post_cost = results['material_costs']['posts']
        self.assertEqual(post_cost['unit_price'], 15.00)
        wire_cost = results['material_costs']['wire_standard']
        self.assertEqual(wire_cost['unit_price'], 150.00)

    def test_hot_wire_calculation(self):
        Material.objects.create(name="Bullnose Insulator", unit="each", default_price=Decimal('2.50'))
        Material.objects.create(name="Claw Insulator", unit="each", default_price=Decimal('1.80'))

        results = calculate_fence_requirements(
            fence_type=self.electric_fence,
            fence_length=Decimal('100.00'),
            netting_type='none',
            top_wire_type='hot',
            hot_wire_count=2
        )

        self.assertIn('insulators_bullnose', results['material_costs'])
        self.assertIn('insulators_claw', results['material_costs'])
        self.assertEqual(results['insulator_counts']['bullnose'], 4)
        self.assertGreater(results['insulator_counts']['claw'], 0)

    def test_zero_length_fence(self):
        results = calculate_fence_requirements(
            fence_type=self.electric_fence,
            fence_length=Decimal('0.00'),
            netting_type='none'
        )

        self.assertEqual(results['posts_required'], 1)
        self.assertEqual(results['wire_length_meters'], 0.0)
        self.assertEqual(results['wire_rolls_required'], 0.0)

    def test_very_long_fence(self):
        results = calculate_fence_requirements(
            fence_type=self.electric_fence,
            fence_length=Decimal('5000.00'),
            netting_type='none'
        )

        self.assertGreater(results['posts_required'], 0)
        self.assertGreater(results['wire_rolls_required'], 0)
        self.assertGreater(results['total_cost'], 0)


class FenceCalculationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test materials and fence types
        self.post_material = Material.objects.create(
            name="Standard Post",
            unit="each",
            default_price=Decimal('12.50')
        )
        self.wire_material = Material.objects.create(
            name="HT Wire",
            unit="roll",
            default_price=Decimal('139.00'),
            roll_length=Decimal('500.00')
        )
        
        self.fence_type = FenceType.objects.create(
            name='2_wire_electric',
            display_name='2 Wire Electric',
            post_spacing=Decimal('8.00'),
            wire_count=2,
            post_material=self.post_material,
            wire_material=self.wire_material
        )

    def test_index_view(self):
        """Test the main index page loads correctly"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Farm Fence Planner')
        self.assertContains(response, 'Calculator')

    def test_calculate_api_valid_input(self):
        """Test calculation API with valid input"""
        data = {
            'netting_type': 'none',
            'fence_length': '100.0',
            'labor_rate': '55.0',
            'wire_count': '2',
            'post_spacing': '8.0',
            'top_wire_type': 'standard'
        }
        
        response = self.client.post(
            reverse('calculate'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Check response structure
        self.assertIn('posts_required', result)
        self.assertIn('wire_rolls_required', result)
        self.assertIn('total_cost', result)
        self.assertIn('calculation_id', result)

    def test_calculate_api_invalid_input(self):
        """Test calculation API with invalid input"""
        data = {
            'netting_type': 'none',
            'fence_length': 'invalid',  # Invalid number
        }
        
        response = self.client.post(
            reverse('calculate'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)

    def test_calculation_detail_view(self):
        """Test calculation detail view"""
        # Create a calculation first
        calc = FenceCalculation.objects.create(
            fence_type=self.fence_type,
            fence_length=Decimal('100.00'),
            posts_required=13,
            wire_length_meters=Decimal('200.00'),
            wire_rolls_required=Decimal('1.00'),
            labor_hours=Decimal('0.50'),
            labor_rate_per_hour=Decimal('55.00'),
            labor_cost=Decimal('27.50'),
            material_costs={},
            total_material_cost=Decimal('300.00'),
            total_cost=Decimal('327.50')
        )
        
        response = self.client.get(reverse('calculation_detail', args=[calc.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Calculation #{calc.pk}')
        self.assertContains(response, '100 m')

    def test_api_fence_types(self):
        """Test fence types API endpoint"""
        response = self.client.get(reverse('api_fence_types'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('fence_types', data)
        self.assertEqual(len(data['fence_types']), 1)
        self.assertEqual(data['fence_types'][0]['name'], '2_wire_electric')

    def test_api_materials(self):
        """Test materials API endpoint"""
        response = self.client.get(reverse('api_materials'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('materials', data)
        self.assertEqual(len(data['materials']), 2)  # post and wire materials


class FenceCalculationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a complete set of materials for deer fence
        self.post_material = Material.objects.create(
            name="Standard Post", unit="each", default_price=Decimal('12.50')
        )
        self.wire_material = Material.objects.create(
            name="HT Wire", unit="roll", default_price=Decimal('139.00'),
            roll_length=Decimal('500.00')
        )
        self.netting_material = Material.objects.create(
            name="Deer Netting 200cm", unit="roll", default_price=Decimal('310.00'),
            roll_length=Decimal('100.00')
        )
        self.outrigger_wire = Material.objects.create(
            name="Electric Outrigger Wire", unit="roll", default_price=Decimal('120.00'),
            roll_length=Decimal('400.00')
        )

        # Create deer fence type
        self.deer_fence = FenceType.objects.create(
            name='deer',
            display_name='Deer Fence',
            post_spacing=Decimal('6.00'),
            wire_count=0,
            post_material=self.post_material,
            wire_material=self.outrigger_wire,
            netting_material=self.netting_material
        )

    def test_full_deer_fence_workflow(self):
        """Test complete deer fence calculation workflow"""
        # Step 1: Calculate deer fence
        data = {
            'netting_type': 'deer',
            'fence_length': '300.0',
            'labor_rate': '60.0',
            'wire_count': '0',
            'post_spacing': '6.0',
            'electric_outrigger': True
        }

        response = self.client.post(
            reverse('calculate'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        calc_id = result['calculation_id']
        self.assertEqual(result['netting_type'], 'deer')
        self.assertTrue(result['electric_outrigger'])
        self.assertIn('netting_height_cm', result)

        # Step 2: Verify calculation was saved
        calc = FenceCalculation.objects.get(pk=calc_id)
        self.assertEqual(calc.fence_type.name, 'deer')
        self.assertEqual(calc.fence_length, Decimal('300.00'))
        self.assertEqual(calc.netting_type, 'deer')
        self.assertTrue(calc.electric_outrigger)
        self.assertEqual(calc.netting_height_cm, Decimal('200'))

        # Step 3: Test detail view
        response = self.client.get(reverse('calculation_detail', args=[calc_id]))
        self.assertEqual(response.status_code, 200)

        # Step 4: Test PDF export
        response = self.client.get(reverse('export_pdf', args=[calc_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        # Step 5: Test Excel export
        response = self.client.get(reverse('export_excel', args=[calc_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
