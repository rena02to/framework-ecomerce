from django.db import models


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.IntegerField()
    payment_methods = models.ManyToManyField("PaymentMethod")
    value = models.DecimalField(max_digits=30, decimal_places=2)

    def __str__(self):
        return f"Compra do usuário #{self.user_id} (id: {self.id})"


class ProductOrder(models.Model):
    order = models.OneToOneField(
        "Order", related_name="product_order", on_delete=models.PROTECT
    )
    product_id = models.IntegerField()
    value = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.IntegerField()

    def __str__(self):
        return f"#{self.id} - Produto #{self.product_id} da compra {self.order.id}"
