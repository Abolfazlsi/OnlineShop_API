from django.urls import path, re_path, include
from product.views import HomePageView
from rest_framework.routers import DefaultRouter
from product import views

app_name = "product"
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('product-detail/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('comments/', views.CommentView.as_view(), name='comments'),
    path('add-comment/<slug:slug>/', views.CreateCommentView.as_view(), name='add-comment'),
    path('delete-comment/<int:pk>/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('edit-comment/<int:pk>/', views.EditCommentView.as_view(), name='edit-comment'),
]

