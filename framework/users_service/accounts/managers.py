from django.contrib.auth.models import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        from .models import EmployeeProfile, User

        if not email:
            raise ValueError("O campo email é obrigatório")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_employee", True)
        extra_fields.setdefault("is_client", False)
        extra_fields.setdefault("is_active", True)

        with transaction.atomic():
            user = User(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)

            EmployeeProfile.objects.create(user=user)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
