import random
from recommendations_service.utils.requests import call_service
from rest_framework import status
from rest_framework.response import Response


def recommend_by_category(self, request, product):
    product_data = call_service(
        f"http://nginx_gateway:8000/api/products/{product}", None
    )

    if product_data["status_code"] != 200:
        return Response(
            {"message": product_data.get("data").get("message")},
            status=product_data["status_code"],
        )

    categories = product_data.get("data").get("data").get("categories", None)
    if categories:
        category = random.choice(categories).get("id")
    else:
        category = None
    products = call_service(
        f"http://nginx_gateway:8000/api/products/?category={category if category else ''}",
        None,
    )

    if products["status_code"] != 200:
        return Response(
            {"message": products.get("data").get("message")},
            status=products["status_code"],
        )

    products_list = products.get("data", {}).get("data", [])
    sampled_products = random.sample(products_list, min(len(products_list), 25))

    return Response({"products": sampled_products}, status=status.HTTP_200_OK)
