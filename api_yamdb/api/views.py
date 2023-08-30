import re
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError, models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings

from api.filters import FilterTitles
from api.permissions import (IsAdminOrReadOnly, IsOwnerOrIsAdmin,
                             IsOwnerOrIsAdminOrIsModerator)
from api.serializers import (CategorySerializer, GenreSerializer,
                             ReviewCommentSerializer, ReviewPostSerializer,
                             ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             )
from users.serializers import UserDisplaySerializer, UserCreateSerializer, SignUpSerializer, TokenSerializer
from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import Category, Genre, Review, Title
from users.models import User


class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()


class ReviewCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return (IsOwnerOrIsAdminOrIsModerator(),)
        elif self.action in ['retrieve', 'list']:
            return (AllowAny(),)
        return (IsAuthenticated(),)

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
    search_fields = ('name', )
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
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
    filterset_class = FilterTitles
    search_fields = ('name', 'year', 'genre__slug', 'category__slug')
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer
