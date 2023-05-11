from api.utils import ReviewDefault, TitleDefault
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        default=ReviewDefault(),
        write_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.PrimaryKeyRelatedField(
        queryset=Title.objects.all(),
        default=TitleDefault(),
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author'],
                message='Нельзя добавить больше одного '
                        'отзыва на произведение')]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('score')).get('score__avg')


class TitleGetSerializer(TitleSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')

    def create(self, validated_data):
        """Создает и возвращает пользователя"""
        return User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
        )


class TokenObtainSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(serializers.Serializer, self).__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField(
            max_length=150,
            validators=(UnicodeUsernameValidator,))
        self.fields['confirmation_code'] = serializers.CharField(max_length=50)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        try:
            self.user = User.objects.get(
                username=username,
            )
        except User.DoesNotExist:
            return {'error': 'Пользователь не найден.'}
        if not self.user.is_active:
            raise serializers.ValidationError(
                'Аккаунт заблокирован'
            )
        if default_token_generator.check_token(self.user, confirmation_code):
            refresh = self.get_token(self.user)
            token = refresh.access_token
            update_last_login(None, self.user)

            return {"token": str(token)}
        raise serializers.ValidationError(
            'Неверный confirmation_code'
        )
