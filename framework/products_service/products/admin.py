from django.contrib import admin
from .models import Product, ImageProduct, FeatureProduct, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "value",
        "stock",
        "code",
        "display_categories",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("id", "name", "code")
    list_select_related = ("categories",)
    autocomplete_fields = ("categories",)

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    display_categories.short_description = "Categories"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("categories")


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image", "main")
    search_fields = ("id", "product__id", "product__code")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)


@admin.register(FeatureProduct)
class FeatureProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "value")
    search_fields = ("id", "product__id", "name")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "name")


admin.site.site_url = "SGBD - Serviço de produtos"
admin.site.index_title = "SGBD - Serviço de produtos"
admin.site.site_header = "SGBD - Serviço de produtos"
