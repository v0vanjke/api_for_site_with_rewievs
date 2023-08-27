from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import permissions, status, viewsets, filters, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from api.serializers import (ReviewSerializer, ReviewCommentSerializer,
                             CategorySerializer, GenreSerializer,
                             SignUpSerializer, UserSerializer,
                             TokenSerializer, TitleGetSerializer, TitlePostSerializer,
                             ReviewPostSerializer,)
from .permissions import (IsOwnerOrIsAdminOrIsModerator, IsAuthorOrReadOnly,
                          IsModeratorOrReadOnly, IsOwnerOrIsAdmin)
from reviews.models import Review, ReviewComment, User, Title, Genre, Category
from api_yamdb.settings import DEFAULT_FROM_EMAIL
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import FilterTitles
import re


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)}, status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrIsAdmin, )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=['put'], detail=True)
    def disallow_put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['get', 'patch'],
        url_path='me',
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            self.request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=self.request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return Response(
                {'detail': 'Имя пользователя должно содержать только буквы, цифры и подчеркивания.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            raise ValidationError(
                'Имя пользователя или email уже используются',
                status.HTTP_400_BAD_REQUEST
            )
        
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        return Response(confirmation_code, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewPostSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
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


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.annotate(
                rating=models.Avg("reviews__score")).order_by("id"))
    serializer_class = TitleGetSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitles
    search_fields = ('name', 'year', 'genre__slug', 'category__slug')
    # permission_classes =

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleGetSerializer
        return TitlePostSerializer
