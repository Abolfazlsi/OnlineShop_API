from django.shortcuts import render
from account.serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from account.models import User,Otp
from rest_framework.views import APIView
from random import randint
from uuid import uuid4
from django.contrib.auth import login, logout
class UserRegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = randint(1000, 9999)
            token = str(uuid4())
            Otp.objects.create(phone=phone, code=code, token=token)
            print(code)
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OtpVerifyViewSet(viewsets.ViewSet):
    def create(self, request):
        token = request.data.get('token')
        code = request.data.get('code')
        if Otp.objects.filter(token=token, code=code).exists():
            otp = Otp.objects.get(token=token)
            if User.objects.filter(phone=otp.phone).exists():
                user = User.objects.get(phone=otp.phone)
                login(request, user)
                otp.delete()
            else:
                created = User.objects.create(phone=otp.phone)
                login(request, created)
                otp.delete()
            return Response({"message": "User logged in successfully"}, status=status.HTTP_200_OK)
        return Response({"Error": "invalid token or code"}, status=status.HTTP_400_BAD_REQUEST)


