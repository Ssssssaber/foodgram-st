from django.db import models
from custom_user.models import User


class Ingridient(models.Model):
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
        default='images/base.jpg'
    )
    description = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        verbose_name='Ингридиенты'
    )
    time_to_cook = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
