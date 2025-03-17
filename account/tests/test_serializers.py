from account.serializers import UserRegisterSerializer, UserSerializer, AddressSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError, ErrorDetail


class TestUserRegisterSerializer(TestCase):
    def test_with_invalid_data(self):
        data = {
            "phone": "0933213"
        }

        data2 = {
            "phone": "093327293409823413"
        }

        serializer = UserRegisterSerializer(data=data)
        serializer2 = UserRegisterSerializer(data=data2)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)
        expected_error = [ErrorDetail(string="Phone number is incorrect", code="invalid")]
        self.assertEqual(serializer.errors["phone"], expected_error)

        self.assertFalse(serializer2.is_valid())
        expected_error2 = [ErrorDetail(string='Ensure this field has no more than 11 characters.', code='max_length')]
        self.assertEqual(serializer2.errors["phone"], expected_error2)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_without_data(self):
        data = {}
        serializer = UserRegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)
        self.assertIn("This field is required.", serializer.errors["phone"])

    def test_with_valid_data(self):
        data = {
            "phone": "09876543212"
        }
        serializer = UserRegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertIn("phone", serializer.data)
        self.assertIn("09876543212", serializer.data["phone"])
