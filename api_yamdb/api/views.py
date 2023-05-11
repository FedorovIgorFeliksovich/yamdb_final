from api.filterset import TitleFilter
from api.mixins import BaseMixinViewClass
from api.permission import (AuthorModeratorAdminOrReadOnly, IsAdmin,
                            IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitleSerializer,
                             TokenObtainSerializer, UserRegistrationSerializer,
                             UserSerializer)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainSlidingView
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    permission_classes = (IsAdmin,)

    @action(detail=False, methods=['GET', 'PATCH'], url_path='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = self.serializer_class(request.user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                instance=request.user,
                data=request.POST,
                partial=True
            )
            serializer.fields.pop('role')
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return None


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(BaseMixinViewClass):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenreViewSet(BaseMixinViewClass):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return TitleGetSerializer
        return TitleSerializer


class TokenObtainView(TokenObtainSlidingView):
    "View для получения JWT"
    serializer_class = TokenObtainSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            if 'error' in serializer.validated_data:
                return Response(
                    serializer.validated_data,
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = User.objects.filter(**serializer.data).last()
        if user:
            code = default_token_generator.make_token(user)
            send_mail(
                'Код для получения токена',
                f'Код для получения JWT токена: {code}',
                'yamdb@gmail.com',
                [user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
