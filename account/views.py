import rest_framework.permissions
import rest_framework_simplejwt.authentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import User, Otp
from .serializers import UserRegisterSerializer
from uuid import uuid4
from random import randint
from django.contrib.auth import login, logout


class UserRegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid() or 'phone' in request.data:
            phone = request.data['phone']

            if len(phone) < 11 or len(phone) > 12:
                return Response({"message": "phone number is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            code = randint(1000, 9999)
            token = str(uuid4())

            Otp.objects.update_or_create(phone=phone, defaults={'code': code, 'token': token})

            print(code)
            return Response({"token": token}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerifyViewSet(viewsets.ViewSet):
    def create(self, request):
        token = request.data.get('token')
        code = request.data.get('code')

        if Otp.objects.filter(token=token, code=code).exists():
            otp = Otp.objects.get(token=token)
            user, created = User.objects.get_or_create(phone=otp.phone)

            otp.delete()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': "User logged in successfully"
            }, status=status.HTTP_200_OK)

        return Response({"Error": "Invalid token or code"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get('refresh')

        try:
            if refresh_token:
                outstanding_refresh_token = OutstandingToken.objects.get(token=refresh_token)
                BlacklistedToken.objects.create(token=outstanding_refresh_token)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except OutstandingToken.DoesNotExist as e:
            return Response({"detail": "invalid token".format(str(e))}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)