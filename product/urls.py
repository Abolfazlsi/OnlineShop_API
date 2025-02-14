from django.urls import path, re_path, include
from product import views
from rest_framework.routers import DefaultRouter
from product import views

app_name = "product"
urlpatterns = [
    path('', views.HomePageAPIView.as_view(), name='home'),
    # product's url
    path('products-list/', views.ProductListAPIView.as_view(), name='product_list'),
    re_path(r'product-detail/(?P<slug>[-\w]*)/', views.ProductDetailAPIView.as_view(), name='product_detail'),
    re_path(r'product-delete/(?P<slug>[-\w]*)/', views.ProductDeleteView.as_view(), name='product_delete'),
    re_path(r'product-edit/(?P<slug>[-\w]*)/', views.ProductEditView.as_view(), name='product_edit'),
    path('product-search/', views.ProductSearchAPIView.as_view(), name='product_search'),

    # category's url
    re_path(r'category-details/(?P<slug>[-\w]*)/', views.CategoryDetailsAPIView.as_view(), name='category_details'),
    path('category-list/', views.CategoryListAPIView.as_view(), name='category_list'),

    # comment's url
    path('comments/', views.CommentListView.as_view(), name='comments'),
    re_path(r'add-comment/(?P<slug>[-\w]*)/', views.CreateCommentAPIView.as_view(), name='add-comment'),
    path('delete-comment/<int:pk>/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('edit-comment/<int:pk>/', views.EditCommentView.as_view(), name='edit-comment'),

    # rating's url
    path('ratings/', views.RatingListView.as_view(), name='ratings'),
    re_path(r'add-rating/(?P<slug>[-\w]*)/', views.CreateRatingAPIView.as_view(), name='ratings'),

    # contact us
    path('contactus-list/', views.ContactUsListView.as_view(), name='contactus'),
    path('contactus-create/', views.CreateContactUsAPIView.as_view(), name='contactus_create'),

]
