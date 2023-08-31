from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User
USERNAME_LENGTH = 150
EMAIL_LENGTH = 254


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        max_length=50, unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['slug']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        max_length=50, unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['slug']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        db_index=True,
        validators=[MaxValueValidator(datetime.now().year),
                    MinValueValidator(0)])
    description = models.TextField(
        blank=True, null=True, max_length=200, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre, blank=True, verbose_name='Жанр', related_name='titles'
    )
    category = models.ForeignKey(
        Category, blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews',
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True,
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1), MaxValueValidator(10)
        ],
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_together'
            )
        ]

    def __str__(self):
        return (
            f'Отзыв пользователя {self.author} к'
            f' произведению {self.title.name}.'
        )


class ReviewComment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )
    text = models.TextField(verbose_name='Комментарий',)
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзывам'

    def __str__(self):
        return (
            f'Комментарий пользователя {self.author}'
            f' к отзыву {self.review}.'
        )
