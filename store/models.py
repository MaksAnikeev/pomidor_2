from django.contrib.auth.models import User
from django.db import models




class Book(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=7,
        decimal_places=2
    )
    author_name = models.CharField(
        verbose_name='Автор',
        max_length=255,
        default=''
    )
    is_published = models.BooleanField(
        verbose_name='Опубликована ли книга',
        default=False,
    )
    owner = models.ForeignKey(
        User,
        verbose_name="владелец книги",
        on_delete=models.SET_NULL,
        null=True,
        related_name="books_owner"
    )
    reader = models.ManyToManyField(
        User,
        through='UserBookRelationship',
        related_name="books_reactions"
    )
    rating = models.DecimalField(
        verbose_name='рейтинг книги',
        max_digits=3,
        decimal_places=2,
        default=None,
        null=True
    )

    def __str__(self):
        return f'id {self.id}: {self.name}'


class UserBookRelationship(models.Model):
    RATE_CHOISE = (
        (1, "OK"),
        (2, "Good"),
        (3, "Super"),
        (4, "Amazing"),
        (5, "Incredible"),
    )

    user = models.ForeignKey(
        User,
        verbose_name="пользователь",
        on_delete=models.CASCADE,
        related_name="reactions"
    )
    book = models.ForeignKey(
        Book,
        verbose_name="книга",
        on_delete=models.CASCADE,
        related_name="users"
    )
    like = models.BooleanField(
        verbose_name="лайк",
        default=False
    )
    in_bookmarks = models.BooleanField(
        verbose_name="закладки",
        default=False
    )
    rate = models.PositiveSmallIntegerField(
        verbose_name="рейтинг",
        choices=RATE_CHOISE,
        null=True
    )

    def __str__(self):
        return f'{self.user.username}: {self.book.name} RATE {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import calculate_rating
        super().save(*args, **kwargs)
        calculate_rating(self.book)
