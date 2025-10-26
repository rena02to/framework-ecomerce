from curses.ascii import isdigit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, ProductCart
from carts_service.utils.requests import call_service, call_service_product
from django.conf import settings


class CartView(APIView):
    def post(self, request, client):
        try:
            token = request.headers.get("X-Service-Token")
            if token != settings.INTERNAL_SERVICE_TOKEN:
                return Response(
                    {"message": "Você não tem permissão para esta ação!"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            cart = Cart.objects.get_or_create(user_id=client)
            return Response(
                {"message": "Carrinho criado com sucesso."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao criar o carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CartProductView(APIView):
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

            if not user_data or not user_data["data"].get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data["data"].get("id")
            product = request.data.get("product")
            amount = request.data.get("amount")
            if amount and not str(amount).isdigit():
                amount = None
            if not product:
                return Response(
                    {"message": "Há campos obrigatórios ausentes"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_data = call_service_product(
                f"http://nginx_gateway:8000/api/products/{product}/", access_token
            )

            if not product_data:
                return Response(
                    {"message": "Ocorreu um erro ao buscar o produto"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not product_data["data"]:
                return Response(
                    {"message": "Este produto não existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            cart = Cart.objects.get(user_id=user_id)
            product_instance = ProductCart.objects.filter(product_id=product)
            if not product_instance:
                ProductCart.objects.create(
                    cart=cart, product_id=product, amount=amount if amount else 1
                )
            else:
                product = product_instance.first()
                product.amount = product.amount + (int(amount) if amount else 1)
                product.save()

            return Response(
                {"message": "Produto adicionado ao carrinho."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao adicionar o produto ao carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
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

            if not user_data or not user_data["data"].get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data["data"].get("id")
            cart = Cart.objects.get(user_id=user_id).id
            products = ProductCart.objects.filter(cart__id=cart).order_by("updated_at")
            data = []
            for product in products:
                return_product = call_service(
                    f"http://nginx_gateway:8000/api/products/{product.product_id}/",
                    access_token,
                )
                if not return_product:
                    return Response(
                        {
                            "message": "Ocorreu um erro ao buscar os produtos no carrinho."
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                data["data"].append(return_product)

            return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos no carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
