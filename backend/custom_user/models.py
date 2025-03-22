from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
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
    # avatar

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

