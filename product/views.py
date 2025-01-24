import rest_framework.permissions
from celery.backends.database import retry
from django.db.transaction import commit
from django.http import Http404
from django.template.context_processors import request
from rest_framework.response import Response
from rest_framework.views import APIView
from product.models import Product, Rating, Comment, Category, ContactUs
from rest_framework import viewsets, generics
from product.serializer import ProductSerializer, CommentSerializer, RatingSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from product.permissions import IsCommentOwnerOrReadOnly


# ویو برای صفحه اصلی
class HomePageView(APIView):
    def get(self, request):
        # گرفتن 8 تا از اخرین محصولات
        latest_product = Product.objects.all()[:8]

        serializer = ProductSerializer(latest_product, many=True)
        response_data = {
            "latest_product": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# نشان دادن اطلاعات محصول
class ProductDetailView(APIView):
    def get_queryset(self, slug):
        try:
            # نشان دادن محصول از طریق slug
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Http404("Page Not Found")

    # نشان دادن محصول
    def get(self, request, slug):
        # اسفاده از ویو get_queryset
        product = self.get_queryset(slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # ادیت محصول
    def put(self, request, slug):
        product = self.get_queryset(slug)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            # ادیت محصول در صورت معتبر بودن داده های ورودی
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # حذف محصول
    def delete(self, request, slug):
        product = self.get_queryset(slug)
        # حذف محصول
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        serializer = CommentSerializer(data=request.data)
        product = Product.objects.get(slug=slug)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    queryset = Comment.objects.all()


class EditCommentView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class RatingListView(APIView):
    def get(self, request):
        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        serializer = RatingSerializer(data=request.data)
        product = Product.objects.get(slug=slug)

        if serializer.is_valid():
            try:
                rating = Rating.objects.get(product=product, user=request.user)
                rating.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Rating.DoesNotExist:
                serializer.save(user=request.user, product=product)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class ProductDetailView(DetailView):
#     model = Product
#     template_name = "product/product_detail.html"
#
#
#     def get_related_products(self, product):
#         categories = product.category.all()
#
#         related_products = Product.objects.filter(ategory__in=categories).exclude(slug=product.slug)[:12]
#         return related_products
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product = self.object
#
#         context['related_products'] = self.get_related_products(product)
#
#         if self.request.user.is_authenticated:
#             if self.request.user.ratings.filter(product=self.object, user=self.request.user).exists():
#                 context["is_rate"] = True
#             else:
#                 context["is_rate"] = False
#
#         return context
#
#
# class ProductsListView(ListView):
#     model = Product
#     template_name = "product/products_list.html"
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         request = self.request
#         min_price = request.GET.get("min_price")
#         max_price = request.GET.get("max_price")
#         filter = request.GET.get("filter")
#         colors = request.GET.getlist("color")
#         sizes = request.GET.getlist("size")
#         products = Product.objects.all()
#         page_number = request.GET.get("page", 1)
#
#         if min_price and max_price:
#             products = products.filter(price__gte=min_price, price__lte=max_price).distinct()
#
#         if filter == "cheapest":
#             products = products.order_by("price")
#         elif filter == "expensive":
#             products = products.order_by("-price")
#
#         if colors:
#             products = products.filter(color__name__in=colors).distinct()
#
#         if sizes:
#             products = products.filter(size__name__in=sizes).distinct()
#
#         paginator = Paginator(products, 9)
#         objects_list = paginator.get_page(page_number)
#
#         context = super(ProductsListView, self).get_context_data()
#         context["product_list"] = objects_list
#         context["selected_colors"] = colors
#         context["selected_sizes"] = sizes
#         return context
#
#
# class SearchProductView(ListView):
#     model = Product
#     template_name = "product/products_list.html"
#
#     def get_queryset(self):
#         q = self.request.GET.get("q")
#         queryset = Product.objects.filter(name__icontains=q) if q else Product.objects.all()
#         return queryset
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         request = self.request
#         q = request.GET.get("q")
#         products = Product.objects.filter(name__icontains=q) if q else Product.objects.all()
#         page_number = request.GET.get("page")
#
#         min_price = request.GET.get("min_price")
#         max_price = request.GET.get("max_price")
#         filter = request.GET.get("filter")
#         colors = request.GET.getlist("color")
#         sizes = request.GET.getlist("size")
#
#         if min_price and max_price:
#             products = products.filter(price__gte=min_price, price__lte=max_price).distinct()
#
#         if filter == "cheapest":
#             products = products.order_by("price").distinct()
#         elif filter == "expensive":
#             products = products.order_by("-price").distinct()
#
#         if colors:
#             products = products.filter(color__name__in=colors).distinct()
#
#         if sizes:
#             products = products.filter(size__name__in=sizes).distinct()
#
#         paginator = Paginator(products, 9)
#         objects_list = paginator.get_page(page_number)
#
#         context = super(SearchProductView, self).get_context_data()
#         context["product_list"] = objects_list
#         context["selected_colors"] = colors
#         context["selected_sizes"] = sizes
#         return context
#
#
# class CategoryDetailView(ListView):
#     model = Category
#     template_name = "product/products_list.html"
#
#     def get_queryset(self):
#         slug = self.kwargs.get("slug")
#
#         queryset = Product.objects.filter(category__slug=slug)
#
#         return queryset
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         request = self.request
#         slug = self.kwargs.get("slug")
#         min_price = request.GET.get("min_price")
#         max_price = request.GET.get("max_price")
#         filter = request.GET.get("filter")
#         colors = request.GET.getlist("color")
#         sizes = request.GET.getlist("size")
#         products = Product.objects.filter(category__slug=slug)
#         page_number = request.GET.get("page")
#
#         if min_price and max_price:
#             products = products.filter(price__gte=min_price, price__lte=max_price).distinct()
#
#         if filter == "cheapest":
#             products = products.order_by("price")
#         elif filter == "expensive":
#             products = products.order_by("-price")
#
#         if colors:
#             products = products.filter(color__name__in=colors).distinct()
#
#         if sizes:
#             products = products.filter(size__name__in=sizes).distinct()
#
#         paginator = Paginator(products, 9)
#         objects_list = paginator.get_page(page_number)
#
#         context = super(CategoryDetailView, self).get_context_data()
#         context["product_list"] = objects_list
#         context["selected_colors"] = colors
#         context["selected_sizes"] = sizes
#         return context
#
# class ContactUsView(CreateView):
#     model = ContactUs
#     form_class = ContactUsForm
#     template_name = "product/contact_us.html"
#     success_url = reverse_lazy("product:contact_us")
#     def form_valid(self, form):
#         instance = form.save(commit=False)
#         instance.user = self.request.user
#         instance.save()
#         return super(ContactUsView, self).form_valid(form)
#
