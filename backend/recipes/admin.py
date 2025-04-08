from django.contrib import admin
from .models import (
    Ingredient,
    Recipe,
    IngredientAndRecipe,
    FavoriteUserRecipes,
    Cart,
    User,
    Subscription
)
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin


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
        return user.authors_subscriptions.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "subscribing_user", "target")
    search_fields = (
        "user__username",
        "user__email",
        "target__username",
        "target__email"
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit", "get_recipes")
    search_fields = ('name', "measurement_unit")
    list_filter = ("measurement_unit",)

    @admin.display(description='Рецепты')
    def get_recipes(self, model):
        return model.recipes.count()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "cooking_time",
        "author",
        "get_favcount",
        "get_ingredients",
        "get_image",
    )
    search_fields = ("name", "author__username", "author__email")

    @admin.display(description="В избранном")
    def get_favcount(self, recipe):
        return recipe.favorites.count()

    @admin.display(description="Продукты")
    @mark_safe
    def get_ingredients(self, recipe):
        return '; '.join(
            f" {recipe_ingredient.ingredient.name}, \
{recipe_ingredient.amount} \
{recipe_ingredient.ingredient.measurement_unit}"
            for recipe_ingredient in recipe.recipe_ingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, recipe):
        return f'<img src="{recipe.image.url}" style="height: 70px;" />'


@admin.register(IngredientAndRecipe)
class IngredientAndRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")


@admin.register(FavoriteUserRecipes, Cart)
class FavoriteRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
