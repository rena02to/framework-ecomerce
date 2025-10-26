from django.db import models
import uuid


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

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


class Shipping(models.Model):
    order = models.ForeignKey(
        "Order", related_name="order_shipping", on_delete=models.PROTECT
    )
    address = models.CharField(max_length=255)
    description = models.CharField(max_length=50)
    estimated_delivery = models.DateField()
    delivered = models.BooleanField(default=False)
    receiver = models.CharField(max_length=150, blank=True, null=True)
    traking_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        while (
            not self.traking_code
            or Shipping.objects.filter(traking_code=self.traking_code).exists()
        ):
            self.traking_code = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Peido #{self.id}"


class TrackingStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TrakingEvent(models.Model):
    shipping = models.ForeignKey(
        "Shipping", related_name="shipping_traking", on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        "TrakingStatus", related_name="location_status", on_delete=models.PROTECT
    )
    timestamp = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return f"Atualização #{self.id} ({self.location.name}) do pedido #{self.shipping.id}"
