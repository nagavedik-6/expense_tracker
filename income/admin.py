from django.contrib import admin
from .models import Income

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['source', 'user', 'amount', 'date']
    list_filter = ['source', 'date']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'
