from rest_framework import serializers
from .models import User, Otp

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    def validate(self, attrs):
        if User.objects.filter(phone=attrs['phone']).exists():
            return attrs
