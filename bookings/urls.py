from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_bookings, name="my_bookings"),
    path("book/<int:event_id>/", views.book, name="book"),
]