from django.contrib.auth.models import User
from django.db import connection
from django.db.models.aggregates import Count, Avg
from django.db.models.expressions import Case, When
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json
from django.test.utils import CaptureQueriesContext

from store.models import Book, UserBookRelationship
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.book_1 = Book.objects.create(name='Путешествия',
                                          price=25,
                                          author_name="Макс",
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Встреча',
                                          price=25,
                                          author_name="Катя")
        self.book_3 = Book.objects.create(name='Макс на коне',
                                          price=55,
                                          author_name="Аникеев")
        UserBookRelationship.objects.create(user=self.user, book=self.book_2, like=True, rate=4)

    def test_get(self):
        url = reverse('booking-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(annotate_likes=Count(Case(When(users__like=True, then=1))))\
            .annotate(rate=Avg('users__rate')).order_by('id')
        serialized_data = BookSerializer(books,
                                         many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serialized_data.data, response.data)
        self.assertEqual(serialized_data.data[1]['annotate_likes'], 1)
        self.assertEqual(serialized_data.data[1]['rate'], '4.00')

    def test_quantity_queries(self):
        url = reverse('booking-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))


    def test_get_filter(self):
        url = reverse('booking-list')
        response = self.client.get(url, data={'price': '25'})

        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id])\
            .annotate(annotate_likes=Count(Case(When(users__like=True, then=1))))\
            .annotate(rate=Avg('users__rate')).order_by('-id')
        serialized_data = BookSerializer(books,
                                         many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serialized_data.data, response.data)

    def test_get_search(self):
        url = reverse('booking-list')
        response = self.client.get(url, data={'search': 'Макс'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id])\
            .annotate(annotate_likes=Count(Case(When(users__like=True, then=1))))\
            .annotate(rate=Avg('users__rate'))
        serialized_data = BookSerializer(books,
                                         many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serialized_data.data, response.data)

    def test_get_ordering(self):
        url = reverse('booking-list')
        response = self.client.get(url, data={'ordering': 'price'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id, self.book_3.id]) \
            .annotate(annotate_likes=Count(Case(When(users__like=True, then=1)))) \
            .annotate(rate=Avg('users__rate')).order_by('price', 'id')
        serialized_data = BookSerializer(books,
                                         many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serialized_data.data, response.data)

    def test_created(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('booking-list')
        data = {
            "name": "Python3",
            "price": "22.00",
            "author_name": "Maximus2"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('booking-detail', args=[self.book_1.id])
        data = {
            "name": "Путешествия",
            "price": "220.00",
            "author_name": "Макс"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(float(220), self.book_1.price)

    def test_delete(self):
        quantity_objects = Book.objects.all().count()
        url = reverse('booking-list')
        data = {
            "name": "Python3",
            "price": "22.00",
            "author_name": "Maximus2"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(quantity_objects + 1, Book.objects.all().count())

        url_for_delete = reverse('booking-detail',
                                 args=[response.json()['id']])
        response = self.client.delete(url_for_delete)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(quantity_objects, Book.objects.all().count())

    def test_get_object(self):
        url = reverse('booking-detail', args=[self.book_1.id])
        response = self.client.get(url)
        self.assertEqual('25.00', response.json()['price'])

    def test_update_not_owner(self):
        url = reverse('booking-detail', args=[self.book_1.id])
        data = {
            "name": "Путешествия",
            "price": "220.00",
            "author_name": "Макс"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(float(25), self.book_1.price)

    def test_delete_not_owner(self):
        quantity_objects = Book.objects.all().count()
        url = reverse('booking-list')
        data = {
            "name": "Python3",
            "price": "22.00",
            "author_name": "Maximus2"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(quantity_objects + 1, Book.objects.all().count())

        url_for_delete = reverse('booking-detail', args=[Book.objects.last().id])
        self.client.force_login(self.user2)
        response = self.client.delete(url_for_delete)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(quantity_objects + 1, Book.objects.all().count())
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_update_not_owner_but_staff(self):
        self.user3 = User.objects.create(username='test_user3',
                                         is_staff=True)
        url = reverse('booking-detail', args=[self.book_1.id])
        data = {
            "name": "Путешествия",
            "price": "220.00",
            "author_name": "Макс"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user3)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(float(220), self.book_1.price)

    def test_update_published(self):
        self.book_4 = Book.objects.create(name='Опубликованная',
                                          price=525,
                                          author_name="Тест",
                                          is_published=True,
                                          owner=self.user)
        url = reverse('booking-detail', args=[self.book_4.id])
        data = {
            "name": "Опубликованная",
            "price": "220.00",
            "author_name": "Тест"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(float(525), self.book_4.price)

    def test_update_not_published(self):
        self.book_4 = Book.objects.create(name='Опубликованная',
                                          price=525,
                                          author_name="Тест",
                                          is_published=False,
                                          owner=self.user)
        url = reverse('booking-detail', args=[self.book_4.id])
        data = {
            "name": "Опубликованная",
            "price": "220.00",
            "author_name": "Тест"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_4.refresh_from_db()
        self.assertEqual(float(220), self.book_4.price)


class UserBookRelationshipApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.book_1 = Book.objects.create(name='Путешествия',
                                          price=25,
                                          author_name="Макс",
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Встреча',
                                          price=55,
                                          author_name="Катя")

    def test_like(self):
        url = reverse('reaction-detail', args=[self.book_2.id])

        data = {
            "like": True,
        }

        self.client.force_login(self.user)
        json_data = json.dumps(data)
        response = self.client.patch(url,
                                   data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation = UserBookRelationship.objects.get(user=self.user,
                                                    book=self.book_2)
        self.assertTrue(relation.like)

    def test_rate(self):
        url = reverse('reaction-detail', args=[self.book_2.id])

        data = {
            "rate": 3,
        }
        self.client.force_login(self.user)
        json_data = json.dumps(data)
        response = self.client.patch(url,
                                   data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        relation = UserBookRelationship.objects.get(user=self.user,
                                                    book=self.book_2)
        self.assertEqual(3, relation.rate)
