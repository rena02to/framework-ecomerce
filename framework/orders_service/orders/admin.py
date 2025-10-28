from django.contrib import admin
from .models import (
    Order,
    ProductOrder,
    PaymentMethod,
    Shipping,
    TrackingStatus,
    TrackingEvent,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "value",
        "delivery_value",
        "payment_method",
        "timestamp",
    )
    search_fields = ("id", "user_id")
    readonly_fields = ("timestamp",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active")
    search_fields = ("name",)


@admin.register(ProductOrder)
class ProductOrder(admin.ModelAdmin):
    list_display = ("id", "order", "product_id", "value", "amount")
    autocomplete_fields = ("order",)
    list_select_related = ("order",)
    search_fields = ("id", "order_id")


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "address",
        "estimated_delivery",
        "delivered",
        "receiver",
        "traking_code",
    )
    autocomplete_fields = ("order",)
    search_fields = ("id", "order_id", "traking_code")


@admin.register(TrackingStatus)
class TrackingStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
    )
    search_fields = ("id", "name")


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ("id", "shipping", "status", "timestamp")
    search_fields = ("id",)
    list_select_related = ("shipping", "status")
    autocomplete_fields = ("shipping", "status")


admin.site.site_url = "SGBD - Serviço de compras"
admin.site.index_title = "SGBD - Serviço de compras"
admin.site.site_header = "SGBD - Serviço de compras"
