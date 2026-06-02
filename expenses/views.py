from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal

from .models import Expense, Category, RecurringExpense
from .forms import ExpenseForm, CategoryForm, RecurringExpenseForm, ExpenseFilterForm
from income.models import Income
from budgets.models import Budget
from savings.models import SavingsGoal
from notifications.models import Notification


@login_required
def dashboard_view(request):
    """Main dashboard with summary cards and chart data."""
    user = request.user
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Summary calculations
    total_income = Income.objects.filter(user=user).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    total_expenses = Expense.objects.filter(user=user).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    balance = total_income - total_expenses

    monthly_income = Income.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    monthly_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    monthly_savings = monthly_income - monthly_expenses

    today_expenses = Expense.objects.filter(
        user=user, date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Budget status
    budgets = Budget.objects.filter(user=user, month=current_month, year=current_year)
    total_budget = budgets.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    budget_used = sum(b.spent_amount for b in budgets)
    budget_pct = round((budget_used / total_budget * 100), 1) if total_budget > 0 else 0

    # Recent transactions
    recent_expenses = Expense.objects.filter(user=user).select_related('category')[:5]
    recent_income = Income.objects.filter(user=user)[:5]

    # Chart data: Monthly trend (last 6 months)
    monthly_labels = []
    monthly_income_data = []
    monthly_expense_data = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=i * 30)
        m, y = d.month, d.year
        label = d.strftime('%b %Y')
        monthly_labels.append(label)
        inc = Income.objects.filter(user=user, date__month=m, date__year=y).aggregate(
            total=Sum('amount'))['total'] or 0
        exp = Expense.objects.filter(user=user, date__month=m, date__year=y).aggregate(
            total=Sum('amount'))['total'] or 0
        monthly_income_data.append(float(inc))
        monthly_expense_data.append(float(exp))

    # Chart data: Category-wise expense
    category_data = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    cat_labels = [c['category__name'] or 'Uncategorized' for c in category_data]
    cat_amounts = [float(c['total']) for c in category_data]

    # Savings goals progress
    savings_goals = SavingsGoal.objects.filter(user=user)[:5]

    # Savings growth (last 6 months)
    savings_labels = monthly_labels
    savings_data = []
    cumulative = 0
    for i in range(5, -1, -1):
        d = today - timedelta(days=i * 30)
        m, y = d.month, d.year
        inc = Income.objects.filter(user=user, date__month=m, date__year=y).aggregate(
            total=Sum('amount'))['total'] or 0
        exp = Expense.objects.filter(user=user, date__month=m, date__year=y).aggregate(
            total=Sum('amount'))['total'] or 0
        cumulative += float(inc) - float(exp)
        savings_data.append(max(cumulative, 0))

    # Check for budget alerts
    for budget in budgets:
        if budget.is_over_budget:
            existing = Notification.objects.filter(
                user=user, notification_type='budget_exceeded',
                message__contains=budget.name,
                created_at__month=current_month
            ).exists()
            if not existing:
                Notification.objects.create(
                    user=user,
                    message=f'Budget "{budget.name}" has been exceeded! Spent: ₹{budget.spent_amount} / ₹{budget.amount}',
                    notification_type='budget_exceeded',
                    link='/budgets/'
                )
        elif budget.is_near_limit:
            existing = Notification.objects.filter(
                user=user, notification_type='budget_alert',
                message__contains=budget.name,
                created_at__month=current_month
            ).exists()
            if not existing:
                Notification.objects.create(
                    user=user,
                    message=f'Budget "{budget.name}" is at {budget.percentage_used}% — approaching the limit!',
                    notification_type='budget_alert',
                    link='/budgets/'
                )

    currency_symbol = user.profile.currency_symbol if hasattr(user, 'profile') else '₹'

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'monthly_savings': monthly_savings,
        'today_expenses': today_expenses,
        'budget_pct': budget_pct,
        'total_budget': total_budget,
        'budget_used': budget_used,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'savings_goals': savings_goals,
        'currency_symbol': currency_symbol,
        # Chart data (JSON-safe)
        'monthly_labels': monthly_labels,
        'monthly_income_data': monthly_income_data,
        'monthly_expense_data': monthly_expense_data,
        'cat_labels': cat_labels,
        'cat_amounts': cat_amounts,
        'savings_labels': savings_labels,
        'savings_data': savings_data,
    }
    return render(request, 'dashboard.html', context)


# ─── EXPENSE CRUD ───────────────────────────────────────────────

@login_required
def expense_list(request):
    """List expenses with search, filter, sort."""
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    filter_form = ExpenseFilterForm(request.GET)

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        payment_method = filter_form.cleaned_data.get('payment_method')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        sort_by = filter_form.cleaned_data.get('sort_by')

        if search:
            expenses = expenses.filter(
                Q(title__icontains=search) | Q(description__icontains=search) |
                Q(notes__icontains=search)
            )
        if category:
            expenses = expenses.filter(category=category)
        if payment_method:
            expenses = expenses.filter(payment_method=payment_method)
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)
        if sort_by:
            expenses = expenses.order_by(sort_by)

    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    currency_symbol = request.user.profile.currency_symbol if hasattr(request.user, 'profile') else '₹'

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'filter_form': filter_form,
        'total': total,
        'currency_symbol': currency_symbol,
    })


@login_required
def expense_create(request):
    """Create a new expense."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expenses/expense_form.html', {
        'form': form, 'title': 'Add Expense', 'btn_text': 'Add Expense'
    })


@login_required
def expense_update(request, pk):
    """Update an expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'expenses/expense_form.html', {
        'form': form, 'title': 'Edit Expense', 'btn_text': 'Update Expense'
    })


