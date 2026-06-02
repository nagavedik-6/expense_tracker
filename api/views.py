from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from expenses.models import Category, Expense
from income.models import Income
from budgets.models import Budget
from savings.models import SavingsGoal
from notifications.models import Notification

from .serializers import (
    CategorySerializer, ExpenseSerializer, IncomeSerializer,
    BudgetSerializer, SavingsGoalSerializer, NotificationSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        from django.db.models import Q
        return Category.objects.filter(
            Q(is_default=True) | Q(user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    filterset_fields = ['category', 'payment_method', 'date']
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['date', 'amount', 'title']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    filterset_fields = ['source', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount']

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    filterset_fields = ['month', 'year', 'category']

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_contribution(self, request, pk=None):
        goal = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'}, status=400)
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': 'Invalid amount'}, status=400)

        goal.current_amount += amount
        goal.save()

        if goal.is_completed:
            Notification.objects.create(
                user=request.user,
                message=f'Congratulations! You\'ve reached your savings goal "{goal.goal_name}"! 🎉',
                notification_type='savings_complete',
                link='/savings/'
            )

        return Response(SavingsGoalSerializer(goal).data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'All notifications marked as read'})
