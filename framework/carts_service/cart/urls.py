from django.urls import path
from .views import CartView, CartProductView, ProductCartView


urlpatterns = [
    path("<int:client>/", CartView.as_view()),
    path("", CartProductView.as_view()),
    path("products_in_cart/<int:id>/", ProductCartView.as_view()),
]
