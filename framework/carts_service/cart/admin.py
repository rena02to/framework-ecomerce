from django.contrib import admin
from .models import Cart, ProductCart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id")
    search_fields = ("id", "user_id")


@admin.register(ProductCart)
class ProductCartAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product_id", "amount")
    search_fields = ("id", "cart__id")
    list_select_related = ("cart",)
    autocomplete_fields = ("cart",)


admin.site.site_url = "SGBD - Serviço de carrinho"
admin.site.index_title = "SGBD - Serviço de carrinho"
admin.site.site_header = "SGBD - Serviço de carrinho"
