from django.urls import path, re_path, include
from product.views import ProductViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

app_name = "product"
urlpatterns = [
    path('', include(router.urls)),
]
