from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Псевдоним',
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+\- ]+$')],
        unique=True
    )
    email = models.CharField(
        verbose_name='Электронная почта',
        max_length=256,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="media/user_avatars/",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ("-created_at",)


class Subscription(models.Model):
    subscribing_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Подписчик",
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authors_subscriptions",
        verbose_name="Пользователь",
    )

    def __str__(self):
        return f"{self.subscribing_user} -> {self.target}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("subscribing_user", "target"),
                name="u_subscriptions"
            )
        ]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=64
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="u_ingredient"
            )
        ]
        ordering = ("name",)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes'
    )
    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAndRecipe',
        verbose_name='Продукты',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(1),
        ],
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
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    amount = models.PositiveIntegerField(
        verbose_name=''
    )

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"

    class Meta:
        verbose_name = 'Продукт и рецепт'
        verbose_name_plural = 'Продукты и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="u_ingredient_and_recipe"
            )
        ]


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
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="u_%(class)s"
            )
        ]


class FavoriteUserRecipes(RecipeAndUser):

    class Meta(RecipeAndUser.Meta):
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        default_related_name = "favorites"


class Cart(RecipeAndUser):

    class Meta(RecipeAndUser.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        default_related_name = "carts"
