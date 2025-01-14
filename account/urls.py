from django.urls import path, include
from account import views
from rest_framework.routers import DefaultRouter
from account.views import UserRegisterViewSet, OtpVerifyViewSet, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
app_name = 'account'

router = DefaultRouter()
router.register(r"user-register", UserRegisterViewSet, basename="user-register")
router.register(r'otp-verify', OtpVerifyViewSet, basename="otp-verify")

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]