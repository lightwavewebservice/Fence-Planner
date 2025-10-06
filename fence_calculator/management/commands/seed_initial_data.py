from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone

from fence_calculator.models import Material, FenceType


class Command(BaseCommand):
    help = "Seed initial materials and fence types for demo"

    def handle(self, *args, **options):
        # Materials
        post, _ = Material.objects.get_or_create(
            name="5inch posts",
            defaults=dict(
                description="Standard treated wooden fence post",
                unit="each",
                default_price=Decimal('12.50'),
                current_price=Decimal('12.50'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )
        wire, _ = Material.objects.get_or_create(
            name="Wire - 2.5mm HT",
            defaults=dict(
                description="High tensile wire roll",
                unit="roll",
                default_price=Decimal('139.00'),
                current_price=Decimal('139.00'),
                roll_length=Decimal('500.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        # Additional materials
        claw_ins, _ = Material.objects.get_or_create(
            name="Claw Insulator",
            defaults=dict(
                description="Claw insulator for hot wire",
                unit="each",
                default_price=Decimal('0.69'),
                current_price=Decimal('0.69'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )
        bullnose_ins, _ = Material.objects.get_or_create(
            name="Bullnose Insulator",
            defaults=dict(
                description="Bullnose insulator for hot wire",
                unit="each",
                default_price=Decimal('2.46'),
                current_price=Decimal('2.46'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )
        strainer, _ = Material.objects.get_or_create(
            name="2.5/7 inch Strainer",
            defaults=dict(
                description="2.5/7 inch strainer",
                unit="each",
                default_price=Decimal('37.70'),
                current_price=Decimal('37.70'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        # Additional wire materials for barb option
        barb_wire, _ = Material.objects.get_or_create(
            name="Wire - Barb",
            defaults=dict(
                description="Barb wire roll",
                unit="roll",
                default_price=Decimal('200.00'),
                current_price=Decimal('200.00'),
                roll_length=Decimal('240.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        deer_posts, _ = Material.objects.get_or_create(
            name="Deer Posts",
            defaults=dict(
                description="2.4 m posts suitable for 2.0 m deer fencing",
                unit="each",
                default_price=Decimal('19.50'),
                current_price=Decimal('19.50'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        sheep_netting, _ = Material.objects.get_or_create(
            name="Standed Netting",
            defaults=dict(
                description="Standard stock netting, approximately 90 cm height",
                unit="roll",
                default_price=Decimal('210.00'),
                current_price=Decimal('210.00'),
                roll_length=Decimal('100.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        deer_netting, _ = Material.objects.get_or_create(
            name="Deer Netting",
            defaults=dict(
                description="High tensile woven deer netting, 200 cm height",
                unit="roll",
                default_price=Decimal('310.00'),
                current_price=Decimal('310.00'),
                roll_length=Decimal('100.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        outrigger_wire, _ = Material.objects.get_or_create(
            name="Electric Outrigger Wire",
            defaults=dict(
                description="Polywire suitable for deer outrigger",
                unit="roll",
                default_price=Decimal('120.00'),
                current_price=Decimal('120.00'),
                roll_length=Decimal('400.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        outrigger_insulators, _ = Material.objects.get_or_create(
            name="Outrigger Insulator",
            defaults=dict(
                description="Insulator clip for outrigger wire",
                unit="each",
                default_price=Decimal('1.20'),
                current_price=Decimal('1.20'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        outrigger_connectors, _ = Material.objects.get_or_create(
            name="Outrigger Connectors",
            defaults=dict(
                description="Connector packs for outrigger wire",
                unit="pack",
                default_price=Decimal('38.00'),
                current_price=Decimal('38.00'),
                price_source="Seed",
                price_source_url="",
                last_price_update=timezone.now(),
                auto_update_enabled=False,
                is_active=True,
            ),
        )

        # Fence Types
        ft_data = [
            dict(
                name='2_wire_electric', display_name='2 Wire Electric',
                description='Basic 2-wire electric fence',
                post_spacing=Decimal('8.0'), wire_count=2,
                requires_insulators=True, requires_strainers=True, requires_energiser=True,
                post_material=post, wire_material=wire, netting_material=None,
            ),
            dict(
                name='3_wire_electric', display_name='3 Wire Electric',
                description='3-wire electric fence',
                post_spacing=Decimal('8.0'), wire_count=3,
                requires_insulators=True, requires_strainers=True, requires_energiser=True,
                post_material=post, wire_material=wire, netting_material=None,
            ),
            dict(
                name='9_wire_hot', display_name='9 Wire Hot',
                description='9-wire with one or more hot wires',
                post_spacing=Decimal('5.0'), wire_count=9,
                requires_insulators=True, requires_strainers=True, requires_energiser=True,
                post_material=post, wire_material=wire, netting_material=None,
            ),
            dict(
                name='netting_hot', display_name='Netting + Hot',
                description='Sheep netting fence with a hot wire',
                post_spacing=Decimal('6.0'), wire_count=1,
                requires_insulators=True, requires_strainers=True, requires_energiser=True,
                post_material=post, wire_material=wire, netting_material=sheep_netting,
            ),
            dict(
                name='deer', display_name='Deer Fence',
                description='2.0 m deer netting with optional electric outrigger',
                post_spacing=Decimal('8.0'), wire_count=0,
                requires_insulators=False, requires_strainers=True, requires_energiser=False,
                post_material=deer_posts, wire_material=outrigger_wire,
                netting_material=deer_netting,
            ),
        ]

        for data in ft_data:
            ft, created = FenceType.objects.get_or_create(
                name=data['name'],
                defaults={k: v for k, v in data.items() if k != 'name'}
            )
            if not created:
                # update links/fields if missing
                for k, v in data.items():
                    if k == 'name':
                        continue
                    setattr(ft, k, v)
                ft.save()

        self.stdout.write(self.style.SUCCESS('Seed data ensured.'))
