from django.urls import path
from .views import RecomendationsView


urlpatterns = [
    path("", RecomendationsView.as_view()),
]
