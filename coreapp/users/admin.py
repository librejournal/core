from django.contrib import admin
from django.contrib.auth import get_user_model

from coreapp.users.models import UserVerification, Profile

User = get_user_model()

# Register your models here.


class UserVerificationInline(admin.TabularInline):
    model = UserVerification


class UserProfileInlineAdmin(admin.TabularInline):
    model = Profile
    fields = [
        "id",
        "uuid",
        "type",
    ]
    readonly_fields = [
        "id",
        "uuid",
    ]
    can_delete = False


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
    ]
    inlines = [
        UserVerificationInline,
        UserProfileInlineAdmin,
    ]


admin.site.register(User, UserAdmin)
