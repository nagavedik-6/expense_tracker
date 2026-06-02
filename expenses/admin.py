from django.contrib import admin
from .models import Category, Expense, RecurringExpense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'user', 'is_default']
    list_filter = ['is_default']
    search_fields = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'category', 'payment_method', 'date']
    list_filter = ['payment_method', 'date', 'category']
    search_fields = ['title', 'description', 'notes', 'user__username']
    date_hierarchy = 'date'

@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'frequency', 'next_date', 'is_active']
    list_filter = ['frequency', 'is_active', 'next_date']
    search_fields = ['title', 'user__username']
