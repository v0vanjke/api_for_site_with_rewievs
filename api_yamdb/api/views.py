from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from api.serializers import (ReviewSerializer, ReviewCommentSerializer,
                             CategorySerializer, GenreSerializer)
from reviews.models import Review, ReviewComment, User, Title, Genre, Category


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReviewCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['id'])
        serializer.save(
            review=review,
            author=self.request.user
        )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['id'])
        return review.comments.all()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes =
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes =
    search_fields = ('name', )
    lookup_field = 'slug'


# class TitleViewSet(viewsets.ModelViewSet):
    # queryset = Title.objects.all()
    # пока не разобрался тут, еще в процессе)
