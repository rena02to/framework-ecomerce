import random
from urllib import response
from orders_service.utils.payments import (
    CreditCardProccessPayment,
    DebitCardProccessPayment,
    PixProcessPayment,
    TicketProcessPayment,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, ProductOrder, Shipping, TrackingStatus, TrackingEvent
from rest_framework import status
from orders_service.utils.requests import (
    call_service,
    call_service_patch,
    call_service_update_cart,
)
from .serializers import OrderSerializer, OrderViewSerializer, PaymentMethodSerializer
from django.db import transaction
from datetime import datetime
import pytz


class OrderView(APIView):
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

            data = request.data.copy()
            user_id = user_data.get("data").get("data").get("id")
            data["user_id"] = user_id

            products_in_cart = call_service(
                f"http://nginx_gateway:8000/api/carts/products_in_cart/",
                access_token,
            )
            if products_in_cart["status_code"] != 200:
                return Response(
                    {"message": products_in_cart.get("data").get("message")},
                    status=products_in_cart["status_code"],
                )
            carts_id = products_in_cart.get("data").get("data")

            if not carts_id:
                return Response(
                    {"message": "Não há produtos no carrinho para criar o pedido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total = 0
            products_order = []
            for cart_id in carts_id:
                product_data = call_service(
                    f"http://nginx_gateway:8000/api/carts/products_in_cart/{cart_id}/",
                    access_token,
                )
                if product_data["status_code"] != 200:
                    return Response(
                        {"message": product_data.get("data").get("message")},
                        status=product_data["status_code"],
                    )

                product = call_service(
                    f"http://nginx_gateway:8000/api/products/{product_data.get("data").get("data").get("product_id")}/",
                    access_token,
                )
                if product["status_code"] != 200:
                    return Response(
                        {"message": product.get("data").get("message")},
                        status=product["status_code"],
                    )

                total += product.get("data").get("data").get(
                    "value_unformat"
                ) * product_data.get("data").get("data").get("amount")

                products_order.append(
                    {
                        "product_id": product_data.get("data")
                        .get("data")
                        .get("product_id"),
                        "value": product.get("data").get("data").get("value_unformat"),
                        "amount": product_data.get("data").get("data").get("amount"),
                    }
                )

                update = call_service_update_cart(
                    f"http://nginx_gateway:8000/api/carts/",
                    access_token,
                    {
                        "product": product_data.get("data")
                        .get("data")
                        .get("product_id"),
                        "amount": 0,
                    },
                )
                if update["status_code"] != 200:
                    return Response(
                        {"message": update.get("data").get("message")},
                        status=update["status_code"],
                    )
            data["value"] = total
            if total >= 100:
                data["delivery_value"] = 0
            elif total < 100 and total >= 50:
                data["delivery_value"] = 30
            else:
                data["delivery_value"] = 50
            serializer = OrderSerializer(data=data)
            if serializer.is_valid():
                address = user_data.get("data").get("data").get("client").get("address")
                if not address:
                    return Response(
                        {"message": "Cliente não possui endereço cadastrado"},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )
                order = serializer.save()
                if order.payment_method.name == "PIX":
                    PixProcessPayment(order)
                elif order.payment_method.name == "Cartão de Débito":
                    DebitCardProccessPayment(order)
                elif order.payment_method.name == "Cartão de Crédito":
                    CreditCardProccessPayment(order)
                elif order.payment_method.name == "Boleto Bancário":
                    TicketProcessPayment(order)
                else:
                    pass

                now = datetime.now(pytz.timezone("America/Maceio"))
                shipping = Shipping.objects.create(
                    order=order, address=address, estimated_delivery=now.date()
                )
                traking_status, _ = TrackingStatus.objects.get_or_create(
                    name="Pedido criado",
                    defaults={
                        "description": "Seu pedido foi criado e em breve estará com a transportadora"
                    },
                )
                TrackingEvent.objects.create(shipping=shipping, status=traking_status)

                for product_order in products_order:
                    ProductOrder.objects.create(
                        order=order,
                        product_id=product_order.get("product_id"),
                        value=product_order.get("value"),
                        amount=product_order.get("amount"),
                    )
                    update_stock = call_service_patch(
                        f"http://nginx_gateway:8000/api/products/{product_order.get("product_id")}",
                        access_token,
                        {
                            "quantity_sold": product_order.get("amount"),
                        },
                    )
                    if update_stock["status_code"] != 200:
                        return Response(
                            {"message": update_stock.get("data").get("message")},
                            status=update_stock["status_code"],
                        )

                return Response(
                    {
                        "message": "Pedido criado com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"message": f"Ocorreu um erro ao criar o pedido: {serializer.errors}"}
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao tentar criar pedido: {e}"},
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
            orders = Order.objects.filter(user_id=user_id).order_by("id")
            serializer = OrderViewSerializer(orders, many=True).data
            for data in serializer:
                products = data.get("products")
                for product in products:
                    id = product.get("product_id")
                    returned = call_service(
                        f"http://nginx_gateway:8000/api/products/{id}/",
                        access_token,
                    )
                    if returned["status_code"] != 200:
                        return Response(
                            {"message": returned.get("data").get("message")},
                            status=returned["status_code"],
                        )
                    product["name"] = returned.get("data").get("data").get("name")
                    images = returned.get("data").get("data").get("images", [])
                    product["image"] = images[0].get("image")
            return Response({"data": serializer})
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os pedidos: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderDetailView(APIView):
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

            orders = Order.objects.filter(id=id)
            serializer = OrderViewSerializer(orders, many=False).data
            products = serializer.get("products")
            for product in products:
                id = product.get("product_id")
                returned = call_service(
                    f"http://nginx_gateway:8000/api/products/{id}/",
                    access_token,
                )
                if returned["status_code"] != 200:
                    return Response(
                        {"message": returned.get("data").get("message")},
                        status=returned["status_code"],
                    )
                product["name"] = returned.get("data").get("data").get("name")
                images = returned.get("data").get("data").get("images", [])
                product["image"] = images[0].get("image")
            return Response({"data": serializer})
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar o pedido: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LastOrderView(APIView):
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
            order = Order.objects.filter(user_id=user_id).order_by("id").last()
            if order:
                product = (
                    ProductOrder.objects.filter(order__id=order.id)
                    .order_by("id")
                    .last()
                )
            if product:
                product = product.product_id
            if not product or not order:
                product = None
            return Response({"data": product})
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar o último pedido: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
