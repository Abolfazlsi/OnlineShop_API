from django.urls import path
from cart import views

app_name = "cart"
urlpatterns = [
    # cart's url
    path("cart/", views.CartDetailAPIView.as_view(), name="cart"),
    path("add-cart/<int:pk>/", views.CartAddAPIView.as_view(), name="add_cart"),
    path("delete-cart/<str:pk>/", views.CartDeleteAPIView.as_view(), name="delete_cart"),

    # order's url
    path("order-detail/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("order-creation/", views.OrderCreationAPIView.as_view(), name="order_creation"),

    # pay
    path("send-request/<int:pk>/", views.SendRequestAPIView.as_view(), name="send_request"),
    path("verify/", views.VerifyAPIView.as_view(), name="verify"),

    # discount
    path("apply-discount/<int:pk>/", views.DisCountCodeAPIView.as_view(), name="apply_discount"),

]
