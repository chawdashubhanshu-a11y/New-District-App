from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")