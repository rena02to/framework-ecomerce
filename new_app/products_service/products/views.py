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
from .serializers import CategorySerializer, ProductSerializer, ProductUpdateSerializer
from django.db.models import Q


class ProductView(APIView):
    def get(self, request):
        try:
            category = request.GET.get("category", None)
            query = request.GET.get("query", None)
            filters = Q()
            if category:
                filters &= Q(categories__id=category)
            if query:

                filters &= Q(categories__value__icontains=query)

                filters &= Q(name__icontains=query)
            products = Product.objects.filter(filters, stock__gte=1)
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

    def patch(self, request, id):
        try:
            product = Product.objects.get(id=id)
            data = request.data.copy()
            if request.data.get("quantity_sold", None):
                data["stock"] = product.stock - int(
                    request.data.get("quantity_sold", 0)
                )
            serializer = ProductUpdateSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Produto atualizado com sucesso"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "message": f"Ocorreu um erro ao atualizar o produto: {serializer.errors}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist:
            return Response(
                {"message": "Este produto não existe"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao atualizar o produto: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AvaliableProductsView(APIView):
    def get(self, request):
        try:
            products = Product.objects.filter(stock__gte=1).values_list("id", flat=True)
            return Response({"data": products}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos disponíveis: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
