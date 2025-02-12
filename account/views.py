from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from .models import User, Otp, Address
from .serializers import UserRegisterSerializer, UserSerializer, AddressSerializer
from uuid import uuid4
from random import randint


# login and register with opt system
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


# check otp
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


# logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if refresh_token:
                outstanding_refresh_token = OutstandingToken.objects.get(token=refresh_token)
                BlacklistedToken.objects.create(token=outstanding_refresh_token)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except OutstandingToken.DoesNotExist as e:
            return Response({"detail": "Refresh token is invalid".format(str(e))}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# user profile
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # show details
    def get(self, request):
        user = request.user
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # update details
    def put(self, request):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# add address
class AddAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
