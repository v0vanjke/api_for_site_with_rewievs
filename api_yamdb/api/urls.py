from django.urls import include, path
from rest_framework import routers

from api.views import (ReviewViewSet, ReviewCommentViewSet,
                       sent_confirmation_code)

routerv1 = routers.DefaultRouter()
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

urlpatterns = [
    path('v1/', include(routerv1.urls)),
    path('api/v1/auth/signup/', sent_confirmation_code, name='signup'),
    path('api/v1/auth/token/', sent_confirmation_code, name='token'),
]
