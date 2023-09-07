import re

import rest_framework.exceptions
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import IntegrityError
from rest_framework import serializers

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import EMAIL_LENGTH, USERNAME_LENGTH
from users.models import User
from users.validators import validate_username


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей."""

    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя должно'
                        'соответствовать паттерну ^[\\w.@+-]+$.'
            )
        ]
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    def validate_username(self, value):
        return validate_username(value)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем пользователя уже существует.'
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return data

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserDisplaySerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    def validate_username(self, value):
        return validate_username(value)

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'Имя пользователя или email уже используются.'
            )
        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                'Имя пользователя или email уже используются.'
            )
        return instance


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, username):
        if username is None:
            raise serializers.ValidationError('Поле username обязательно для заполнения.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError(
                'Имя пользователя должно содержать'
                'только латинские буквы, цифры и подчеркивания.'
            )
        if User.objects.filter(username=self.initial_data['username']).exists():
            return username
        raise rest_framework.exceptions.NotFound('Пользователь не найден.')

    def validate_confirmation_code(self, data):
        username = self.initial_data.get('username')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.confirmation_code != self.initial_data['confirmation_code']:
                raise serializers.ValidationError('Неверный код подтверждения.')
            return data
        raise serializers.ValidationError(
            f'Код подтверждения для пользователя {username} отсутствует.'
        )

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )