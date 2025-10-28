from django.urls import path
from .views import OrderView, OrderDetailView


urlpatterns = [
    path("", OrderView.as_view()),
    path("<int:id>", OrderDetailView.as_view()),
]
