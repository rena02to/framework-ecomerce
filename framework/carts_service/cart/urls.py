from django.urls import path
from .views import CartView, CartProductView


urlpatterns = [
    path("<int:client>/", CartView.as_view()),
    path("", CartProductView.as_view()),
]
