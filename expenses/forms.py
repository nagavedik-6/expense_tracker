from django import forms
from django.db import models
from .models import Expense, Category, RecurringExpense



class ExpenseForm(forms.ModelForm):
    """Expense creation/edit form."""
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'category', 'payment_method',
                  'date', 'receipt', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(is_default=True) | models.Q(user=user)
            )


class CategoryForm(forms.ModelForm):
    """Category creation/edit form."""
    class Meta:
        model = Category
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-tag (Bootstrap Icon)'}),
        }


class RecurringExpenseForm(forms.ModelForm):
    """Recurring expense form."""
    class Meta:
        model = RecurringExpense
        fields = ['title', 'description', 'amount', 'category', 'payment_method',
                  'frequency', 'next_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'next_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(is_default=True) | models.Q(user=user)
            )


class ExpenseFilterForm(forms.Form):
    """Form for filtering expenses."""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search expenses...'
    }))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Categories'
    )
    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + Expense.PAYMENT_METHODS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date'
    }))
    sort_by = forms.ChoiceField(
        choices=[
            ('-date', 'Date (Newest)'),
            ('date', 'Date (Oldest)'),
            ('-amount', 'Amount (High to Low)'),
            ('amount', 'Amount (Low to High)'),
            ('title', 'Title (A-Z)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
