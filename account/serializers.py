from rest_framework import serializers
from .models import User, Otp, Address


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user"]

    def get_user(self, obj):
        return obj.user.phone


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "phone", "addresses"]
