from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import TopUpForm
from .models import Transaction, Wallet


@login_required
def wallet_home(request):
    wallet = request.user.wallet
    transactions = wallet.transactions.select_related("booking__event")
    return render(
        request, "wallet/wallet.html", {"wallet": wallet, "transactions": transactions}
    )


@login_required
def add_money(request):
    if request.method == "POST":
        form = TopUpForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(user=request.user)
                wallet.balance += amount
                wallet.save(update_fields=["balance"])
                Transaction.objects.create(
                    wallet=wallet, type=Transaction.Type.TOPUP, amount=amount
                )
            messages.success(request, f"Added ₹{amount} to your wallet.")
            return redirect("wallet")
    else:
        form = TopUpForm()
    return render(request, "wallet/add_money.html", {"form": form})