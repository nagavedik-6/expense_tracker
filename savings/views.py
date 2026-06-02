from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

from .models import SavingsGoal
from .forms import SavingsGoalForm, ContributionForm


@login_required
def savings_list(request):
    """List all savings goals."""
    goals = SavingsGoal.objects.filter(user=request.user)
    currency_symbol = request.user.profile.currency_symbol if hasattr(request.user, 'profile') else '₹'
    return render(request, 'savings/savings_list.html', {
        'goals': goals,
        'currency_symbol': currency_symbol,
    })


@login_required
def savings_create(request):
    """Create a savings goal."""
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Savings goal created!')
            return redirect('savings_list')
    else:
        form = SavingsGoalForm()
    return render(request, 'savings/savings_form.html', {
        'form': form, 'title': 'Create Savings Goal', 'btn_text': 'Create Goal'
    })


@login_required
def savings_update(request, pk):
    """Update a savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Savings goal updated!')
            return redirect('savings_list')
    else:
        form = SavingsGoalForm(instance=goal)
    return render(request, 'savings/savings_form.html', {
        'form': form, 'title': 'Edit Savings Goal', 'btn_text': 'Update Goal'
    })


@login_required
def savings_delete(request, pk):
    """Delete a savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Savings goal deleted!')
        return redirect('savings_list')
    return render(request, 'savings/savings_confirm_delete.html', {'goal': goal})


@login_required
def savings_contribute(request, pk):
    """Add contribution to a savings goal."""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            goal.current_amount += amount
            goal.save()
            messages.success(request, f'Added ₹{amount} to "{goal.goal_name}"!')
            if goal.is_completed:
                from notifications.models import Notification
                Notification.objects.create(
                    user=request.user,
                    message=f'Congratulations! You\'ve reached your savings goal "{goal.goal_name}"! 🎉',
                    notification_type='savings_complete',
                    link='/savings/'
                )
            return redirect('savings_list')
    else:
        form = ContributionForm()
    currency_symbol = request.user.profile.currency_symbol if hasattr(request.user, 'profile') else '₹'
    return render(request, 'savings/savings_contribute.html', {
        'form': form, 'goal': goal, 'currency_symbol': currency_symbol,
    })
