from django.urls import path
from .views import ProductView, ProductDetailView


urlpatterns = [
    path("", ProductView.as_view()),
    path("<int:id>/", ProductDetailView.as_view()),
]
