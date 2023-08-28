from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


USERNAME_LENGTH = 150
EMAIL_LENGTH = 254


class User(AbstractUser):
    """Модель пользователя"""
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


class Genre(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='name'
    )
    slug = models.SlugField(
        max_length=50, unique=True
    )

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='name'
    )
    slug = models.SlugField(
        max_length=50, unique=True
    )

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='name'
    )
    year = models.PositiveBigIntegerField(
        db_index=True
    )
    description = models.TextField(
        blank=True, null=True, max_length=200, verbose_name='description'
    )
    genre = models.ManyToManyField(
        Genre, blank=True, verbose_name='genre'
    )
    category = models.ForeignKey(
        Category, blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name='category'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True,
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_together'
            )
        ]


class ReviewComment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)