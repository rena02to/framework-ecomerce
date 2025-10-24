from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import ClientProfile, EmployeeProfile
import pytz
from .serializers import MeSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token
            now = datetime.now(pytz.timezone("America/Sao_Paulo"))
            expiration_access = now + timedelta(hours=8)
            expiration_refresh = now + timedelta(days=7)
            response = Response(
                {"message": "Usuário autenticado com sucesso!"},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="access_token",
                value=str(access_token),
                expires=expiration_access,
                samesite="None",
                path="/",
                secure=True,
                httponly=True,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh_token),
                expires=expiration_refresh,
                samesite="None",
                path="/",
                secure=True,
                httponly=True,
            )
            return response
        return Response(
            {"message": "E-mail ou senha incorretos."}, status=status.HTTP_404_NOT_FOUND
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

        response = Response(
            {"message": "Logout realizado com sucesso"}, status=status.HTTP_200_OK
        )
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        return response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        pass


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = MeSerializer(request.user)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao buscar os dados do usuário: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                email = request.data.get("email")
                name = request.data.get("name")
                phone = request.data.get("phone")
                birth_date = request.data.get("birth_date")
                password = request.data.get("password")

                if not email or not name or not phone or not birth_date or not password:
                    return Response(
                        {"message": "Campos obrigatórios faltando."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user, _ = User.objects.get_or_create(
                    email=email,
                )
                if hasattr(user, "client_profile"):
                    user.is_client = True
                    user.save()
                    return Response(
                        {"message": "Já existe uma conta com este e-mail!"},
                        status=status.HTTP_409_CONFLICT,
                    )

                user.name = name
                user.phone = phone
                user.birth_date = birth_date
                user.is_client = True
                user.set_password(password)

                user.full_clean()
                user.save()
                client, _ = ClientProfile.objects.get_or_create(user=user)

                return Response(
                    {
                        "message": "Cliente criado com sucesso",
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"message": "Você não tem permissão para esta ação."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao tentar criar cliente: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            if hasattr(request.user, "employee_profile"):
                email = request.data.get("email")
                name = request.data.get("name")
                phone = request.data.get("phone")
                birth_date = request.data.get("birth_date")

                if not email or not name or not phone or not birth_date:
                    return Response(
                        {"message": "Campos obrigatórios faltando."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user, _ = User.objects.get_or_create(
                    email=email,
                )
                if hasattr(user, "employee_profile"):
                    user.is_employee = True
                    user.save()
                    return Response(
                        {"message": "Já existe uma conta com este e-mail!"},
                        status=status.HTTP_409_CONFLICT,
                    )
                user.name = name
                user.phone = phone
                user.birth_date = birth_date
                user.is_employee = True
                if user.has_usable_password():
                    pass

                user.full_clean()
                user.save()
                employee, _ = EmployeeProfile.objects.update_or_create(
                    user=user,
                )

                return Response(
                    {
                        "message": "Funcionário criado com sucesso",
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"message": "Você não tem permissão para esta ação."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            return Response(
                {"message": f"Ocorreu um erro ao tentar criar cliente: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
