from django.urls import path
from cart import views

app_name = "cart"
urlpatterns = [
    # cart's url
    path("cart/", views.CartDetailAPIView.as_view(), name="cart"),
    path("add-cart/<int:pk>/", views.CartAddAPIView.as_view(), name="add_cart"),
    path("delete-cart/<str:pk>/", views.CartDeleteAPIView.as_view(), name="delete_cart"),
]
