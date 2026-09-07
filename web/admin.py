from django.contrib import admin
from .models import Customer, KeywordMetric, Lead, License, MediaAsset, Partner, Product, SiteSection

admin.site.site_header = "إدارة منصة كاجو"
admin.site.site_title = "كاجو"
admin.site.index_title = "مركز إدارة المنصة"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "category", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name_ar", "name_en", "slug")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "created_at")
    search_fields = ("name", "phone")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("key", "product", "customer", "status", "expires_at")
    list_filter = ("status", "product")
    search_fields = ("key", "customer__name")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "commission_rate", "is_active")
    list_filter = ("is_active", "region")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "stage", "created_at")
    list_filter = ("stage",)
    search_fields = ("name", "phone")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "placement", "product", "is_active", "updated_at")
    list_filter = ("type", "placement", "product", "is_active")
    search_fields = ("title", "alt_text", "placement")


@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    list_display = ("title_ar", "page", "key", "order", "is_visible", "updated_at")
    list_filter = ("page", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("title_ar", "title_en", "key", "body_ar", "body_en")
    fieldsets = (
        ("الموقع", {"fields": ("key", "page", "order", "is_visible")}),
        ("المحتوى العربي", {"fields": ("eyebrow_ar", "title_ar", "accent_ar", "body_ar")}),
        ("English content", {"fields": ("eyebrow_en", "title_en", "accent_en", "body_en")}),
    )


@admin.register(KeywordMetric)
class KeywordMetricAdmin(admin.ModelAdmin):
    list_display = ("keyword", "monthly_volume", "difficulty", "rank", "updated_at")
    search_fields = ("keyword",)
