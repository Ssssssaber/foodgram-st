from django.contrib import admin
from .models import Ingredient, Recipe, IngredientAndRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "author", "created_at")
    search_fields = ("name", "author__username", "author__email")

    @admin.display(description="Количество добавлений в избранное")
    def get_favorites(self, obj):
        return obj.favorites.count()


@admin.register(IngredientAndRecipe)
class IngredientAndRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
