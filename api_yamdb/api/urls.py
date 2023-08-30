from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet, GenreViewSet, ReviewCommentViewSet,
    ReviewViewSet, TitleViewSet
)
from users.views import UserViewSet, TokenView, SignUpView

routerv1 = routers.DefaultRouter()
routerv1.register('users', UserViewSet, basename='users')
routerv1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
routerv1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    ReviewCommentViewSet,
    basename='comments',
)
routerv1.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
routerv1.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
routerv1.register(
    'titles',
    TitleViewSet,
    basename='titles'
)

auth_urls = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

urlpatterns = [
    path('v1/', include(routerv1.urls)),
    path('v1/auth/', include(auth_urls)),
]
