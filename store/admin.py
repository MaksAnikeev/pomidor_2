from django.contrib import admin

from store.models import Book, UserBookRelationship


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display=["id", "name", "price"]


@admin.register(UserBookRelationship)
class UserBookRelationshipAdmin(admin.ModelAdmin):
    pass
