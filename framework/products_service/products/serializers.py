from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = ["name", "description", "value", "stock", "categories"]
