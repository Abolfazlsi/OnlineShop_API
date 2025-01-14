# from django.core.paginator import Paginator
# from django.http import JsonResponse
# from django.shortcuts import render, get_object_or_404
# from django.views.generic import DetailView, TemplateView, View, ListView, CreateView
import rest_framework.permissions

from product.models import Product, Rating, Comment, Category, ContactUs
# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.urls import reverse_lazy
# import random
from rest_framework import viewsets
from product.serializer import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]


# class ProductDetailView(DetailView):
#     model = Product
#     template_name = "product/product_detail.html"
#
#     def post(self, request, slug):
#         text = request.POST.get("text")
#         product = get_object_or_404(Product, slug=slug)
#         if request.user.is_authenticated:
#             add_comment = Comment.objects.create(user=request.user, text=text, product=product)
#             return JsonResponse({
#                 "status": "success",
#                 "comment_text": add_comment.text,
#                 "user_username": add_comment.user.fullname if add_comment.user.fullname else add_comment.user.phone,
#                 "created_at": add_comment.time_since_creation(),
#                 'slug': product.slug
#             })
#
#
#     def get_related_products(self, product):
#         categories = product.category.all()
#
#         related_products = Product.objects.filter(category__in=categories).exclude(slug=product.slug)[:12]
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
# class RatingsView(View):
#     def get(self, request, slug):
#         product = get_object_or_404(Product, slug=slug)
#         try:
#             rating = Rating.objects.get(product=product, user=request.user)
#             rating.delete()
#             return JsonResponse({"response": "on_rating"})
#         except:
#             Rating.objects.create(product=product, user=request.user)
#             return JsonResponse({"response": "rating"})
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
