from django.core.validators import MaxLengthValidator
from django.db import models
import uuid


def image_product_upload_to(instance, filename):
    product = instance.product.code if instance.product else "unknown"
    return f"products/{product}/{filename}"


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(validators=[MaxLengthValidator(500)])
    value = models.DecimalField(max_digits=15, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField("Category")
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        while not self.code or Product.objects.filter(code=self.code).exists():
            self.code = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ImageProduct(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.PROTECT, related_name="photo_product"
    )
    image = models.ImageField(upload_to=image_product_upload_to)
    main = models.BooleanField(default=True)


class FeatureProduct(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.PROTECT, related_name="feature_product"
    )
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
