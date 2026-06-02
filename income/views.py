from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

from .models import Income
from .forms import IncomeForm


@login_required
def income_list(request):
    """List all income records."""
    incomes = Income.objects.filter(user=request.user)

    # Filter by source
    source = request.GET.get('source')
    if source:
        incomes = incomes.filter(source=source)

    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)

    total = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    currency_symbol = request.user.profile.currency_symbol if hasattr(request.user, 'profile') else '₹'

    return render(request, 'income/income_list.html', {
        'incomes': incomes,
        'total': total,
        'currency_symbol': currency_symbol,
        'source_choices': Income.SOURCE_CHOICES,
    })


@login_required
def income_create(request):
    """Add new income."""
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm()
    return render(request, 'income/income_form.html', {
        'form': form, 'title': 'Add Income', 'btn_text': 'Add Income'
    })


@login_required
def income_update(request, pk):
    """Update income."""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_form.html', {
        'form': form, 'title': 'Edit Income', 'btn_text': 'Update Income'
    })


@login_required
def income_delete(request, pk):
    """Delete income."""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income deleted successfully!')
        return redirect('income_list')
    return render(request, 'income/income_confirm_delete.html', {'income': income})
