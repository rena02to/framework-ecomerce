from django.urls import path
from .views import LoginView, ClientView, LogoutView, EmployeeView, UserMeView


urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("client/", ClientView.as_view()),
    path("employee/", EmployeeView.as_view()),
    path("me/", UserMeView.as_view()),
]
