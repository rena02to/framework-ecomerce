from rest_framework import serializers
from .models import (
    Order,
    PaymentMethod,
    ProductOrder,
    Shipping,
    TrackingStatus,
    TrackingEvent,
)
from orders_service.utils.requests import call_service
from babel.numbers import format_currency


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["user_id", "payment_method", "value", "delivery_value"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["name", "active"]


class ProductOrderSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = ProductOrder
        fields = ["product_id", "value", "amount"]

    def get_value(self, obj):
        return format_currency(obj.value, "BRL", locale="pt_BR")


class ShippingSerializer(serializers.ModelSerializer):
    estimated_delivery = serializers.DateField(format="%d/%m/%Y")
    delivered_in = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%s")

    class Meta:
        model = Shipping
        fields = [
            "address",
            "estimated_delivery",
            "delivered",
            "receiver",
            "delivered_in",
            "traking_code",
        ]


class TrackingEventSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%s")

    class Meta:
        model = TrackingEvent
        fields = ["status", "timestamp"]

    def get_status(self, obj):
        return {
            "name": obj.status.name,
            "description": obj.status.description if obj.status.description else None,
        }


class OrderViewSerializer(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%d/%m/%Y - %H:%M")
    products = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()
    traking_events = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "payment_method",
            "value",
            "delivery_value",
            "timestamp",
            "products",
            "shipping",
            "traking_events",
        ]

    def get_payment_method(self, obj):
        return obj.payment_method.name

    def get_products(self, obj):
        products_instance = ProductOrder.objects.filter(order__id=obj.id)
        return ProductOrderSerializer(products_instance, many=True).data

    def get_shipping(self, obj):
        shipping = Shipping.objects.get(order__id=obj.id)
        return ShippingSerializer(shipping, many=False).data

    def get_traking_events(self, obj):
        shipping = obj.order_shipping.id
        trakings = TrackingEvent.objects.filter(shipping__id=shipping)
        return TrackingEventSerializer(trakings, many=True).data
