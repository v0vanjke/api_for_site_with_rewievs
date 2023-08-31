from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        null=False,
        blank=False,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        max_length=50,
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLES,
        default=USER,
        blank=True,
        max_length=100,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=10,
        null=True,
        blank=False,
        default='XXXXX'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
