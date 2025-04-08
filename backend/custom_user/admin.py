from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from custom_user.models import User, Subscription
from django.utils.safestring import mark_safe


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "pk",
        "username",
        "full_name",
        "email",
        "get_avatar",
        "get_recipes_count",
        "get_subscriptions",
        "get_subscribers"
    )
    search_fields = ("email", "username")

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar(self, user):
        if user.avatar:
            return f'<img src="{user.avatar.url}" style="height: 70x;" />'
        return 'Нет аватара'

    @admin.display(description='Количество рецептов')
    def get_recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def get_subscriptions(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчики')
    def get_subscribers(self, user):
        return user.authors.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "subscribing_user", "target")
    search_fields = (
        "user__username",
        "user__email",
        "target__username",
        "target__email"
    )
