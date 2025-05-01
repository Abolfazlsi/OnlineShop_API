from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from .models import User, Otp, Address
from .serializers import UserRegisterSerializer, AddressSerializer, UserSerializer
from uuid import uuid4
from random import randint
from account.tasks import delete_otp
from product.permissions import IsOwnerOrReadOnly


# login and register with opt system
class UserRegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        phone = request.data.get("phone")

        if serializer.is_valid() or User.objects.filter(phone=phone).exists():
            code = randint(1000, 9999)

            token = str(uuid4())

            otp = Otp.objects.create(phone=phone, code=code, token=token)

            print(code)  # for test
            print(otp.id)

            # delete_otp.apply_async(args=[otp.id], countdown=30)

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
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
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
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# addresses list
class AddressListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


# add address
class AddAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# edit address(just owner can edit it)
class EditAddressView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


# delete address(just owner can delete it)
class DeleteAddressView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Address.objects.all()
