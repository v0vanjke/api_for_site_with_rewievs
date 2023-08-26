from django.urls import include, path
from rest_framework import routers

from api.views import (ReviewViewSet, ReviewCommentViewSet, TokenView,
                       SignUpView, UserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet)

routerv1 = routers.DefaultRouter()
routerv1.register('users', UserViewSet, basename='users')
routerv1.register(
    r'title/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
routerv1.register(
    r'title/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
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


urlpatterns = [
    path('v1/', include(routerv1.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
