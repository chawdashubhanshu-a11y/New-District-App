import uuid

from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CONSUMED = "CONSUMED", "Consumed"

    ticket_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings"
    )
    event = models.ForeignKey(
        "events.Event", on_delete=models.PROTECT, related_name="bookings"
    )
    slot = models.ForeignKey(
        "events.Slot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.title} - {self.ticket_id}"