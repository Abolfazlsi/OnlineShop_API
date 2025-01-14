from django.contrib import admin
from product.models import Category, Product, Rating, Comment
from product.models import Category, Product, Rating, Comment, Color, Size, ContactUs


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    exclude = ("slug",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Size)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    list_filter = ("price", "category")
    exclude = ("slug",)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "product")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "product")


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("user", "email")
    search_fields = ("email",)