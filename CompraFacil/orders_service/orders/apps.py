from django.apps import AppConfig
from pathlib import Path


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        from orders_service.utils.create_payments import setup_payment_methods

        config_file = Path(__file__).resolve().parent.parent / "payment_methods.json"
        if config_file.exists():
            import json

            with open(config_file) as f:
                active_methods = json.load(f)
            setup_payment_methods(active_methods)
