from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import phonenumbers
from datetime import date
from .managers import UserManager


class Person(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=14)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser, Person):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(max_length=255, unique=True)
    is_client = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone", "birth_date"]
    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["email", "is_client"], name="idx_user_email_client"),
            models.Index(
                fields=["email", "is_employee"], name="idx_user_email_employee"
            ),
        ]

    def clean(self):
        super().clean()

        if self.name:
            self.name = self.name.title()
        if self.email:
            self.email = self.email.lower()

        if self.phone:
            try:
                parsed = phonenumbers.parse(self.phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValidationError("Número de telefone inválido")
                if not self.phone.startswith("+"):
                    raise ValidationError(
                        "Número deve estar no formato internacional (ex: +5511999999999)"
                    )
            except phonenumbers.NumberParseException:
                raise ValidationError("Formato de telefone inválido")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        type = (
            "Funcionário"
            if self.is_employee
            else "Cliente" if self.is_client else "Usuário"
        )
        return f"{type} #{self.id} - {self.email}"


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.PROTECT, related_name="employee_profile"
    )
    inactivation_date = models.DateTimeField(blank=True, null=True)


class ClientProfile(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.PROTECT, related_name="client_profile"
    )

    def clean(self):
        super().clean()
        if self.user.birth_date:
            today = date.today()
            age = (
                today.year
                - self.user.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.user.birth_date.month, self.user.birth_date.day)
                )
            )
            if age < 18:
                raise ValidationError(
                    {"birth_date": "Cliente deve ter pelo menos 18 anos."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
