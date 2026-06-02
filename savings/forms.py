from django import forms
from .models import SavingsGoal


class SavingsGoalForm(forms.ModelForm):
    """Savings goal creation/edit form."""
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'goal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Goal Name'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ContributionForm(forms.Form):
    """Form to add money to a savings goal."""
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount to add'
        })
    )
