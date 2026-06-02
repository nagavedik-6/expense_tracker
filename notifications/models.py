from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """User notification."""
    NOTIFICATION_TYPES = [
        ('budget_alert', 'Budget Alert'),
        ('budget_exceeded', 'Budget Exceeded'),
        ('savings_reminder', 'Savings Reminder'),
        ('savings_complete', 'Savings Goal Complete'),
        ('monthly_summary', 'Monthly Summary'),
        ('payment_reminder', 'Payment Reminder'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES,
                                         default='general')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.message[:50]}"
