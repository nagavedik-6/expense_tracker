from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Budget
from .forms import BudgetForm


@login_required
def budget_list(request):
    """List budgets with current status."""
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    budgets = Budget.objects.filter(user=request.user, month=month, year=year)
    currency_symbol = request.user.profile.currency_symbol if hasattr(request.user, 'profile') else '₹'

    return render(request, 'budgets/budget_list.html', {
        'budgets': budgets,
        'current_month': month,
        'current_year': year,
        'currency_symbol': currency_symbol,
        'month_choices': Budget.MONTH_CHOICES,
    })


@login_required
def budget_create(request):
    """Create a new budget."""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        today = timezone.now().date()
        form = BudgetForm(user=request.user, initial={
            'month': today.month, 'year': today.year
        })
    return render(request, 'budgets/budget_form.html', {
        'form': form, 'title': 'Create Budget', 'btn_text': 'Create Budget'
    })


@login_required
def budget_update(request, pk):
    """Update a budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, 'budgets/budget_form.html', {
        'form': form, 'title': 'Edit Budget', 'btn_text': 'Update Budget'
    })


@login_required
def budget_delete(request, pk):
    """Delete a budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})
