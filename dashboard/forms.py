from django import forms

from events.models import Event, Slot


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(**kwargs)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "venue",
            "kind",
            "price",
            "starts_at",
            "total_tickets",
        ]
        widgets = {"starts_at": DateTimeLocalInput()}
        help_texts = {
            "starts_at": "Ticket events only.",
            "total_tickets": "Ticket events only.",
        }

    def clean(self):
        data = super().clean()
        kind = data.get("kind")
        if kind == Event.Kind.TICKET:
            if not data.get("starts_at"):
                self.add_error("starts_at", "Required for ticket events.")
            if not data.get("total_tickets"):
                self.add_error("total_tickets", "Required for ticket events.")
        elif kind == Event.Kind.SLOT:
            data["starts_at"] = None
            data["total_tickets"] = None
        return data


class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ["starts_at", "ends_at", "capacity"]
        widgets = {
            "starts_at": DateTimeLocalInput(),
            "ends_at": DateTimeLocalInput(),
        }

    def clean(self):
        data = super().clean()
        start, end = data.get("starts_at"), data.get("ends_at")
        if start and end and end <= start:
            self.add_error("ends_at", "End time must be after the start time.")
        if data.get("capacity") is not None and data["capacity"] < 1:
            self.add_error("capacity", "Capacity must be at least 1.")
        return data