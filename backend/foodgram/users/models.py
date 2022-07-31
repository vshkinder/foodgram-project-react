from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    GUEST = 'guest'
    USER = 'user'
    USER_ROLES = [
        (USER, 'user'),
        (GUEST, 'guest'),
        (ADMIN, 'admin'),
    ]
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=150,
        unique=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        unique=False,
        verbose_name='Фамилия',
    )
    role = models.CharField(
        max_length=150,
        blank=False,
        choices=USER_ROLES,
        default='user',
        verbose_name='Роль пользователя',
    )
    password = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscribe'
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.author}'
