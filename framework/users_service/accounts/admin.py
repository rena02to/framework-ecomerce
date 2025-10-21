from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClientProfile, EmployeeProfile

PERSON_FIELDS = ("name", "phone", "birth_date")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "birth_date",
                    "password",
                    "is_active",
                    "is_client",
                    "is_employee",
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "birth_date",
                    "password1",
                    "password2",
                    "is_client",
                    "is_employee",
                ),
            },
        ),
    )
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "birth_date",
        "is_client",
        "is_employee",
    )
    search_fields = ("email", "name", "phone")
    ordering = ("id",)
    readonly_fields = ("last_login", "date_joined")


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
    )
    search_fields = ("user__email", "user__phone")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__email", "user__phone")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)


admin.site.site_url = "SGBD - Serviço de usuários"
admin.site.index_title = "SGBD - Serviço de usuários"
admin.site.site_header = "SGBD - Serviço de usuários"
