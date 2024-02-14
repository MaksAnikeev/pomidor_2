from django.db.models.aggregates import Count, Avg
from django.db.models.expressions import Case, When
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from store.models import Book, UserBookRelationship
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationshipSerializer


class BookView(ModelViewSet):
    queryset = Book.objects.all()\
        .annotate(annotate_likes=Count(Case(When(users__like=True, then=1))), rate=Avg('users__rate'))\
        .select_related('owner').prefetch_related('reader')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    order_fields = '__all__'

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.validated_data['owner'] = self.request.user
            serializer.save()


class UserBookRelationshipView(UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelationship.objects.all()
    serializer_class = UserBookRelationshipSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelationship.objects.get_or_create(user=self.request.user,
                                                            book_id=self.kwargs['book'])
        return obj


def oauth(request):
    return render(request, 'oauth.html')
