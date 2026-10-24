from django.db import transaction
from django.utils import timezone

from events.models import Event, Slot
from wallet.models import Transaction, Wallet

from .models import Booking


class BookingError(Exception):
    pass


def book_event(*, user, event_id, slot_id=None):
    with transaction.atomic():
        # Lock order is always wallet, then event/slot, to avoid deadlocks
        wallet = Wallet.objects.select_for_update().get(user=user)

        try:
            if slot_id is None:
                event = Event.objects.select_for_update().get(
                    pk=event_id, is_active=True
                )
            else:
                event = Event.objects.get(pk=event_id, is_active=True)
        except Event.DoesNotExist:
            raise BookingError("This event is not available.")

        slot = None
        if event.kind == Event.Kind.TICKET:
            if event.total_tickets is None or event.tickets_sold >= event.total_tickets:
                raise BookingError("Sorry, this event is sold out.")
            if event.starts_at and event.starts_at <= timezone.now():
                raise BookingError("This event has already started.")
        else:
            if slot_id is None:
                raise BookingError("Please choose a slot.")
            try:
                slot = Slot.objects.select_for_update().get(pk=slot_id, event=event)
            except Slot.DoesNotExist:
                raise BookingError("That slot does not exist.")
            if slot.starts_at <= timezone.now():
                raise BookingError("That slot has already started.")
            if slot.booked_count >= slot.capacity:
                raise BookingError("That slot is full.")

        if wallet.balance < event.price:
            raise BookingError("Insufficient wallet balance. Please add money.")

        wallet.balance -= event.price
        wallet.save(update_fields=["balance"])

        if slot:
            slot.booked_count += 1
            slot.save(update_fields=["booked_count"])
        else:
            event.tickets_sold += 1
            event.save(update_fields=["tickets_sold"])

        booking = Booking.objects.create(
            user=user, event=event, slot=slot, price_paid=event.price
        )
        Transaction.objects.create(
            wallet=wallet,
            type=Transaction.Type.PURCHASE,
            amount=event.price,
            booking=booking,
        )
        return booking