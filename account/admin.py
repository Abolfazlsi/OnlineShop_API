from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.forms import UserChangeForm, UserCreationForm
from account.models import User, Otp, Address


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["phone", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["phone", "password"]}),
        (None, {"fields": ["fullname"]}),
        (None, {"fields": ["email"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["phone", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["phone"]
    ordering = ["phone"]
    filter_horizontal = []


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ("token", 'phone')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "fullname", "email", "postal_code")


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
