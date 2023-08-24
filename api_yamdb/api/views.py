from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins

from api.serializers import (ReviewSerializer, ReviewCommentSerializer,
                             CategorySerializer, GenreSerializer,
                             TitleGetSerializer, TitlePostSerializer)
from api.filters import FilterTitles
from reviews.models import Review, ReviewComment, User, Title, Genre, Category
from rest_framework.filters import SearchFilter
from rest_framework.pagination import (PageNumberPagination)
from rest_framework.permissions import SAFE_METHODS


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(
            title=title,
            author=self.request.user,
        )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()


class ReviewCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(
            review=review,
            author=self.request.user
        )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        return review.comments.all()


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    # permission_classes =
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    # permission_classes =
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.prefetch_related(
            "title_genre", "category").annotate(
                rating=models.Avg("reviews__score")).order_by("id"))
    serializer_class = TitleGetSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitles
    search_fields = ('name', 'year', 'genre__slug', 'category__slug')
    # permission_classes =

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer
