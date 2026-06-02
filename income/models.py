from django.db import models
from django.contrib.auth.models import User


class Income(models.Model):
    """Income record."""
    SOURCE_CHOICES = [
        ('salary', 'Salary'),
        ('freelance', 'Freelance'),
        ('business', 'Business'),
        ('investment', 'Investment'),
        ('rental', 'Rental'),
        ('gift', 'Gift'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='salary')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Incomes'

    def __str__(self):
        return f"{self.get_source_display()} - {self.amount}"
