from django.db import models
from django.contrib.auth.models import User
from expenses.models import Category


class Budget(models.Model):
    """Monthly budget for a category."""
    MONTH_CHOICES = [(i, m) for i, m in enumerate(
        ['January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December'], 1)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    alert_threshold = models.IntegerField(default=80,
                                          help_text='Alert when spending reaches this % of budget')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['user', 'category', 'month', 'year']

    def __str__(self):
        return f"{self.name} - {self.get_month_display()} {self.year}"

    @property
    def spent_amount(self):
        """Calculate total spent in this budget's category for the month."""
        from expenses.models import Expense
        filters = {
            'user': self.user,
            'date__month': self.month,
            'date__year': self.year,
        }
        if self.category:
            filters['category'] = self.category
        total = Expense.objects.filter(**filters).aggregate(
            total=models.Sum('amount'))['total'] or 0
        return total

    @property
    def remaining(self):
        return self.amount - self.spent_amount

    @property
    def percentage_used(self):
        if self.amount == 0:
            return 0
        return min(round((self.spent_amount / self.amount) * 100, 1), 100)

    @property
    def is_over_budget(self):
        return self.spent_amount > self.amount

    @property
    def is_near_limit(self):
        return self.percentage_used >= self.alert_threshold and not self.is_over_budget
