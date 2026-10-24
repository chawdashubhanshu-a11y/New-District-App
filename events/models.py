from django.db import models
from django.db.models import F, Q


class Event(models.Model):
    class Kind(models.TextChoices):
        SLOT = "SLOT", "Slot-based"
        TICKET = "TICKET", "Ticket-based"

    organization = models.ForeignKey(
        "accounts.OrganizationProfile",
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=200, blank=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    starts_at = models.DateTimeField(null=True, blank=True)
    total_tickets = models.PositiveIntegerField(null=True, blank=True)
    tickets_sold = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0), name="event_price_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(total_tickets__isnull=True)
                | Q(tickets_sold__lte=F("total_tickets")),
                name="event_not_oversold",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def tickets_left(self):
        if self.total_tickets is None:
            return None
        return self.total_tickets - self.tickets_sold


class Slot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="slots")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    booked_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["starts_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(booked_count__lte=F("capacity")),
                name="slot_not_overbooked",
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")),
                name="slot_ends_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.event.title} ({self.starts_at:%d %b %H:%M})"