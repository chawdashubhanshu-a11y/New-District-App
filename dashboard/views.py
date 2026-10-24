from django.shortcuts import render
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import organization_required
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