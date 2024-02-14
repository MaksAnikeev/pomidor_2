from django.db.models import Avg

from store.models import UserBookRelationship


def calculate_rating(book):
    rating = UserBookRelationship.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating = rating
    book.save()
