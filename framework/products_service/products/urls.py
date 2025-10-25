from django.urls import path
from .views import CategoryView, CategoryDetailView, ProductView, ProductDetailView


urlpatterns = [
    path("", ProductView.as_view()),
    path("<int:id>/", ProductDetailView.as_view()),
    path("category/", CategoryView.as_view()),
    path("category/<int:id>/", CategoryDetailView.as_view()),
]
