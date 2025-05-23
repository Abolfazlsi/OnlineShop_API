from rest_framework import serializers
from account.models import User, Address
import re


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    def validate_phone(self, value):
        if not re.match(r'^\d{11,12}$', value):
            raise serializers.ValidationError("Phone number is incorrect")
        return value


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

    def update(self, instance, validated_data):

        addresses_data = validated_data.pop('addresses', None)

        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()

        if addresses_data is not None:

            instance.addresses.all().delete()

            for address_data in addresses_data:
                Address.objects.create(user=instance, **address_data)

        return instance
