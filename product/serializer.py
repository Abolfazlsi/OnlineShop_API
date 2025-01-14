from rest_framework import serializers
from product.models import Product, Category, Color, Size

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
        fields = '__all__'
