from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .simple import recommend_by_category
from recommendations_service.utils.requests import call_service
import random


class RecomendationLastPurchaseView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access_token")
        last_product = None
        if access_token:
            last_product_data = call_service(
                "http://nginx_gateway:8000/api/orders/last/", access_token
            )
            if last_product_data["status_code"] == 200:
                last_product = last_product_data.get("data").get("data")
        if not access_token or not last_product:
            avaliable_products = call_service(
                "http://nginx_gateway:8000/api/products/avaliable_products/", None
            )
            if avaliable_products["status_code"] == 200:
                last_product = random.choice(avaliable_products.get("data").get("data"))
        return recommend_by_category(self, request, last_product)


class RecomendationLastAddCartView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access_token")
        last_product = None
        if access_token:
            last_product_data = call_service(
                "http://nginx_gateway:8000/api/carts/last/", access_token
            )
            if last_product_data["status_code"] == 200:
                last_product = last_product_data.get("data").get("data")
        if not access_token or not last_product:
            avaliable_products = call_service(
                "http://nginx_gateway:8000/api/products/avaliable_products/", None
            )
            if avaliable_products["status_code"] == 200:
                last_product = random.choice(avaliable_products.get("data").get("data"))
        return recommend_by_category(self, request, last_product)
