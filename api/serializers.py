from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import UserProfile
from expenses.models import Category, Expense, RecurringExpense
from income.models import Income
from budgets.models import Budget
from savings.models import SavingsGoal
from notifications.models import Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'currency', 'theme', 'profile_picture']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_default']
        read_only_fields = ['is_default']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount', 'category', 'category_name',
            'payment_method', 'date', 'receipt', 'notes', 'created_at'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class IncomeSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = Income
        fields = ['id', 'source', 'source_display', 'amount', 'date', 'description', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    spent_amount = serializers.ReadOnlyField()
    remaining = serializers.ReadOnlyField()
    percentage_used = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'category', 'category_name', 'amount', 'month', 'year',
            'alert_threshold', 'spent_amount', 'remaining', 'percentage_used'
        ]


class SavingsGoalSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'goal_name', 'target_amount', 'current_amount', 'deadline',
            'completion_percentage', 'remaining_amount', 'is_completed', 'days_remaining'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'notification_type', 'is_read', 'link', 'created_at']
