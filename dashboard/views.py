from django.contrib import messages
from django.db import transaction
from django.db.models import CharField, Count, Q, Sum
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.permissions import organization_required
from bookings.models import Booking
from events.models import Event

from .forms import EventForm, SlotForm


@organization_required
def dashboard(request):
    org = request.user.organization_profile
    events = org.events.annotate(booking_count=Count("bookings")).order_by("-created_at")
    return render(request, "dashboard/dashboard.html", {"org": org, "events": events})


@organization_required
def event_create(request):
    org = request.user.organization_profile
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organization = org
            event.save()
            messages.success(request, "Event created.")
            return redirect("org_event_manage", pk=event.pk)
    else:
        form = EventForm()
    return render(request, "dashboard/event_form.html", {"form": form})


@organization_required
def event_manage(request, pk):
    org = request.user.organization_profile
    event = get_object_or_404(Event, pk=pk, organization=org)
    slot_form = None
    if event.kind == Event.Kind.SLOT:
        if request.method == "POST":
            slot_form = SlotForm(request.POST)
            if slot_form.is_valid():
                slot = slot_form.save(commit=False)
                slot.event = event
                slot.save()
                messages.success(request, "Slot added.")
                return redirect("org_event_manage", pk=event.pk)
        else:
            slot_form = SlotForm()
    return render(
        request,
        "dashboard/event_manage.html",
        {"event": event, "slots": event.slots.all(), "slot_form": slot_form},
    )


@organization_required
def bookings_list(request):
    org = request.user.organization_profile
    bookings = Booking.objects.filter(event__organization=org).select_related(
        "user", "event", "slot"
    )

    status = request.GET.get("status", "")
    event_id = request.GET.get("event", "")
    q = request.GET.get("q", "").strip()

    if status in Booking.Status.values:
        bookings = bookings.filter(status=status)
    if event_id.isdigit():
        bookings = bookings.filter(event_id=int(event_id))
    if q:
        bookings = bookings.annotate(tid=Cast("ticket_id", CharField())).filter(
            tid__icontains=q
        )

    return render(
        request,
        "dashboard/bookings.html",
        {
            "bookings": bookings[:200],
            "events": org.events.all(),
            "status": status,
            "event_id": event_id,
            "q": q,
        },
    )


@organization_required
@require_POST
def mark_consumed(request, ticket_id):
    org = request.user.organization_profile
    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(of=("self",)),
            ticket_id=ticket_id,
            event__organization=org,
        )
        if booking.status == Booking.Status.CONSUMED:
            messages.info(request, "That ticket was already marked as consumed.")
        else:
            booking.status = Booking.Status.CONSUMED
            booking.consumed_at = timezone.now()
            booking.save(update_fields=["status", "consumed_at"])
            messages.success(request, f"Ticket {booking.ticket_id} marked as consumed.")
    return redirect("org_bookings")


@organization_required
def analytics(request):
    org = request.user.organization_profile
    totals = Booking.objects.filter(event__organization=org).aggregate(
        tickets=Count("id"),
        revenue=Sum("price_paid"),
        consumed=Count("id", filter=Q(status=Booking.Status.CONSUMED)),
    )
    tickets = totals["tickets"]
    consumed = totals["consumed"]
    summary = {
        "tickets": tickets,
        "revenue": totals["revenue"] or 0,
        "consumed": consumed,
        "pending": tickets - consumed,
        "consumed_pct": round(consumed * 100 / tickets) if tickets else 0,
    }

    per_event = org.events.annotate(
        tickets=Count("bookings"),
        revenue=Sum("bookings__price_paid"),
        consumed=Count("bookings", filter=Q(bookings__status=Booking.Status.CONSUMED)),
    ).order_by("-revenue", "-created_at")

    return render(
        request,
        "dashboard/analytics.html",
        {"org": org, "summary": summary, "per_event": per_event},
    )