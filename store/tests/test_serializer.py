from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.db.models.aggregates import Avg
from django.test import TestCase

from store.models import Book, UserBookRelationship
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='user_1', first_name='Ivan', last_name='Petrov')
        user_2 = User.objects.create(username='user_2', first_name='Ivan', last_name='Sidorov')
        user_3 = User.objects.create(username='user_3', first_name='Pavel', last_name='Pack')

        book_1 = Book.objects.create(name='Тест_1', price=25, author_name="Maks")
        book_2 = Book.objects.create(name='Тест_2', price=55, author_name="Maks2")


        UserBookRelationship.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelationship.objects.create(user=user_2, book=book_1, like=True, rate=5)
        UserBookRelationship.objects.create(user=user_3, book=book_1, like=True, rate=4)




        UserBookRelationship.objects.create(user=user_1, book=book_2, like=True, rate=4)
        UserBookRelationship.objects.create(user=user_2, book=book_2, like=True, rate=3)
        UserBookRelationship.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(annotate_likes=Count(Case(When(users__like=True, then=1))))\
            .annotate(rate=Avg('users__rate')).order_by('id')
        serialized_data = BookSerializer(books, many=True).data

        expected_data = [
            {
                "id": book_1.id,
                "name": 'Тест_1',
                "price": '25.00',
                "author_name": "Maks",
                "annotate_likes": 3,
                "rate": '4.67',
                "owner_name": '',
                'rating': '4.67',
                'reader_fio': [
                    {
                        "first_name": "Ivan",
                        "last_name": "Petrov"
                    },
                    {
                        "first_name": "Ivan",
                        "last_name": "Sidorov"
                    },
                    {
                        "first_name": "Pavel",
                        "last_name": "Pack"
                    }
                ]

            },
            {
                "id": book_2.id,
                "name": 'Тест_2',
                "price": '55.00',
                "author_name": "Maks2",
                "annotate_likes": 2,
                "rate": '3.50',
                "owner_name": '',
                'rating': '3.50',
                'reader_fio': [
                    {
                        "first_name": "Ivan",
                        "last_name": "Petrov"
                    },
                    {
                        "first_name": "Ivan",
                        "last_name": "Sidorov"
                    },
                    {
                        "first_name": "Pavel",
                        "last_name": "Pack"
                    }
                ]
            }
        ]
        self.assertEqual(expected_data, serialized_data)

    def test_save(self):
        user_1 = User.objects.create(username='user_1', first_name='Ivan', last_name='Petrov')
        user_2 = User.objects.create(username='user_2', first_name='Ivan', last_name='Sidorov')
        user_3 = User.objects.create(username='user_3', first_name='Pavel', last_name='Pack')
        user_4 = User.objects.create(username='user_4', first_name='Pavel2', last_name='Pack2')

        book_1 = Book.objects.create(name='Тест_1', price=25, author_name="Maks")

        UserBookRelationship.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelationship.objects.create(user=user_2, book=book_1, like=True, rate=4)
        user_book_3 = UserBookRelationship.objects.create(user=user_3, book=book_1, like=True)

        serialized_data = BookSerializer(book_1).data
        self.assertEqual('4.50', serialized_data['rating'])

        UserBookRelationship.objects.create(user=user_4, book=book_1, like=True, rate=1)
        serialized_data = BookSerializer(book_1).data
        self.assertEqual('3.33', serialized_data['rating'])

        user_book_3.rate = 5
        user_book_3.save()
        serialized_data = BookSerializer(book_1).data
        self.assertEqual('3.75', serialized_data['rating'])


