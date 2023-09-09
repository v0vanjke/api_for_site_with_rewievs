from datetime import datetime

import rest_framework.exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Review, ReviewComment, Title


class ReviewPostSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate_score(self, score):
        if score not in range(1, 11):
            raise ValidationError()
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

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class ReviewCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария к отзыву на произведение."""

    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
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
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
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
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        model = Title

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['genre'] = [
            GenreSerializer(genre).data for genre in instance.genre.all()
        ]
        return representation

    def validate_year(self, data):
        actual_year = datetime.today().year
        if int(self.initial_data['year']) > actual_year:
            raise serializers.ValidationError('Значение не может быть больше текущего года.')
        elif int(self.initial_data['year']) < 0:
            raise serializers.ValidationError('Значение не может быть меньше 0.')
        return data
