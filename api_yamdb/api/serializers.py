from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError

from reviews.models import Review, ReviewComment, Category, Genre, Title, User


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор для получения кода подтверждения"""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользоваталей"""
    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Имя пользователя недоступно')
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Review
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            ),

        ]

    def validate(self, data):
        if data['score'] not in range(1, 11):
            raise ValidationError('Оценка должна быть целым значением от 1 до 10.')
        return data


class ReviewCommentSerializer(serializers.ModelSerializer):
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
    class Meta:
        exclude = ('id', )
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
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

