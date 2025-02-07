from django.contrib import admin
from cart.models import DiscountCode, Order, OrderItem, UsedDiscountCode


class OrderItemAdmin(admin.StackedInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "total", "is_paid")
    inlines = (OrderItemAdmin,)
    filter = ("is_paid",)


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount", "quantity")


@admin.register(UsedDiscountCode)
class UsedDiscountCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "discount_code", "order")
