from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, TokenObtainView,
                       UserRegistrationView, UserViewSet)
from django.urls import include, path
from rest_framework.routers import SimpleRouter

router_v1 = SimpleRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/'
                   r'(?P<review_id>\d+)/comments',
                   CommentViewSet, basename='comments')

auth_patterns = [
    path(
        'token/',
        TokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'signup/',
        UserRegistrationView.as_view(),
        name='signup'
    ),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_patterns))]
