from django.test import TestCase
from rest_framework.test import APITestCase
from product.models import Product, Color, Size, Category
from cart.models import Order, OrderItem
from account.models import User
from product.models import Product
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import BlacklistedToken


class TestCartDetailAPIView(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="shirt",
            price=17000,
        )

        self.session = self.client.session
        self.session["cart"] = {
            "1-red-L": {
                "id": str(self.product.id),
                "quantity": 2,
                "price": "17000",
                "color": "red",
                "size": "L",
            }
        }

        self.session.save()

    def test_cart_detail_view(self):
        response = self.client.get(reverse('cart:cart'))
        self.assertEqual(response.status_code, 200)

        expected_data = {
            "cart_items": [
                {
                    "product_id": self.product.id,
                    "product_name": "shirt",
                    "quantity": 2,
                    "price": "17000",
                    "color": "red",
                    "size": "L",
                    "total": 34000,
                    "unique_id": f"{self.product.id}-red-L"
                }
            ],
            "total_price": 34000,
            "product_count": 1
        }
        self.assertEqual(response.data, expected_data)

    def test_empty_cart(self):
        self.session["cart"] = {}
        self.session.save()

        response = self.client.get(reverse('cart:cart'))
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "cart_items": [],
            "total_price": 0,
            "product_count": 0
        }

        self.assertEqual(response.data, expected_data)

    def test_cart_with_multiple_items(self):
        product2 = Product.objects.create(
            name="computer",
            price=200,
        )
        self.session["cart"] = {
            "1-red-L": {
                "id": str(self.product.id),
                "quantity": 2,
                "price": "17000",
                "color": "red",
                "size": "L",
            },
            "2-blue-M": {
                "id": product2.id,
                "quantity": 3,
                "price": "200",
                "color": "blue",
                "size": "M",
            }
        }
        self.session.save()

        response = self.client.get(reverse('cart:cart'))

        self.assertEqual(response.status_code, 200)

        expected_data = {
            "cart_items": [
                {
                    "product_id": self.product.id,
                    "product_name": "shirt",
                    "quantity": 2,
                    "price": "17000",
                    "color": "red",
                    "size": "L",
                    "total": 34000,
                    "unique_id": f"{self.product.id}-red-L"
                },
                {
                    "product_id": product2.id,
                    "product_name": "computer",
                    "quantity": 3,
                    "price": "200",
                    "color": "blue",
                    "size": "M",
                    "total": 600,
                    "unique_id": f"{product2.id}-blue-M"
                }
            ],
            "total_price": 34600,
            "product_count": 2
        }

        self.assertEqual(response.data, expected_data)

    def test_product_with_zero_price(self):
        product = Product.objects.create(
            name="computer",
            price=0,
        )

        self.session["cart"] = {
            "2-red-L": {
                "id": str(product.id),
                "quantity": 2,
                "price": "0",
                "color": "red",
                "size": "L",
            },
        }
        self.session.save()

        response = self.client.get(reverse('cart:cart'))

        self.assertEqual(response.status_code, 200)

        expected_data = {
            "cart_items": [
                {
                    "product_id": product.id,
                    "product_name": "computer",
                    "quantity": 2,
                    "price": "0",
                    "color": "red",
                    "size": "L",
                    "total": 0,
                    "unique_id": f"{product.id}-red-L"
                }
            ],
            "total_price": 0,
            "product_count": 1
        }

        self.assertEqual(response.data, expected_data)


class TestCartAddAPIView(TestCase):
    def setUp(self):
        color = Color.objects.create(
            name="blue"
        )

        size = Size.objects.create(
            name="M"
        )

        self.product = Product.objects.create(
            name="computer",
            price=100,
        )
        self.product.color.add(color)
        self.product.size.add(size)

        self.url = reverse("cart:add_cart", args=[self.product.id])

    def test_cart_add_view_with_valid_data(self):
        data = {
            "quantity": 3,
            "color": "blue",
            "size": "M"
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"detail": "Product added to cart."})

        cart = self.client.session.get("cart", {})
        self.assertIn(f"{self.product.id}-blue-M", cart)

    def test_cart_add_view_without_color_and_size(self):
        data = {
            "quantity": 3
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"detail": "Product added to cart."})

        cart = self.client.session.get("cart", {})
        self.assertIn(f"{self.product.id}-empty-empty", cart)

    def test_cart_add_view_without_quantity(self):
        data = {
            "color": "blue",
            "size": "M"
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("This field is required.", response.data["quantity"])

    def test_cart_add_view_with_invalid_quantity(self):
        data = {
            "quantity": 0,
            "color": "red",
            "size": "L"
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Ensure this value is greater than or equal to 1.", response.data["quantity"])

    def test_cart_add_view_with_invalid_color_and_size(self):
        data = {
            "quantity": 3,
            "color": "red",
            "size": "L"
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"message": "Selected color or size does not exists for this product."})

    def test_cart_add_nonexistent_product(self):
        data = {
            "quantity": 3,
            "color": "red",
            "size": "L"
        }
        response = self.client.post(reverse("cart:add_cart", args=[10]), data=data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "No Product matches the given query."})


