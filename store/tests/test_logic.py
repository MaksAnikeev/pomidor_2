from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
import pytest

from store.logic import calculate_rating
from store.models import Book, UserBookRelationship
from rest_framework.test import APITestCase



class RatingTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user_1', first_name='Ivan', last_name='Petrov')
        self.user_2 = User.objects.create(username='user_2', first_name='Ivan', last_name='Sidorov')
        self.user_3 = User.objects.create(username='user_3', first_name='Pavel', last_name='Pack')

        self.book_1 = Book.objects.create(name='Тест_1', price=25, author_name="Maks")

        UserBookRelationship.objects.create(user=self.user_1, book=self.book_1, like=True, rate=5)
        UserBookRelationship.objects.create(user=self.user_2, book=self.book_1, like=True, rate=5)
        UserBookRelationship.objects.create(user=self.user_3, book=self.book_1, like=True, rate=4)



    def test_ok(self):
        calculate_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))


'для подготовки по pytest'
# class UserTestCase(TestCase):
#     def setUp(self):
#         self.user_1 = User.objects.create(username='user_1', first_name='Ivan', last_name='Petrov')
#         self.user_2 = User.objects.create(username='user_2', first_name='Ivan', last_name='Sidorov')
#         self.user_3 = User.objects.create(username='user_3', first_name='Pavel', last_name='Pack')
#
#
#     def test_user2(self):
#         users_in_db = list(User.objects.all())
#         users_for_check = [self.user_1, self.user_2, self.user_3]
#         assert users_for_check == users_in_db, 'объекты не созданы'
#
#
#     def test_user3(self):
#         users_in_db = list(User.objects.all())
#         users_for_check = [self.user_1, self.user_2, self.user_3]
#         assert users_for_check == users_in_db, 'объекты не созданы'
#
#         self.user_1 = User.objects.get(username='user_2')
#         last_name = self.user_1.last_name
#         assert 'Sidorov' == last_name


'для подготовки по pytest'
# @pytest.fixture
# def clients():
#     user_1 = User.objects.create(username='user_1', first_name='Ivan', last_name='Petrov')
#     user_2 = User.objects.create(username='user_2', first_name='Ivan', last_name='Sidorov')
#     user_3 = User.objects.create(username='user_3', first_name='Pavel', last_name='Pack')
#     return [user_1, user_2, user_3]
#
#
# @pytest.mark.django_db
# def test_user4(clients):
#     users_in_db = list(User.objects.all())
#     users_for_check = clients
#     assert users_for_check == users_in_db, 'объекты не созданы'
#
# @pytest.mark.django_db
# def test_user5(clients):
#     user_1 = User.objects.get(username='user_1')
#     last_name = user_1.last_name
#     assert clients[0].last_name == last_name

'для подготовки по pytest'
# @pytest.mark.django_db
# @pytest.mark.parametrize('expected_exception, model',
#                          [(ObjectDoesNotExist, Book),
#                           (ObjectDoesNotExist, UserBookRelationship)])
# def test_noexist_object_error(expected_exception, model, clients):
#     user_1, user_2, user_3 = clients
#     book_1 = Book.objects.create(name='Тест_1', price=25, author_name="Maks")
#     userbook_1 = UserBookRelationship.objects.create(user=user_1, book=book_1, like=True, rate=5)
#     UserBookRelationship.objects.create(user=user_2, book=book_1, like=True, rate=5)
#     userbooks = UserBookRelationship.objects.all()
#     assert len(userbooks) == 2, 'объекты не созданы'
#
#     if model == Book:
#         assert model.objects.get(name='Тест_1') == book_1
#     if model == UserBookRelationship:
#         assert model.objects.get(id=userbook_1.id) == userbook_1
#
#     with pytest.raises(expected_exception):
#         model.objects.get(id=10)
