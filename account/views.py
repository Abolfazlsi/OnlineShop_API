import rest_framework.permissions
import rest_framework_simplejwt.authentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from .models import User, Otp
from .serializers import UserRegisterSerializer
from uuid import uuid4
from random import randint
from django.contrib.auth import login, logout


# کلس برای لاگین یا رجیستر کردن کاربر
class UserRegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        # وجود "phone" در شرط برای ارور ندادن در صورت وجود کاربر با این شماره
        if serializer.is_valid() or 'phone' in request.data:
            phone = request.data['phone']

            # چک کردن شماره موبایل
            if len(phone) < 11 or len(phone) > 12:
                return Response({"message": "phone number is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            # ساخت کد
            code = randint(1000, 9999)

            # ساخت توکن
            token = str(uuid4())

            Otp.objects.update_or_create(phone=phone, defaults={'code': code, 'token': token})

            # استفاده از print فقط برای تست
            print(code)
            return Response({"token": token}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# برای وریفای کردن کاربر
class OtpVerifyViewSet(viewsets.ViewSet):
    def create(self, request):
        # گرفتن توکن و کد
        token = request.data.get('token')
        code = request.data.get('code')

        # چک کردن وجود کد در دیتا بیس
        if Otp.objects.filter(token=token, code=code).exists():
            # ایجاد otp تا بعدا برای حذف ان پس از لاکین کاربر
            otp = Otp.objects.get(token=token)

            # ایجاد کاربر در صورا وجود نداشتن و یا لاگین کاربر در صورت وجود داشتن
            user, created = User.objects.get_or_create(phone=otp.phone)

            otp.delete()

            # نمایش دادن refersh  و access و پیغام مناسب برای کاربر
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': "User logged in successfully"
            }, status=status.HTTP_200_OK)

        return Response({"Error": "Invalid token or code"}, status=status.HTTP_400_BAD_REQUEST)


# خروج کاربر
class LogoutView(APIView):
    # دسترسی کاربر در صورت لاکین بودن
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # گرفتن refresh token
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if refresh_token:
                # چک کردن refresh برای وجود ان در دیتا بیس
                outstanding_refresh_token = OutstandingToken.objects.get(token=refresh_token)
                # بلاک کردن refresh token کاربر
                BlacklistedToken.objects.create(token=outstanding_refresh_token)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except OutstandingToken.DoesNotExist as e:
            return Response({"detail": "Refresh token is invalid".format(str(e))}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
