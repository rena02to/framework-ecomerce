from django.contrib import admin
from .models import Order, ProductOrder, PaymentMethod


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "value", "display_payment_methods")
    search_fields = ("id", "user_id")
    autocomplete_fields = ("payment_methods",)
    list_select_related = ("payment_methods",)

    def display_payment_methods(self, obj):
        return ", ".join([method.name for method in obj.payment_methods.all()])

    display_payment_methods.short_description = "Payment Method"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("payment_methods")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProductOrder)
class ProductOrder(admin.ModelAdmin):
    list_display = ("id", "order", "product_id", "value", "amount")
    autocomplete_fields = ("order",)
    list_select_related = ("order",)


admin.site.site_url = "SGBD - Serviço de compras"
admin.site.index_title = "SGBD - Serviço de compras"
admin.site.site_header = "SGBD - Serviço de compras"
