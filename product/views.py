from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView
from product.models import Product, Rating, Comment, ContactUs, Category
from rest_framework import viewsets, generics
from product.serializer import ProductSerializer, CommentSerializer, RatingSerializer, CategorySerializer, \
    ContactUsSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from product.permissions import IsCommentOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from product.filter_prodcts import filter_product
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


# home page
class HomePageAPIView(APIView):
    def get(self, request):
        latest_product = Product.objects.all()[:8]
        best_seller = Product.objects.annotate(rating_count=Count("ratings")).order_by('-rating_count')[:1]
        latest_product_serializer = ProductSerializer(latest_product, many=True)
        best_seller_serializer = ProductSerializer(best_seller, many=True)

        response_data = {
            "latest_products": latest_product_serializer.data,
            "best_seller": best_seller_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# products list
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# product search(found product by name)
class ProductSearchAPIView(APIView, PageNumberPagination):
    def get(self, request):
        q = request.GET.get("q", "")

        filtered_products = filter_product(request)
        filtered_products = filtered_products.filter(name__icontains=q).distinct()

        result = self.paginate_queryset(filtered_products, request, view=self)

        serializer = ProductSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


# product detail
class ProductDetailAPIView(APIView):
    def get(self, request, slug):
        # اسفاده از ویو get_queryset
        product = get_object_or_404(Product, slug=slug)
        categories = product.category.all()
        # 12 related product
        related_products = Product.objects.filter(category__in=categories).exclude(slug=product.slug).prefetch_related(
            'category')[:12]

        product_serializer = ProductSerializer(product)
        related_product_serializer = ProductSerializer(related_products, many=True)

        response_data = {
            "product": product_serializer.data,
            "related_product": related_product_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# product edit(just admin can edit it)
class ProductEditView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ProductSerializer

    # get product by slug for edit
    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Product, slug=slug)


# delete product(just admin can delete it)
class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ProductSerializer

    # get product by slug for delete
    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Product, slug=slug)


# comments list
class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


# add comment
class CreateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        serializer = CommentSerializer(data=request.data)
        product = Product.objects.get(slug=slug)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# delete comment(just owner can delete it)
class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    queryset = Comment.objects.all()


# edit comment(just owner can edit it)
class EditCommentView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


# ratings list
class RatingListView(generics.ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


# add rating to product
class CreateRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        serializer = RatingSerializer(data=request.data)
        product = Product.objects.get(slug=slug)

        if serializer.is_valid():
            try:
                # delete ratings if rating already exists
                rating = Rating.objects.get(product=product, user=request.user)
                rating.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Rating.DoesNotExist:
                # add rating if raring does not exist
                serializer.save(user=request.user, product=product)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# category list
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# show products that related by category
class CategoryDetailsAPIView(APIView, PageNumberPagination):
    def get(self, request, slug):
        q = request.GET.get("q", "")

        filtered_product = filter_product(request)
        filtered_product = filtered_product.filter(Q(category__slug=slug) & Q(name__icontains=q))

        result = self.paginate_queryset(filtered_product, request, view=self)

        serializer = ProductSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


# list of people who send message to shop
class ContactUsListView(generics.ListAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer


# add contact us
class CreateContactUsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
