from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from account.models import User, Otp, Address
from rest_framework_simplejwt.tokens import RefreshToken
from threading import Thread
from rest_framework_simplejwt.tokens import BlacklistedToken


class TestUserRegisterView(APITestCase):
    def test_user_register_view_valid_data(self):
        data = {
            "phone": "09715460912",
        }
        response = self.client.post("/account/user-register/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)

    def test_user_register_view_invalid_data(self):
        data = {
            "phone": "0971546012",
        }

        data2 = {
            "phone": "09712342344546012",
        }
        response = self.client.post("/account/user-register/", data, format="json")
        response2 = self.client.post("/account/user-register/", data2, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Phone number is incorrect", response.data["phone"])
        self.assertIn("Ensure this field has no more than 11 characters.", response2.data["phone"])

    def test_user_register_view_without_data(self):
        data = {}
        response = self.client.post("/account/user-register/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_otp_creation(self):
        url = "/account/user-register/"
        data = {
            "phone": "09651239871",
        }

        response = self.client.post(url, data, format="json")
        otp = Otp.objects.filter(phone=data["phone"]).first()
        self.assertTrue(1000 <= otp.code <= 9999)
        self.assertIn("token", response.data)


class TestOtpVerifyView(APITestCase):
    @classmethod
    def setUpTestData(self):
        Otp.objects.create(token="ebb05731-9c74-4790-8946-514e5f71e434", phone="09123456783", code=5464)
        self.url = "/account/otp-verify/"

    def test_create_user_with_valid_data(self):
        data = {
            "token": "ebb05731-9c74-4790-8946-514e5f71e434",
            "code": 5464
        }

        response = self.client.post(self.url, data, format="json")
        user = User.objects.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertIn("User logged in successfully", response.data["message"])
        self.assertEqual(user, 1)
        self.assertEqual(User.objects.first().phone, "09123456783")
        self.assertEqual(Otp.objects.all().count(), 0)

    def test_create_user_with_invalid_data(self):
        data = {
            "token": "ebb05731-9c74-4790-8946-514e5f71f76",
            "code": 1360
        }

        response = self.client.post(self.url, data, format="json")
        user = User.objects.all().count()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid token or code", (response.data["Error"]))
        self.assertEqual(user, 0)
        self.assertEqual(Otp.objects.all().count(), 1)

    def test_create_user_with_without_data(self):
        data = {}

        response = self.client.post(self.url, data, format="json")
        user = User.objects.all().count()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid token or code", (response.data["Error"]))
        self.assertEqual(user, 0)
        self.assertEqual(Otp.objects.all().count(), 1)


class TestLogoutView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(phone="09716498162")
        self.url = reverse("account:logout")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_user_logout_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        data = {
            "refresh": str(self.refresh)
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(BlacklistedToken.objects.all().count(), 1)

    def test_user_logout_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        data = {
            "refresh": str(self.refresh) + "Hello"
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BlacklistedToken.objects.all().count(), 0)
        self.assertIn("Refresh token is invalid", response.data["detail"])

    def test_user_logout_without_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        data = {}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BlacklistedToken.objects.all().count(), 0)
        self.assertIn("Refresh token is required", response.data["message"])

    def test_user_logout_anon_user(self):
        data = {
            "refresh": str(self.refresh) + "Hello"
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(BlacklistedToken.objects.all().count(), 0)
        self.assertIn("Authentication credentials were not provided.", response.data["detail"])


class TestUserProfileViews(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="0971645190")
        self.url = reverse('account:user_profile')

    def test_user_profile_view_anon_user_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_user_profile_view_auth_user_GET(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        expected_data = {
            "fullname": None,
            "email": None,
            "phone": "0971645190",
            "addresses": []
        }

        self.assertEqual(response.data, expected_data)

    def test_update_user_profile_view_valid_data_PUT(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        data = {
            "fullname": "Steve",
            "email": "asd@gmail.com",
            "phone": "0971645190",
            "addresses": [
                {
                    "id": 1,
                    "user": "09657481984",
                    "fullname": "Abol",
                    "address": "asdadasdasdasdasddddddd",
                    "email": "qeweqwqeqewws@gmail.com",
                    "phone": "22131321231",
                    "postal_code": "123121212"
                }
            ]
        }

        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["fullname"], "Steve")

    def test_update_user_profile_view_invalid_data_PUT(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        data = {
            "fullname": "Steve",
            "email": "asd@gmail.com",
            "addresses": [
                {
                    "id": 1,
                    "user": "09657481984",
                    "fullname": "Abol",
                    "address": "asdadasdasdasdasddddddd",
                    "email": "qeweqwqeqewws@gmail.com",
                    "phone": "22131321231",
                    "postal_code": "123121212"
                }
            ]
        }

        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)


class TestAddressListView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(phone="09716498162")
        self.url = reverse("account:address_list")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.address = Address.objects.create(user=self.user, fullname="Steve", phone="09716498162", address="Hello",
                                              email="aasd@gmail.com", postal_code="123121212")

    def test_address_list_view_anon_user_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication credentials were not provided.", response.data["detail"])

    def test_address_list_view_auth_user_GET(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.get(self.url)

        expected_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "user": self.user.phone,
                    "fullname": "Steve",
                    "address": "Hello",
                    "email": "aasd@gmail.com",
                    "phone": "09716498162",
                    "postal_code": "123121212"
                },
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)


class TestAddAddressAPIView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(phone="09716498162")
        self.url = reverse("account:add_address")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_add_address_view_anon_user_and_valid_data(self):
        data = {
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication credentials were not provided.", response.data["detail"])
        self.assertEqual(Address.objects.all().count(), 0)

    def test_add_address_view_auth_user_and_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        data = {
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["fullname"], "Steve Hamber")
        self.assertEqual(Address.objects.all().count(), 1)

    def test_add_address_view_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        data = {
            "fullname": ["Hello"],
            "address": 123,
            "email": "qwe$gmail.com",
            "phone": "0951648",
            "postal_code": "123465123"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Address.objects.all().count(), 0)


class TestEditAddressView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="09716498162")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.address = Address.objects.create(user=self.user, fullname="Steve", phone="09716498162", address="Hello",
                                              email="aasd@gmail.com", postal_code="123121212")

        self.url = reverse("account:edit_address", args=[1])

    def test_edit_address_view_anon_user(self):
        data = {
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertTrue(data["fullname"] != Address.objects.first().fullname)

    def test_edit_address_view_auth_user_and_valid_data_and_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        data = {
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.put(self.url, data, format="json")

        expected_data = {
            "id": 1,
            "user": "09716498162",
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_data)

    def test_edit_address_view_auth_user_and_is_not_owner(self):
        other_user = User.objects.create_user(phone="09716498869")
        other_refresh = RefreshToken.for_user(other_user)
        other_access = str(other_refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_access}")

        data = {
            "fullname": "Steve Hamber",
            "address": "what's up bro?",
            "email": "qwe@gmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("You do not have permission to perform this action.", response.data["detail"])
        self.assertEqual(self.address.fullname, "Steve")

    def test_edit_address_view_auth_user_and_invalid_data_and_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        data = {
            "fullname": ["Steve Hamber"],
            "address": "what's up bro?",
            "email": "qwegmail.com",
            "phone": "09516481846",
            "postal_code": "123465123"
        }
        response = self.client.put(self.url, data, format="json")

        expected_data = {
            "fullname": [
                "Not a valid string."
            ],
            "email": [
                "Enter a valid email address."
            ]
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_data)
        self.assertEqual(self.address.fullname, "Steve")


class TestDeleteAddressView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(phone="09716498162")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.address = Address.objects.create(user=self.user, fullname="Steve", phone="09716498162", address="Hello",
                                              email="aasd@gmail.com", postal_code="123121212")

        self.url = reverse("account:delete_address", args=[1])

    def test_delete_address_view_anon_user(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication credentials were not provided.", response.data["detail"])
        self.assertEqual(Address.objects.all().count(), 1)
        self.assertEqual(Address.objects.first().fullname, "Steve")

    def test_delete_address_view_auth_user_and_is_not_owner(self):
        other_user = User.objects.create_user(phone="09716498869")
        other_refresh = RefreshToken.for_user(other_user)
        other_access = str(other_refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_access}")

        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("You do not have permission to perform this action.", response.data["detail"])
        self.assertEqual(Address.objects.all().count(), 1)
        self.assertEqual(Address.objects.first().fullname, "Steve")

    def test_delete_address_view_auth_user_and_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Address.objects.all().count(), 0)
