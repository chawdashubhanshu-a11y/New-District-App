from django import forms


class TopUpForm(forms.Form):
    amount = forms.DecimalField(
        min_value=1, max_value=100000, max_digits=10, decimal_places=2
    )