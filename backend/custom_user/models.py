from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


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
