from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from product.models import Product  # جایگزین کنید با مسیر واقعی مدل Product
from cart.views import CartDetailAPIView
from django.urls import reverse


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
