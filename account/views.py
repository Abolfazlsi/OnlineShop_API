import rest_framework.permissions
from django.shortcuts import render
from account.serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from account.models import User,Otp
from rest_framework.views import APIView
from random import randint
from uuid import uuid4
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User, Otp
from .serializers import UserRegisterSerializer
from uuid import uuid4
from random import randint


class UserRegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)


        if serializer.is_valid() or 'phone' in request.data:
            phone = request.data['phone']

            if len(phone) < 11 or len(phone) > 12:
                return Response({"message": "phone number is invalid"}, status=status.HTTP_400_BAD_REQUEST)

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
                'message': "User created in successfully"
            }, status=status.HTTP_200_OK)

        return Response({"Error": "invalid token or code"}, status=status.HTTP_400_BAD_REQUEST)



