from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def post_login(request):
    if request.user.groups.filter(name="Organization").exists():
        return redirect("org_dashboard")
    return redirect("event_list")

from .forms import CustomerSignUpForm


def signup(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name="Customer"))
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = CustomerSignUpForm()
    return render(request, "registration/signup.html", {"form": form})