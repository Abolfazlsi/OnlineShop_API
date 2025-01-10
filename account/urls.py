from django.urls import path, include
from account import views
from rest_framework.routers import DefaultRouter
from account.views import UserRegisterViewSet, OtpVerifyViewSet
router = DefaultRouter()
router.register(r"user-register", UserRegisterViewSet, basename="user-register")
router.register(r'otp-verify', OtpVerifyViewSet, basename="otp-verify")
app_name = 'account'
urlpatterns = [
    path('', include(router.urls)),
]