class TestCartDeleteAPIView(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="shirt",
            price=17000,
        )

        self.session = self.client.session
        self.session["cart"] = {
            "1-red-L": {
                "id": str(self.product.id),
                "quantity": 2,
                "price": "17000",
                "color": "red",
                "size": "L",
            }
        }

        self.session.save()

        self.url = reverse("cart:delete_cart", args=[f"{self.product.id}-red-L"])

    def test_cart_delete_view(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "product removed from cart"})

        cart = self.client.session.get("cart", {})
        self.assertNotIn("1-red-L", cart)
        self.assertEqual(cart, {})

    def test_nonexistent_product(self):
        response = self.client.delete(reverse("cart:delete_cart", args=["5-red-L"]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"message": "product not found in cart"})

        cart = self.client.session.get("cart", {})
        self.assertIn("1-red-L", cart)


class TestOrderDetailAPIView(APITestCase):
    def setUp(self):
        color = Color.objects.create(
            name="blue"
        )

        size = Size.objects.create(
            name="M"
        )

        category = Category.objects.create(
            name="shirt"
        )
        self.user = User.objects.create_user(phone="09876543212")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

        self.order = Order.objects.create(user=self.user, total=90000, is_paid=False, full_name="John Doe",
                                          address="Hello World", phone_number="09876543234", postal_code="7195473")

        self.product = Product.objects.create(name="T-shirt", description="Hello World", price=67000)
        self.product.color.add(color)
        self.product.size.add(size)
        self.product.category.add(category)

        self.order_item1 = OrderItem.objects.create(order=self.order, product=self.product, quantity=3, size="L",
                                                    color="red", price=900)
        self.order_item2 = OrderItem.objects.create(order=self.order, product=self.product, quantity=4, size="M",
                                                    color="blue", price=900)

    def test_with_auth_user_and_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        response = self.client.get(reverse("cart:order_detail", args=[self.order.id]))

        data = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["full_name"], "John Doe")
        self.assertEqual(data["phone_number"], "09876543234")
        self.assertIn("orderitems", data)
        self.assertEqual(data["orderitems"][0]["color"], "red")
        self.assertEqual(data["orderitems"][0]["price"], 900)
        self.assertEqual(data["orderitems"][1]["color"], "blue")
        self.assertEqual(data["orderitems"][1]["price"], 900)

    def test_with_auth_user_and_is_not_owner(self):
        self.user = User.objects.create_user(phone="09876543290")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        response = self.client.get(reverse("cart:order_detail", args=[self.order.id]))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"detail": "You do not have permission to perform this action."})

    def test_with_anon_user(self):
        response = self.client.get(reverse("cart:order_detail", args=[self.order.id]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})


class TestOrderCreationAPIView(APITestCase):

    def setUp(self):
        color = Color.objects.create(
            name="blue"
        )

        size = Size.objects.create(
            name="M"
        )

        category = Category.objects.create(
            name="shirt"
        )

        self.user = User.objects.create_user(phone="09876543212")
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

        self.product = Product.objects.create(name="T-shirt", description="Hello World", price=67000)
        self.product.color.add(color)
        self.product.size.add(size)
        self.product.category.add(category)

        self.product2 = Product.objects.create(name="computer", description="Hello World2", price=89600)
        self.product2.color.add(color)
        self.product2.size.add(size)
        self.product2.category.add(category)

        self.session = self.client.session
        self.session["cart"] = {
            "1-red-L": {
                "id": str(self.product.id),
                "quantity": 2,
                "price": "17000",
                "color": "red",
                "size": "L",
            },
            "2-blue-M": {
                "id": self.product2.id,
                "quantity": 3,
                "price": "200",
                "color": "blue",
                "size": "M",
            }
        }
        self.session.save()

    def test_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.post(reverse("cart:order_creation"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total"], 34600),
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)

    def test_with_empty_cart(self):
        user = User.objects.create_user(phone="09876543292")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        self.session["cart"] = None
        self.session.save()

        # Send POST request with empty cart
        response = self.client.post(reverse("cart:order_creation"))

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"message": "cart is empty"})
        self.assertEqual(Order.objects.count(), 0)



