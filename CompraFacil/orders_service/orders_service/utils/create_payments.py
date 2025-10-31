from orders.models import PaymentMethod

DEFAULT_PAYMENT_METHODS = [
    {"name": "Pix"},
    {"name": "Boleto"},
    {"name": "Cartão de Crédito"},
    {"name": "Cartão de Débito"},
]


def setup_payment_methods(active_methods: dict):
    """
    active_methods: dict como {"Pix": True, "Boleto": False, ...}
    """
    for method in DEFAULT_PAYMENT_METHODS:
        name = method["name"]
        PaymentMethod.objects.update_or_create(
            name=name,
            defaults={
                "description": method["description"],
                "active": active_methods.get(name, True),
            },
        )
