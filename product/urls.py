from django.urls import path, re_path, include
from product.views import HomePageView
from rest_framework.routers import DefaultRouter
from product import views

app_name = "product"
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('product-detail/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]

