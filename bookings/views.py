from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Booking
from .services import BookingError, book_event


@login_required
@require_POST
def book(request, event_id):
    slot_id = request.POST.get("slot_id") or None
    try:
        if slot_id is not None:
            slot_id = int(slot_id)
        booking = book_event(user=request.user, event_id=event_id, slot_id=slot_id)
    except (BookingError, ValueError) as exc:
        messages.error(request, str(exc) if isinstance(exc, BookingError) else "Invalid slot.")
        return redirect("event_detail", pk=event_id)
    messages.success(request, f"Booked! Ticket ID: {booking.ticket_id}")
    return redirect("my_bookings")


@login_required
def my_bookings(request):
    bookings = request.user.bookings.select_related("event", "slot")
    return render(
        request,
        "bookings/my_bookings.html",
        {
            "active": [b for b in bookings if b.status == Booking.Status.ACTIVE],
            "past": [b for b in bookings if b.status == Booking.Status.CONSUMED],
        },
    )