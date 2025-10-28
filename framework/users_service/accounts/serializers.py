from rest_framework import serializers
from .models import User, ClientProfile, EmployeeProfile


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ["inactivation_date"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile()
        fields = ["address"]


class MeSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "birth_date",
            "is_client",
            "is_employee",
            "client",
            "employee",
        ]

    def get_client(self, obj):
        if hasattr(obj, "client_profile"):
            return ClientSerializer(obj.client_profile).data
        return None

    def get_employee(self, obj):
        if hasattr(obj, "employee_profile"):
            return EmployeeSerializer(obj.employee_profile).data
        return None
