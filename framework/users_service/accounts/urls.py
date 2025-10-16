from django.contrib import admin
from django.urls import path
from .views import LoginView, ClientView, LogoutView, EmployeeView


urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("client/", ClientView.as_view()),
    path("employee/", EmployeeView.as_view()),
]
