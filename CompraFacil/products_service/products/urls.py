from django.urls import path
from .views import ProductView, ProductDetailView, AvaliableProductsView


urlpatterns = [
    path("", ProductView.as_view()),
    path("<int:id>/", ProductDetailView.as_view()),
    path("avaliable_products/", AvaliableProductsView.as_view()),
]
