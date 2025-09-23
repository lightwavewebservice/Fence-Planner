from django.contrib import admin
from .models import Material, Supplier, SupplierPrice, FenceType, FenceCalculation, PriceSource, ScrapingSettings


@admin.action(description="Enable auto-update")
def enable_auto_update(modeladmin, request, queryset):
    queryset.update(auto_update_enabled=True)


@admin.action(description="Disable auto-update")
def disable_auto_update(modeladmin, request, queryset):
    queryset.update(auto_update_enabled=False)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "current_price", "default_price", "price_source", "last_price_update", "auto_update_enabled", "is_active")
    search_fields = ("name", "description", "price_source")
    list_filter = ("auto_update_enabled", "is_active")
    actions = [enable_auto_update, disable_auto_update]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "contact_phone", "website", "is_active")
    search_fields = ("name", "contact_email")
    list_filter = ("is_active",)


@admin.register(SupplierPrice)
class SupplierPriceAdmin(admin.ModelAdmin):
    list_display = ("material", "supplier", "price", "last_updated")
    search_fields = ("material__name", "supplier__name")
    list_filter = ("supplier",)


@admin.register(FenceType)
class FenceTypeAdmin(admin.ModelAdmin):
    list_display = ("display_name", "name", "post_spacing", "wire_count", "is_active")
    search_fields = ("display_name", "name")
    list_filter = ("is_active",)


@admin.register(FenceCalculation)
class FenceCalculationAdmin(admin.ModelAdmin):
    list_display = ("id", "fence_type", "fence_length", "total_cost", "created_at")
    search_fields = ("fence_type__display_name",)
    list_filter = ("fence_type", "created_at")
    date_hierarchy = "created_at"


@admin.register(PriceSource)
class PriceSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "region", "currency", "excludes_gst", "last_scraped", "scrape_interval_hours", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("name", "base_url")


@admin.register(ScrapingSettings)
class ScrapingSettingsAdmin(admin.ModelAdmin):
    list_display = ("auto_scraping_enabled", "default_scrape_interval_hours", "max_retries", "timeout_seconds", "last_global_scrape")
