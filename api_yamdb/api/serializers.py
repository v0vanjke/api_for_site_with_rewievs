from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from review.models import Review, ReviewComment


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Review


class ReviewCommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = ReviewComment


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    following = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            ),

        ]

    def validate(self, data):
        if data['following'] == self.context['request'].user:
            raise ValidationError('Нельзя подписываться на самого себя!')
        return data
