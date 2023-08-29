import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (
    EMAIL_LENGTH, USERNAME_LENGTH, Category,
    Genre, Review, ReviewComment, Title, User,
)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                'Имя пользователя должно содержать только',
                'буквы, цифры и подчеркивания.'
            )
        return value

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        bio = validated_data.get('bio', '')
        role = validated_data.get('role', User.USER)

        existing_user_by_username = (
            User.objects
            .filter(username=username)
            .first()
        )
        if existing_user_by_username:
            raise serializers.ValidationError(
                'Пользователь с таким именем пользователя уже существует.'
            )

        existing_user_by_email = User.objects.filter(email=email).first()
        if existing_user_by_email:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            role=role
        )
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользоваталей."""

    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    class Meta:
        model = User
        fields = ['email', 'username']

    def create(self, validated_data):
        user = User.objects.create(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )
        return user

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Имя пользователя недоступно')
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField(required=True)

    def validate_code(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтерждения')
        return RefreshToken.for_user(user).access_token

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


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

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        model = Title
