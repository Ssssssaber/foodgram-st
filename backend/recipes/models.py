from django.db import models
from custom_user.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=300
    )
    measure = models.CharField(
        verbose_name='Единица измерения',
        max_length=50
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measure"], name="u_ingredient"
            )
        ]
        ordering = ("name",)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    picture = models.ImageField(
        verbose_name='Картинка',
        upload_to='images',
        default='media/base.png'
    )
    description = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        through='IngredientAndRecipe',
        verbose_name='Ингридиенты'
    )
    time_to_cook = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах'
    )
    # keke = models.CharField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("-created_at",)


class IngredientAndRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name=''
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=''
    )
    amount = models.PositiveIntegerField(
        verbose_name=''
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    def __str__(self):
        return self.recipe.name + " - " + self.ingredient.name

    class Meta:
        verbose_name = 'Ингредиент и рецепт'
        verbose_name_plural = 'Ингридиенты и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="u_ingredient_and_recipe"
            )
        ]
        ordering = ("-created_at",)


class RecipeAndUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    def __str__(self):
        return f"{self.user} - {self.recipe}"

    class Meta:
        abstract = True


class FavoriteUserRecipes(RecipeAndUser):

    class Meta(RecipeAndUser.Meta):
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        default_related_name = "favorites"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="u_favorite_user_recipe"
            )
        ]


class UserCart(RecipeAndUser):

    class Meta(RecipeAndUser.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        default_related_name = "carts"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="u_user_cart"
            )
        ]
