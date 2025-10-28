from itertools import product
from rest_framework import serializers
from .models import Category, Product, ImageProduct, FeatureProduct
from babel.numbers import format_currency


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["stock"]


class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = ["id", "image"]


class FeatureProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureProduct
        fields = ["id", "name", "value"]


class ProductSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    value_unformat = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "value",
            "stock",
            "categories",
            "images",
            "features",
            "value_unformat",
        ]

    def get_value(self, obj):
        return format_currency(obj.value, "BRL", locale="pt_BR")

    def get_value_unformat(self, obj):
        return obj.value

    def get_features(self, obj):
        features = FeatureProduct.objects.filter(product__id=obj.id)
        return FeatureProductSerializer(features, many=True).data

    def get_categories(self, obj):
        return CategorySerializer(obj.categories, many=True).data

    def get_images(self, obj):
        images = ImageProduct.objects.filter(product__id=obj.id)
        return ImageProductSerializer(images, many=True).data
