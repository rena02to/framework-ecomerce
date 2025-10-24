from django.urls import path
from .views import CategoryView, CategoryDetailView, ProductView


urlpatterns = [
    path("", ProductView.as_view()),
    path("category/", CategoryView.as_view()),
    path("category/<int:id>/", CategoryDetailView.as_view()),
]
