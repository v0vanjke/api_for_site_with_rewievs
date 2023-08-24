from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django_filters import rest_framework
from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from api.serializers import (ReviewSerializer, ReviewCommentSerializer,
                             CategorySerializer, GenreSerializer,
                             SignUpSerializer, UserSerializer,
                             TokenSerializer, ConfirmationCodeSerializer,
                             )
from .permissions import (IsAdminOrReadOnly, IsAuthorOrReadOnly,
                          IsModeratorOrReadOnly, IsOwnerOrIsAdmin)
from reviews.models import Review, ReviewComment, User, Title, Genre, Category
from api_yamdb.settings import DEFAULT_FROM_EMAIL


def sent_confirmation_code(request):
    """Функция отправки кода подтверждения при регистрации"""
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def get_token(request):
    """Функция для получения токена"""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения!'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsAdmin]
    pagination_class = PageNumberPagination
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_fields = ["username"]
    lookup_field = "username"

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == "GET":
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class SignUp(APIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sent_confirmation_code(request)
        return Response(request.data, status=status.HTTP_200_OK)


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
