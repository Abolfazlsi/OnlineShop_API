from rest_framework.test import APITestCase, APIClient
from django.urls import reverse, resolve
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from account import views


class TestUrls(APITestCase):
    def test_user_profile_url_resolves_to_view(self):
        url = reverse("account:user_profile")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.UserProfileView)
