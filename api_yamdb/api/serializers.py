from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError

from reviews.models import Review, ReviewComment


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
