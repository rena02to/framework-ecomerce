from django.urls import path
from .views import OrderView, OrderDetailView, LastOrderView


urlpatterns = [
    path("", OrderView.as_view()),
    path("<int:id>/", OrderDetailView.as_view()),
    path("last/", LastOrderView.as_view()),
]
