from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from reviews.models import Category, Genre, Review, Title
from api.filters import FilterTitle
from api.permissions import IsAdminOrReadOnly, IsOwnerOrIsAdminOrIsModerator
from api.serializers import (CategorySerializer, GenreSerializer,
                             ReviewCommentSerializer, ReviewPostSerializer,
                             ReviewSerializer, TitleGetSerializer,
                             TitlePostSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_current_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewPostSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return (IsOwnerOrIsAdminOrIsModerator(),)
        elif self.action in ['retrieve', 'list']:
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def perform_create(self, serializer):
        serializer.save(
            title=self.get_current_title(),
            author=self.request.user,
        )

    def get_queryset(self):
        return self.get_current_title().reviews.all()


class ReviewCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_current_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return (IsOwnerOrIsAdminOrIsModerator(),)
        elif self.action in ['retrieve', 'list']:
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_current_review(),
            author=self.request.user
        )

    def get_queryset(self):
        return self.get_current_review().comments.all()


class GenreCategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):

    """
    """


class CategoryViewSet(GenreCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name', )
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(GenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ('name', )
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects
        .annotate(rating=models.Avg("reviews__score"))
        .order_by("id")
    )
    serializer_class = TitleGetSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle
    search_fields = ('name', 'year', 'genre__slug', 'category__slug')
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer
