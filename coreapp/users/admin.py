from django.contrib import admin
from django.contrib.auth import get_user_model

from coreapp.users.models import UserVerification

User = get_user_model()

# Register your models here.

class UserVerificationInline(admin.TabularInline):
    model = UserVerification


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
    ]
    inlines = [UserVerificationInline]

admin.site.register(User, UserAdmin)
