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


class CategoryView(APIView):
    def post(self, request):
        try:
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return Response(
                    {"message": "Token não fornecido ou inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = call_service(
                "http://nginx_gateway:8000/api/users/me/", access_token
            )

            if not user_data or not user_data["data"].get("is_employee"):
                return Response(
                    {
                        "message": "Usuário sem permissão para criar categorias de produto"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            name = request.data.get("name")
            if not name:
                return Response(
                    {"message": "Há campos obrigatórios ausentes"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Category.objects.filter(name=name):
                return Response(
                    {"message": "Esta categoria já existe"},
                    status=status.HTTP_409_CONFLICT,
                )

            Category.objects.create(name=name)
            return Response(
                {"message": "Categoria criada com sucesso"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao criar a categoria: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CategoryDetailView(APIView):
    def get(self, request, id):
        try:
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return Response(
                    {"message": "Token não fornecido ou inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = call_service(
                "http://nginx_gateway:8000/api/users/me/", access_token
            )

            if not user_data or user_data["data"].get("is_employee"):
                return Response(
                    {
                        "message": "Usuário sem permissão para criar categorias de produto"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            category = Category.objects.get(id=id)
            serializer = CategorySerializer(category, many=False)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response(
                {"message": f"Esta categoria não existe"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar a categoria : {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, id):
        try:
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return Response(
                    {"message": "Token não fornecido ou inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = call_service(
                "http://nginx_gateway:8000/api/users/me/", access_token
            )

            if not user_data or not user_data["data"].get("is_employee"):
                return Response(
                    {
                        "message": "Usuário sem permissão para criar categorias de produto"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            category = Category.objects.filter(id=id).delete()
            return Response(
                {"message": "Categoria deletada com sucesso"}, status=status.HTTP_200_OK
            )
        except Category.DoesNotExist:
            return Response(
                {"message": f"Esta categoria não existe"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao deletar a categoria : {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductView(APIView):
    @transaction.atomic()
    def post(self, request):
        try:
            access_token = request.COOKIES.get("access_token")
            if not access_token:
                return Response(
                    {"message": "Token não fornecido ou inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user_data = call_service(
                "http://nginx_gateway:8000/api/users/me/", access_token
            )

            if not user_data or not user_data["data"].get("is_employee"):
                return Response(
                    {
                        "message": "Usuário sem permissão para criar categorias de produto"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            data = request.data.copy()
            images = request.FILES.getlist("image")[:5]
            features = request.data.getlist("feature", [])[:25]
            features = [json.loads(item) for item in features]
            data["description"] = data.get("description", "")[:1500]
            if data.get("value"):
                data["value"] = int(float(data["value"]) * 100) / 100
            serializer = ProductCreateSerializer(data=data)

            if serializer.is_valid():
                product = serializer.save()
                for image in images:
                    ImageProduct.objects.create(product=product, image=image)
                for feature in features:
                    FeatureProduct.objects.create(
                        product=product, name=feature["name"], value=feature["value"]
                    )
                return Response(
                    {"message": "Produto criado com sucesso."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "message": f"Ocorreu um erro ao cadastrar o produto: {serializer.errors}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao criar o produto: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            pass
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

    def delete(self, request, id):
        try:
            purchases = False
            # consultar o serviço orders para verificar se este produto já possui compras vinculadas
            if not purchases:
                product = Product.objects.get(id=id)
                ImageProduct.objects.filter(product__id=id).delete()
                FeatureProduct.objects.filter(product__id=id).delete()
                product.delete()
                return Response(
                    {"message": "Produto deletado com sucesso"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "message": "Já foram realizadas compras desse produto. Não é possível deletá-lo."
                },
                status=status.HTTP_409_CONFLICT,
            )
        except Product.DoesNotExist:
            return Response(
                {"message": "Este produto não existe"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao deletar o produto: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, id):
        try:
            product = Product.objects.get(id=id)
            data = request.data.copy()

            images = request.FILES.getlist("image")
            if images:
                images = images[:5]
            features = request.data.getlist("feature", [])[:25]
            if features:
                features = [json.loads(item) for item in features]
            if data.get("description"):
                data["description"] = data.get("description", "")[:1500]
            if data.get("value"):
                data["value"] = int(float(data["value"]) * 100) / 100

            serializer = ProductCreateSerializer(product, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                ImageProduct.objects.filter(product__id=id).delete()
                FeatureProduct.objects.filter(product__id=id).delete()
                for image in images:
                    ImageProduct.objects.create(product=product, image=image)
                for feature in features:
                    FeatureProduct.objects.create(
                        product=product, name=feature["name"], value=feature["value"]
                    )
                return Response(
                    {"message": "Produto editado com sucesso."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "message": f"Ocorreu um erro ao atualizar o produto: {serializer.errors}"
                }
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
