import random
from recommendations_service.utils.requests import call_service
from rest_framework import status
from rest_framework.response import Response


def recommend_by_last_category(self, request, last_product):
    access_token = request.COOKIES.get("access_token")
    if not access_token:
        return Response(
            {"message": "Token não fornecido ou inválido"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    product_data = call_service(
        f"http://nginx_gateway:8000/api/products/{last_product}", access_token
    )

    if product_data["status_code"] != 200:
        return Response(
            {"message": product_data.get("data").get("message")},
            status=product_data["status_code"],
        )

    category = random.choice(product_data.get("data").get("data").get("categories"))
    products = call_service(
        f"http://nginx_gateway:8000/api/products/?category={category.get("id")}",
        access_token,
    )

    if products["status_code"] != 200:
        return Response(
            {"message": products.get("data").get("message")},
            status=products["status_code"],
        )

    products_list = products.get("data", {}).get("data", [])
    sampled_products = random.sample(products_list, min(len(products_list), 25))

    return Response({"products": sampled_products}, status=status.HTTP_200_OK)
