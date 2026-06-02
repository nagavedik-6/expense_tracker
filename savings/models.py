from django.db import models
from django.contrib.auth.models import User


class SavingsGoal(models.Model):
    """Savings goal with progress tracking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    goal_name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline']

    def __str__(self):
        return f"{self.goal_name} - {self.completion_percentage}%"

    @property
    def completion_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(round((self.current_amount / self.target_amount) * 100, 1), 100)

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, 0)

    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount

    @property
    def days_remaining(self):
        from django.utils import timezone
        delta = self.deadline - timezone.now().date()
        return max(delta.days, 0)
