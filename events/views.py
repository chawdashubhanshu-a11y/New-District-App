from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Event


@login_required
def event_list(request):
    events = Event.objects.filter(is_active=True).select_related("organization")
    return render(request, "events/event_list.html", {"events": events})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related("organization"), pk=pk, is_active=True
    )
    slots = None
    if event.kind == Event.Kind.SLOT:
        slots = event.slots.filter(
            starts_at__gte=timezone.now(), booked_count__lt=F("capacity")
        )
    return render(request, "events/event_detail.html", {"event": event, "slots": slots})