from rest_framework.test import APITestCase, APISimpleTestCase
from django.urls import reverse, resolve
from account.models import User, Address
from rest_framework_simplejwt.tokens import RefreshToken
from account import views


class TestUrls(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone="09716498162")
        cls.url = reverse("account:logout")
        cls.refresh = RefreshToken.for_user(cls.user)
        cls.access = str(cls.refresh.access_token)

        Address.objects.create(user=cls.user, fullname="Steve", phone="09716498162", address="Hello",
                               email="aasd@gmail.com", postal_code="123121212")

    def test_user_profile_url_correct_view(self):
        url = reverse("account:user-register-list")
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, views.UserRegisterViewSet)
        self.assertIn("post", resolver.func.actions)

    def test_otp_verify_url_resolves_correct_view(self):
        url = reverse("account:otp-verify-list")
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, views.OtpVerifyViewSet)
        self.assertIn("post", resolver.func.actions)

    def test_logout_url_resolves_correct_view(self):
        url = reverse("account:logout")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.LogoutView)
        self.assertIn("post", resolver.func.view_class.http_method_names)

    def test_user_profile_url_resolves_correct_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        url = reverse("account:user_profile")
        resolver = resolve(url)

        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(resolver.func.view_class, views.UserProfileView)
        self.assertTrue(hasattr(views.UserProfileView, 'patch'))
        self.assertTrue(hasattr(views.UserProfileView, 'get'))

    def test_addresses_list_url_resolves_correct_view(self):
        url = reverse("account:address_list")
        resolver = resolve(url)

        self.assertEqual(resolver.func.view_class, views.AddressListView)
        self.assertTrue(hasattr(views.AddressListView, 'get'))

    def test_add_address_url_resolves_correct_view(self):
        url = reverse("account:add_address")
        resolver = resolve(url)

        self.assertEqual(resolver.func.view_class, views.AddAddressAPIView)
        self.assertTrue(hasattr(views.AddAddressAPIView, 'post'))

    def test_edit_address_url_resolves_correct_view(self):
        url = reverse("account:edit_address", args=[1])
        resolver = resolve(url)

        self.assertEqual(resolver.func.view_class, views.EditAddressView)
        self.assertTrue(hasattr(views.EditAddressView, 'patch'))
        self.assertTrue(hasattr(views.EditAddressView, 'put'))

    def test_delete_address_url_resolves_correct_view(self):
        url = reverse("account:delete_address", args=[1])
        resolver = resolve(url)

        self.assertEqual(resolver.func.view_class, views.DeleteAddressView)
        self.assertTrue(hasattr(views.DeleteAddressView, 'delete'))
