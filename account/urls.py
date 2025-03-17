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

# user register and login
router.register(r"user-register", UserRegisterViewSet, basename="user-register")
router.register(r'otp-verify', OtpVerifyViewSet, basename="otp-verify")

urlpatterns = [
    path('', include(router.urls)),

    # refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # user's profile
    path('user-profile/', views.UserProfileView.as_view(), name='user_profile'),

    # address's url
    path('addresses-list/', views.AddressListView.as_view(), name='address_list'),
    path('add-address/', views.AddAddressAPIView.as_view(), name='add_address'),
    path('edit-address/<int:pk>/', views.EditAddressView.as_view(), name='edit_address'),
    path('delete-address/<int:pk>/', views.DeleteAddressView.as_view(), name='delete_address'),

]
