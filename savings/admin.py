from django.contrib import admin
from .models import SavingsGoal

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['goal_name', 'user', 'target_amount', 'current_amount', 'deadline']
    list_filter = ['deadline']
    search_fields = ['goal_name', 'user__username']
