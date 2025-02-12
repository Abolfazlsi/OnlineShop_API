from rest_framework import serializers

from cart.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "total", "is_paid", "full_name", "address", "phone_number", "postal_code", "created_at",
                  "orderitems"]


class CartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    color = serializers.CharField(required=False, default='empty')
    size = serializers.CharField(required=False, default='empty')
