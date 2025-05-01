from django.db import models
from account.models import User
from product.models import Product
from django.core.validators import  MinValueValidator, MaxValueValidator

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    postal_code = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return self.user.phone

    class Meta:
        ordering = ("-created_at",)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderitems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orderitems")
    quantity = models.IntegerField()
    size = models.CharField(max_length=10, null=True)
    color = models.CharField(max_length=15, null=True)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.product}"


class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(90)])
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.code


class UsedDiscountCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UsedDiscountCodes")
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.CASCADE, related_name="UsedDiscountCodes")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="UsedDiscountCodes")

    def __str__(self):
        return self.user.phone
