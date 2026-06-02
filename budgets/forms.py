from django import forms
from .models import Budget
from expenses.models import Category
from django.db import models


class BudgetForm(forms.ModelForm):
    """Budget creation/edit form."""
    class Meta:
        model = Budget
        fields = ['name', 'category', 'amount', 'month', 'year', 'alert_threshold']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Budget Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2026'}),
            'alert_threshold': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': '80'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(is_default=True) | models.Q(user=user)
            )
