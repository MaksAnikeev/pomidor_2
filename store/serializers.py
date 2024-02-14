from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelationship


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

class BookSerializer(ModelSerializer):
    # count_likes = serializers.SerializerMethodField()
    annotate_likes = serializers.IntegerField(read_only=True)
    rate = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='', read_only=True)
    reader_fio = UserSerializer(many=True, source='reader', read_only=True)

    class Meta:
        model = Book
        fields = ["id", "name", "price", "author_name",
                  "annotate_likes", "rate", 'owner_name', "reader_fio", 'rating']

    # def get_count_likes(self, instance):
    #     return UserBookRelationship.objects.filter(book=instance, like=True).count()


class UserBookRelationshipSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelationship
        fields = ["book", "like", "in_bookmarks", "rate"]

