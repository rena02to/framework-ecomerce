from django.urls import path
from .views import (
    CartView,
    CartProductView,
    ProductsCartView,
    ProductCartView,
    LastProductAddCartView,
)


urlpatterns = [
    path("<int:client>/", CartView.as_view()),
    path("", CartProductView.as_view()),
    path("products_in_cart/", ProductsCartView.as_view()),
    path("products_in_cart/<int:id>/", ProductCartView.as_view()),
    path("last/", LastProductAddCartView.as_view()),
]
