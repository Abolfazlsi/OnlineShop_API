from django.shortcuts import get_object_or_404
from product.models import Product
from cart.cart_module import Cart
from cart.models import DiscountCode, Order, OrderItem, UsedDiscountCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from cart.serializer import OrderSerializer, CartSerializer
from product.permissions import IsOrderOwner
from django.conf import settings
from account.models import Address
import requests
import json
from django.db import transaction


# cart detail
class CartDetailAPIView(APIView):
    def get(self, request):
        cart = Cart(request)

        cart_items = []
        for item in cart:
            product = item["product"]
            cart_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item["quantity"],
                "price": item["price"],
                "color": item["color"],
                "size": item["size"],
                "total": item["total"],
                "unique_id": item["unique_id"],
            })

        # total price of products
        total_price = cart.final_total()

        response_data = {
            "cart_items": cart_items,
            "total_price": total_price,
            # number of products in cart
            "product_count": cart.get_product_count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)


# cart add(add product to cart)
class CartAddAPIView(APIView):

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        serializer = CartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        quantity = serializer.validated_data.get("quantity")
        color = serializer.validated_data.get("color", "empty")
        size = serializer.validated_data.get("size", "empty")

        if not quantity or int(quantity) <= 0:
            return Response(
                {"detail": "Quantity must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # add product to cart if color and size were in product
        if (product.color.filter(name=color).exists() and product.size.filter(name=size).exists()) or (
                color == "empty" or size == "empty"):
            cart = Cart(request)
            cart.add(product, quantity, color, size)
            return Response(
                {"detail": "Product added to cart."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": 'Selected color or size does not exists for this product.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# delete product from cart
class CartDeleteAPIView(APIView):
    def delete(self, request, pk):
        cart = Cart(request)

        if not cart.item_exists(pk):
            return Response({"message": "product not found in cart"}, status=status.HTTP_404_NOT_FOUND)

        cart.delete(pk)
        return Response({"message": "product removed from cart"}, status=status.HTTP_200_OK)


# order details
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# add product from cart to orders
class OrderCreationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart(request)
        if not cart:
            return Response({"message": "cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total=cart.final_total())
                for item in cart:
                    OrderItem.objects.create(order=order, product=item["product"], quantity=item["quantity"],
                                             size=item["size"],
                                             color=item["color"], price=item["price"])
                cart.remove_cart()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# discount code
class DisCountCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        code = request.data.get("code")
        order = get_object_or_404(Order, id=pk)

        try:
            discount_code = DiscountCode.objects.get(code=code)
        except DiscountCode.DoesNotExist:
            return Response({"message": "invalid  discount code"}, status=status.HTTP_400_BAD_REQUEST)

        if UsedDiscountCode.objects.filter(user=request.user, discount_code=discount_code).exists():
            return Response({"message": "you have already use this discount code"}, status=status.HTTP_400_BAD_REQUEST)

        if discount_code.quantity <= 0:
            discount_code.delete()
            return Response({"message": "this discount code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        if order.is_paid:
            return Response({"message": "you have already paid the amount"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                discount_code.quantity -= 1
                discount_code.save()

                UsedDiscountCode.objects.create(user=request.user, discount_code=discount_code, order=order)

                order.total -= (order.total * discount_code.discount) / 100
                order.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# payment gateway
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'payment'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"

description = "Hello my dear friend"

CallbackURL = 'http://127.0.0.1:8000/cart/verify/'


# payment gateway
class SendRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)

        address = get_object_or_404(Address, id=request.data.get("address"))

        order.full_name = f"{address.fullname}"
        order.address = f"{address.address}"
        order.phone_number = f"{address.phone}"
        order.postal_code = f"{address.postal_code}"
        order.save()

        request.session["order_id"] = str(order.id)

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": order.total,
            "description": description,
            "callback_url": CallbackURL,
        }
        data = json.dumps(data)

        headers = {'content-type': 'application/json', 'content-length': str(len(data))}

        response = requests.post(ZP_API_REQUEST, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()

            if response["data"]['code'] == 100:
                url = f"{ZP_API_STARTPAY}{response['data']['authority']}"
                return Response({"redirect_url": url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": response["errors"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "something  were wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# verify payment gateway
class VerifyAPIView(APIView):

    def get(self, request):
        payment_status = request.query_params.get('Status')
        authority = request.query_params.get('Authority')

        order_id = request.session.get('order_id')
        if not order_id:
            return Response({"error": "order bot found"})

        order = get_object_or_404(Order, id=int(order_id))

        if payment_status == "OK":
            data = {
                "merchant_id": settings.MERCHANT,
                "amount": order.total,
                "authority": authority
            }
            data = json.dumps(data)

            headers = {'content-type': 'application/json', 'Accept': 'application/json'}

            response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()

                if response_data['data']['code'] == 100:
                    order.is_paid = True
                    order.save()
                    return Response({"message": "payment was successfully", "order_id": order.id})

                elif response_data['data']['code'] == 101:
                    return Response({"message": "payment has already been made"}, status=status.HTTP_200_OK)

                else:
                    return Response({"error": "payment failed"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"error": "error connecting to the payment gateway"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": "payment canceled by user"}, status=status.HTTP_200_OK)
