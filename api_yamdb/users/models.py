from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models


def username_not_me(username):
    if username == 'me':
        raise ValidationError('username не может быть "me"')


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None,
                    role='user', bio=''):
        """ Создает и возвращает пользователя с email и именем. """

        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),)

        code = default_token_generator.make_token(user)
        if password is None:
            password = code

        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.role = role
        user.bio = bio
        user.save()
        send_mail(
            'Код для получения токена',
            f'Код для получения JWT токена: {code}',
            'yamdb@gmail.com',
            [email],
            fail_silently=False,
        )
        return user

    def create_superuser(self, username, email, password,
                         role='admin', bio=''):
        """ Создает и возвращает пользователя с привилегиями суперадмина."""

        user = self.create_user(username, email, password, role, bio)
        user.is_superuser = True
        user.is_staff = True
        user.role = role
        user.bio = bio
        user.save()

        return user


class User(AbstractUser):
    "Пользовательская модель юзера"
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, username_not_me],
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254,

    )
    bio = models.TextField(
        verbose_name='Био',
        blank=True,
    )

    class RoleChoice(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        verbose_name='Роль',
        choices=RoleChoice.choices,
        default=RoleChoice.USER,
        max_length=10
    )

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta(AbstractUser.Meta):
        ordering = ('-id',)
