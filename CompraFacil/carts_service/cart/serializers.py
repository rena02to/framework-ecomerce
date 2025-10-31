from rest_framework import serializers
from .models import ProductCart


class ProductCartSerializer(serializers.ModelSerializer):
    cart = serializers.SerializerMethodField()

    class Meta:
        model = ProductCart
        fields = ["cart", "product_id", "amount", "updated_at"]

    def get_cart(self, obj):
        return obj.cart.id
