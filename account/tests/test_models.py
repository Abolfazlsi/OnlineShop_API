from django.test import TestCase
from account.models import User, UserManager, Otp


class TestUserModel(TestCase):
    def test_create_user(self):
        user = User.objects.create(phone="09876543212", fullname="John Doe")
        self.assertEqual(user.phone, "09876543212")
        self.assertEqual(user.fullname, "John Doe")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)

    def test_str_method(self):
        user = User.objects.create(phone="09876543212")
        self.assertEqual(str(user), "09876543212")

    def test_is_staff_property(self):
        user = User.objects.create(phone="09876543212", is_admin=True)
        self.assertTrue(user.is_staff)

    def test_unique_phone(self):
        User.objects.create(phone="09876543213")
        with self.assertRaises(Exception):
            User.objects.create(phone="09876543213")


class TestUserManager(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(phone="09876543212", password="secret")
        self.assertEqual(user.phone, "09876543212")
        self.assertTrue(user.check_password("secret"))
        self.assertFalse(user.is_admin)

    def test_create_user_without_phone(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phone=None, password="secret")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(phone="09876543212", password="secret")
        self.assertEqual(admin.phone, "09876543212")
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)


class TestOtpModel(TestCase):
    def test_unique_otp(self):
        Otp.objects.create(token="ebb05731-9c74-4790-8946-514e5f71e434", phone="09876543212", code=1234)
        with self.assertRaises(Exception):
            Otp.objects.create(token="ebb05731-9c7p-4790-8946-514e5f71e4g4", phone="09876543212", code=8765)

