from django.db import models
from django.contrib.postgres.fields import ArrayField


class Cart(models.Model):
    user_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"Carrinho do cliente {self.user_id}"


class ProductCart(models.Model):
    cart = models.OneToOneField("Cart", on_delete=models.PROTECT)
    product_id = models.IntegerField(unique=True)
    amount = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} x {self.product_id} do cliente {self.cart.user_id}"
