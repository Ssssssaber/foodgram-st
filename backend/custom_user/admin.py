from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from custom_user.models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "pk",
        "email",
        "username",
        "first_name",
        "last_name",
        "avatar"
    )
    search_fields = ("email", "username")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "target")
    search_fields = (
        "suser__username",
        "user__email",
        "target__username",
        "target__email"
    )
