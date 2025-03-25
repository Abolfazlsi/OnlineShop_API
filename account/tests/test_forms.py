from django.test import TestCase
from account.forms import UserCreationForm, UserChangeForm
from account.models import User


class TestUserCreation(TestCase):
    def test_password_do_not_match(self):
        data = {
            "phone": "09876543212",
            "password1": "secret",
            "password2": "secret132"
        }

        form = UserCreationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("Passwords don't match", form.errors["password2"])

    def test_missing_password(self):
        data = {
            "phone": "09876543212"
        }

        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["password1"])
        self.assertIn("This field is required.", form.errors["password2"])

    def test_with_valid_data(self):
        data = {
            "phone": "09876543212",
            "password1": "secret",
            "password2": "secret"
        }

        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.phone, "09876543212")
        self.assertTrue(user.check_password("secret"))

    def test_update_existing_user_password(self):
        user = User.objects.create(phone="09876543212", password="secret")

        data = {
            "phone": "09876543212",
            "password1": "secret123",
            "password2": "secret123"
        }

        form = UserCreationForm(instance=user, data=data)
        self.assertTrue(form.is_valid())
        updated_user = form.save()

        self.assertTrue(updated_user.check_password("secret123"))


class TestUserChangeForm(TestCase):
    def test_with_valid_data(self):
        data = {
            "phone": "09876543212",
            "fullname": "John Doe",
            "password": "secret",
            "is_active": True,
            "is_admin": False
        }

        form = UserChangeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_missing_required_fields(self):
        data = {
            "phone": "",
            "fullname": "",
            "password": "secret",
            "is_active": True,
            "is_admin": False
        }
        form = UserChangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["phone"])

    def test_with_invalid_phone_number(self):
        data = {
            "phone": "invalidphone",
            "fullname": "",
            "password": "secret",
            "is_active": True,
            "is_admin": False
        }
        form = UserChangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Ensure this value has at most 11 characters (it has 12).", form.errors["phone"])

    def test_readonly_password_field(self):
        form_data = {
            'phone': '09876543212',
            'fullname': 'John Doe',
            'password': 'secret123',
            'is_active': True,
            'is_admin': False
        }
        form = UserChangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        user.set_password("secret123")
        user.save()
        self.assertNotEqual(user.password, 'newpassword')

    def test_update_user_info_and_password_not_change(self):
        user = User.objects.create(phone="09876543212", password="secret", fullname="Steve Doe", is_admin=False,
                                   is_active=True)

        data = {
            'phone': '09876545676',
            'fullname': 'John Doe',
            'password': 'secret123',
            'is_active': False,
            'is_admin': True
        }

        form = UserChangeForm(instance=user, data=data)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertFalse(updated_user.is_active)
        self.assertTrue(updated_user.is_admin)
        self.assertEqual(updated_user.fullname, "John Doe")
        self.assertEqual(updated_user.password, 'secret')



