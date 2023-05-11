from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        verbose_name='Название',
        related_name='reviews')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор')
    text = models.TextField(verbose_name='Текст')
    score = models.IntegerField(
        choices=list(zip(range(1, 11), range(1, 11))))
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'], name='unic_rev'), ]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']


class Category(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Категория')
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='Slug категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категория'
        ordering = ('-id',)


class Genre(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Жанр')
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='Slug жанра')

    def __str__(self):
        self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанр'
        ordering = ('-id',)


class Title(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выхода')
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведение'
        ordering = ('-id',)


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    def __str__(self):
        return f'{self.title} {self.genre}'

    class Meta:
        verbose_name = 'Связка категоря-жанр'
        verbose_name_plural = 'Связка категоря-жанр'
