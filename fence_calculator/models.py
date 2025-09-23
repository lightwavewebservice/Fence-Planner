from __future__ import annotations
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Material(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], null=True, blank=True)
    roll_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, 
                                    help_text="Roll length in meters (for wire materials)")
    price_source = models.CharField(max_length=200, blank=True)
    price_source_url = models.URLField(blank=True)
    last_price_update = models.DateTimeField(null=True, blank=True)
    auto_update_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.current_price is None:
            self.current_price = self.default_price
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class SupplierPrice(TimeStampedModel):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    last_updated = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('material', 'supplier')

    def __str__(self) -> str:
        return f"{self.material} @ {self.supplier}"


class FenceType(TimeStampedModel):
    NAME_CHOICES = [
        ('2_wire_electric', '2 Wire Electric'),
        ('3_wire_electric', '3 Wire Electric'),
        ('9_wire_hot', '9 Wire Hot'),
        ('9_wire_barb', '9 Wire Barb'),
        ('netting_hot', 'Netting + Hot'),
        ('deer', 'Deer Fence'),
    ]

    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    post_spacing = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    wire_count = models.PositiveIntegerField()

    requires_insulators = models.BooleanField(default=False)
    requires_strainers = models.BooleanField(default=True)
    requires_energiser = models.BooleanField(default=False)

    # Material FKs
    post_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='post_fence_types', null=True, blank=True)
    wire_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='wire_fence_types', null=True, blank=True)
    barb_wire_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='barb_wire_fence_types', null=True, blank=True)
    netting_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='netting_fence_types', null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.display_name or self.get_name_display()


class FenceCalculation(models.Model):
    fence_type = models.ForeignKey(FenceType, on_delete=models.PROTECT)
    fence_length = models.DecimalField(max_digits=10, decimal_places=2)

    posts_required = models.PositiveIntegerField()
    wire_length_meters = models.DecimalField(max_digits=10, decimal_places=2)
    wire_rolls_required = models.DecimalField(max_digits=8, decimal_places=2)

    labor_hours = models.DecimalField(max_digits=6, decimal_places=2)
    labor_rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)

    material_costs = models.JSONField(default=dict)
    total_material_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    price_overrides = models.JSONField(default=dict, blank=True)
    user_session = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Calc #{self.pk} - {self.fence_type} ({self.fence_length} m)"


class PriceSource(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)

    region = models.CharField(max_length=100, default='Southland')
    currency = models.CharField(max_length=10, default='NZD')
    excludes_gst = models.BooleanField(default=True)

    last_scraped = models.DateTimeField(null=True, blank=True)
    scrape_interval_hours = models.PositiveIntegerField(default=24)

    def __str__(self) -> str:
        return self.name


class ScrapingSettings(TimeStampedModel):
    auto_scraping_enabled = models.BooleanField(default=False)
    default_scrape_interval_hours = models.PositiveIntegerField(default=24)
    max_retries = models.PositiveIntegerField(default=2)
    timeout_seconds = models.PositiveIntegerField(default=10)
    user_agent = models.CharField(max_length=255, default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36')
    last_global_scrape = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_settings(cls) -> 'ScrapingSettings':
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return 'Scraping Settings'
