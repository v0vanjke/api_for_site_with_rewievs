from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='name'
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
        max_length=200, verbose_name='name'
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
