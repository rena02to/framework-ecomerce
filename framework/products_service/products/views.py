from functools import partial
from itertools import product
from os import access
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from products_service.utils.requests import call_service
from .models import Category, ImageProduct, FeatureProduct, Product
from .serializers import CategorySerializer, ProductCreateSerializer, ProductSerializer
import json


class ProductView(APIView):
    def get(self, request):
        try:
            products = Product.objects.filter(stock__gte=1)
            serializer = ProductSerializer(products, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductDetailView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product, many=False)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"message": "Este produto não existe"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar o produto: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
