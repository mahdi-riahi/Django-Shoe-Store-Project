from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from .forms import CustomUserChangeForm, AdminUserCreationForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = AdminUserCreationForm
    form = CustomUserChangeForm

    list_display = ('email', 'phone_number','is_staff', )
    ordering = ('email', )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name", "phone_number", "phone_verified", "email_verified")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone_number", "phone_verified", "password1", "password2", ),
            },
        ),
    )