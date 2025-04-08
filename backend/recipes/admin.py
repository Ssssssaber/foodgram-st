from django.contrib import admin
from .models import (
    Ingredient,
    Recipe,
    IngredientAndRecipe,
    FavoriteUserRecipes,
    UserCart
)
from django.utils.safestring import mark_safe


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


@admin.register(FavoriteUserRecipes, UserCart)
class FavoriteRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
