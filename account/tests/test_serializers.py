from account.serializers import UserRegisterSerializer, UserSerializer, AddressSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError, ErrorDetail
from account.models import User, Address


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


class TestAddressSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="09876543212")
        self.address = Address.objects.create(user=self.user, fullname="Steve jakson", address="what's up bro?",
                                              email="asd@gmail.com", phone="09816496571", postal_code="82643")

    def test_correct_fields(self):
        serializer = AddressSerializer(instance=self.address)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("user", data)
        self.assertIn("fullname", data)
        self.assertIn("address", data)
        self.assertIn("email", data)
        self.assertIn("phone", data)
        self.assertIn("postal_code", data)

        self.assertEqual(data["user"], self.user.phone)

    def test_read_only_field(self):
        serializer = AddressSerializer()

        self.assertTrue(serializer.fields["user"].read_only)

    def test_get_user(self):
        serializer = AddressSerializer(instance=self.address)
        user_phone = serializer.get_user(self.address)

        self.assertEqual(user_phone, self.user.phone)

    def test_with_invalid_data(self):
        data = {
            "user": "09876543212",
            "fullname": "",
            "address": "Hello World",
            "email": "asdasgmail.com",
            "phone": "22131321231",
            "postal_code": "123123"
        }

        serializer = AddressSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("fullname", serializer.errors)
        self.assertIn("email", serializer.errors)

    def test_with_valid_data(self):
        data = {
            "fullname": "asdasd",
            "address": "Hello World",
            "email": "asdas@gmail.com",
            "phone": "22131321231",
            "postal_code": "123123"
        }

        serializer = AddressSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        address = serializer.save(user=self.user)

        self.assertEqual(address.fullname, data["fullname"])
        self.assertEqual(address.address, data["address"])
        self.assertEqual(address.email, data["email"])
        self.assertEqual(address.phone, data["phone"])
        self.assertEqual(address.postal_code, data["postal_code"])
        self.assertEqual(address.user, self.user)


class TestUserSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone="09876543212")

        cls.address1 = Address.objects.create(user=cls.user, fullname="Steve jakson", address="what's up bro?",
                                              email="asd@gmail.com", phone="09816496571", postal_code="82643")

        cls.address2 = Address.objects.create(user=cls.user, fullname="Hana Moli", address="I am Atomic.",
                                              email="ghr@gmail.com", phone="09816354671", postal_code="7654")

    def test_correct_fields(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertIn("fullname", data)
        self.assertIn("email", data)
        self.assertIn("phone", data)
        self.assertIn("user", data["addresses"][0])
        self.assertIn("fullname", data["addresses"][0])
        self.assertIn("address", data["addresses"][0])
        self.assertIn("email", data["addresses"][0])
        self.assertIn("phone", data["addresses"][0])
        self.assertIn("postal_code", data["addresses"][0])

        self.assertEqual(data["fullname"], self.user.fullname)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["phone"], self.user.phone)

        self.assertEqual(len(data["addresses"]), 2)

    def test_update_main_fields(self):
        updated_data = {
            "fullname": "Abolfazl",
            "email": "asdas@gmail.com",
            "phone": "09876543213",
            "addresses": []
        }

        serializer = UserSerializer(instance=self.user, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.fullname, updated_data["fullname"])
        self.assertEqual(updated_user.email, updated_data["email"])
        self.assertEqual(updated_user.phone, updated_data["phone"])

    def test_update_addresses(self):
        new_addresses_data = [
            {
                "user": "09876543213",
                "fullname": "Alex",
                "address": "Hello World",
                "email": "asdas@gmail.com",
                "phone": "09174651324",
                "postal_code": "123123"
            },
            {
                "user": "09876543213",
                "fullname": "book",
                "address": "Hello book",
                "email": "poiuy@gmail.com",
                "phone": "09817645241",
                "postal_code": "123123"
            }
        ]

        updated_data = {
            "fullname": "Abolfazl",
            "email": "asdas@gmail.com",
            "phone": "09876543213",
            "addresses": new_addresses_data
        }

        serializer = UserSerializer(instance=self.user, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.addresses.count(), len(new_addresses_data))

        for i, address_data in enumerate(new_addresses_data):
            address = updated_user.addresses.all()[i]
            self.assertEqual(address.user.phone, address_data["user"])
            self.assertEqual(address.fullname, address_data["fullname"])
            self.assertEqual(address.address, address_data["address"])
            self.assertEqual(address.email, address_data["email"])
            self.assertEqual(address.phone, address_data["phone"])
            self.assertEqual(address.postal_code, address_data["postal_code"])

    def test_with_invalid_data(self):
        data = {
            "fullname": None,
            "email": None,
            "phone": "",
            "addresses": [
                {
                    "user": "09876543212",
                    "fullname": "mana",
                    "address": "Hello World",
                    "email": "asd@",
                    "phone": "09876543212",
                    "postal_code": "123123"
                }
            ]
        }

        serializer = UserSerializer(instance=self.user, data=data)
        self.assertFalse(serializer.is_valid())

        self.assertIn("phone", serializer.errors)
        self.assertIn("addresses", serializer.errors)
