from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("bookings/", include("bookings.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("wallet/", include("wallet.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("events.urls")),
]