@login_required
def expense_delete(request, pk):
    """Delete an expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def expense_detail(request, pk):
    """View expense details."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})


# ─── CATEGORY CRUD ──────────────────────────────────────────────

@login_required
def category_list(request):
    """List categories."""
    default_categories = Category.objects.filter(is_default=True)
    custom_categories = Category.objects.filter(user=request.user)
    return render(request, 'expenses/category_list.html', {
        'default_categories': default_categories,
        'custom_categories': custom_categories,
    })


@login_required
def category_create(request):
    """Create a custom category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/category_form.html', {
        'form': form, 'title': 'Add Category'
    })


@login_required
def category_update(request, pk):
    """Edit a custom category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'expenses/category_form.html', {
        'form': form, 'title': 'Edit Category'
    })


@login_required
def category_delete(request, pk):
    """Delete a custom category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted!')
        return redirect('category_list')
    return render(request, 'expenses/category_confirm_delete.html', {'category': category})


# ─── RECURRING EXPENSES ─────────────────────────────────────────

@login_required
def recurring_list(request):
    """List recurring expenses."""
    recurring = RecurringExpense.objects.filter(user=request.user)
    return render(request, 'expenses/recurring_list.html', {'recurring_expenses': recurring})


@login_required
def recurring_create(request):
    """Create a recurring expense."""
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.save()
            messages.success(request, 'Recurring expense created!')
            return redirect('recurring_list')
    else:
        form = RecurringExpenseForm(user=request.user)
    return render(request, 'expenses/recurring_form.html', {
        'form': form, 'title': 'Add Recurring Expense'
    })


@login_required
def recurring_delete(request, pk):
    """Delete a recurring expense."""
    recurring = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    if request.method == 'POST':
        recurring.delete()
        messages.success(request, 'Recurring expense deleted!')
        return redirect('recurring_list')
    return render(request, 'expenses/recurring_confirm_delete.html', {'recurring': recurring})


@login_required
def recurring_toggle(request, pk):
    """Toggle active state of a recurring expense."""
    recurring = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    recurring.is_active = not recurring.is_active
    recurring.save()
    state = 'activated' if recurring.is_active else 'paused'
    messages.success(request, f'Recurring expense {state}.')
    return redirect('recurring_list')


# ─── ANALYTICS ──────────────────────────────────────────────────

@login_required
def analytics_view(request):
    """Analytics and insights page."""
    user = request.user
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # This month's expenses
    month_expenses = Expense.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    )

    total_month = month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Highest category
    top_category = month_expenses.values('category__name').annotate(
        total=Sum('amount')).order_by('-total').first()

    # Most frequent expense
    frequent = month_expenses.values('title').annotate(
        count=models.Count('id')).order_by('-count').first() if month_expenses.exists() else None

    # Monthly income
    month_income = Income.objects.filter(
        user=user, date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    savings_rate = round(((month_income - total_month) / month_income * 100), 1) if month_income > 0 else 0

    # Average daily spending
    days_passed = today.day
    avg_daily = round(total_month / days_passed, 2) if days_passed > 0 else 0

    # Category breakdown for charts
    category_breakdown = list(month_expenses.values('category__name').annotate(
        total=Sum('amount')).order_by('-total'))

    # Payment method breakdown
    payment_breakdown = list(month_expenses.values('payment_method').annotate(
        total=Sum('amount')).order_by('-total'))

    # Weekly trend (last 4 weeks)
    weekly_labels = []
    weekly_data = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + i * 7)
        week_end = week_start + timedelta(days=6)
        label = f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"
        weekly_labels.append(label)
        total = Expense.objects.filter(
            user=user, date__gte=week_start, date__lte=week_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        weekly_data.append(float(total))

    currency_symbol = user.profile.currency_symbol if hasattr(user, 'profile') else '₹'

    # AI-like insights (rule-based)
    insights = []
    if total_month > month_income and month_income > 0:
        insights.append({
            'type': 'warning',
            'icon': 'bi-exclamation-triangle',
            'title': 'Overspending Alert',
            'message': f'Your expenses ({currency_symbol}{total_month}) exceed your income ({currency_symbol}{month_income}) this month.'
        })
    if top_category:
        insights.append({
            'type': 'info',
            'icon': 'bi-pie-chart',
            'title': 'Top Spending Category',
            'message': f'"{top_category["category__name"]}" is your highest spending category at {currency_symbol}{top_category["total"]}.'
        })
    if savings_rate > 20:
        insights.append({
            'type': 'success',
            'icon': 'bi-piggy-bank',
            'title': 'Great Savings!',
            'message': f'Your savings rate is {savings_rate}% this month. Keep it up!'
        })
    elif savings_rate > 0:
        insights.append({
            'type': 'info',
            'icon': 'bi-lightbulb',
            'title': 'Savings Tip',
            'message': f'Your savings rate is {savings_rate}%. Try to aim for at least 20%.'
        })

    context = {
        'total_month': total_month,
        'top_category': top_category,
        'frequent': frequent,
        'savings_rate': savings_rate,
        'avg_daily': avg_daily,
        'month_income': month_income,
        'category_breakdown': category_breakdown,
        'payment_breakdown': payment_breakdown,
        'weekly_labels': weekly_labels,
        'weekly_data': weekly_data,
        'insights': insights,
        'currency_symbol': currency_symbol,
    }
    return render(request, 'expenses/analytics.html', context)


# Need to import models for Count
from django.db import models
