import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from reviews.models import (
    EMAIL_LENGTH, USERNAME_LENGTH, Category,
    Genre, Review, ReviewComment, Title, User,
)
from django.conf import settings


class ReviewPostSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate_score(self, score):
        if score not in range(1, 11):
            raise ValidationError(
                'Оценка должна быть целым значением от 1 до 10.')
        return score

    def validate(self, data):
        if Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['view'].kwargs['title_id']
        ).exists():
            raise serializers.ValidationError('Можно оставить только'
                                              'один отзыв к произведению!')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва на произведение."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Review


class ReviewCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария к отзыву на произведение."""

    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = ReviewComment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории произведения."""

    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра произведения."""

    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных о произведении."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведения."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title
