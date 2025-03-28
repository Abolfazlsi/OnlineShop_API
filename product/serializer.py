from rest_framework import serializers
from product.models import Product, Category, Color, Size, Comment, Rating, ContactUs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    color = ColorSerializer(many=True, read_only=True)
    size = SizeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "product", "time_since_creation"]
        read_only_fields = ["user", "product"]

    def get_user(self, obj):
        return obj.user.phone

    def get_product(self, obj):
        return obj.product.name


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ["user", "product"]

    def get_user(self, obj):
        return obj.user.phone

    def get_product(self, obj):
        return obj.product.name


class ContactUsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ContactUs
        fields = ['id', 'user', 'email', 'text']
        read_only_fields = ['user']

    def get_user(self, obj):
        return obj.user.phone
