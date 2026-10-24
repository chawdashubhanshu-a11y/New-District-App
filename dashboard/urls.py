from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="org_dashboard"),
    path("events/new/", views.event_create, name="org_event_create"),
    path("events/<int:pk>/", views.event_manage, name="org_event_manage"),
    path("bookings/", views.bookings_list, name="org_bookings"),
    path(
        "bookings/<uuid:ticket_id>/consume/",
        views.mark_consumed,
        name="org_mark_consumed",
    ),
    path("analytics/", views.analytics, name="org_analytics"),
]