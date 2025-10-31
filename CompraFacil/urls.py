from django.urls import path
from .views import (
    RecomendationLastPurchaseView,
    RecomendationLastAddCartView,
)

urlpatterns = [
    path("last_purchase/", RecomendationLastPurchaseView.as_view()),
    path("last_add_cart/", RecomendationLastAddCartView.as_view()),
]
