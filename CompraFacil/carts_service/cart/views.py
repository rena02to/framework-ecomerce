from curses.ascii import isdigit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, ProductCart
from carts_service.utils.requests import call_service, call_service_product
from django.conf import settings
from .serializers import ProductCartSerializer
from babel.numbers import format_currency


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

            if user_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=user_data["status_code"],
                )
            if not user_data.get("data").get("data").get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data.get("data").get("data").get("id")
            product = request.data.get("product")
            amount = request.data.get("amount")

            try:
                amount = int(amount)
            except (TypeError, ValueError):
                amount = 1

            if not product:
                return Response(
                    {"message": "Há campos obrigatórios ausentes"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_data = call_service_product(
                f"http://nginx_gateway:8000/api/products/{product}/", access_token
            )

            if product_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=product_data["status_code"],
                )

            cart = Cart.objects.get(user_id=user_id)
            product_instance = ProductCart.objects.filter(product_id=product)
            if not product_instance:
                if amount > 0 or not amount:
                    ProductCart.objects.create(
                        cart=cart, product_id=product, amount=amount
                    )
            else:
                product = product_instance.first()
                if product.amount + amount > 0 and amount > 0:
                    product.amount = product.amount + amount
                    product.save()
                else:
                    product.delete()

            return Response(
                {"message": "Carrinho atualizado."},
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

            if user_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=user_data["status_code"],
                )
            if not user_data.get("data").get("data").get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data.get("data").get("data").get("id")
            cart = Cart.objects.get(user_id=user_id).id
            products = ProductCart.objects.filter(cart__id=cart).order_by("-updated_at")
            data = []
            total = 0
            for product in products:
                return_product = call_service(
                    f"http://nginx_gateway:8000/api/products/{product.product_id}/",
                    access_token,
                )
                if return_product["status_code"] != 200:
                    return Response(
                        {"message": user_data.get("data").get("message")},
                        status=return_product["status_code"],
                    )
                data.append(
                    {
                        "product": return_product.get("data").get("data"),
                        "amount": product.amount,
                    }
                )
                total += (
                    return_product.get("data").get("data").get("value_unformat")
                    * product.amount
                )

            return Response(
                {"data": data, "total": format_currency(total, "BRL", locale="pt_BR")},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos no carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductCartView(APIView):
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

            if user_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=user_data["status_code"],
                )
            if not user_data.get("data").get("data").get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data.get("data").get("data").get("id")
            product = ProductCart.objects.get(id=id, cart__user_id=user_id)
            if not product:
                return Response(
                    {"message": "Produto não encontrado no carrinho."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = ProductCartSerializer(product, many=False)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos no carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductsCartView(APIView):
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

            if user_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=user_data["status_code"],
                )
            if not user_data.get("data").get("data").get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data.get("data").get("data").get("id")
            cart = Cart.objects.get(user_id=user_id).id
            products = ProductCart.objects.filter(cart__id=cart).values_list(
                "id", flat=True
            )
            return Response({"data": products}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os produtos no carrinho: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LastProductAddCartView(APIView):
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

            if user_data["status_code"] != 200:
                return Response(
                    {"message": user_data.get("data").get("message")},
                    status=user_data["status_code"],
                )
            if not user_data.get("data").get("data").get("is_client"):
                return Response(
                    {"message": "Você não possui uma conta de cliente. Cadastre-se."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user_id = user_data.get("data").get("data").get("id")
            cart = Cart.objects.get(user_id=user_id).id
            product = ProductCart.objects.filter(cart__id=cart).order_by("-id").first()
            if product:
                product = product.id
            else:
                product = None
            return Response({"data": product}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "message": f"Ocorreu um erro ao buscar o último produto no carrinho: {e}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
