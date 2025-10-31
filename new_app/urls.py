from django.urls import path
from .views import (
    RecomendationLastAddCartView,
)

urlpatterns = [
    path("last_add_cart/", RecomendationLastAddCartView.as_view()),
]
