from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('expenses', views.ExpenseViewSet, basename='expense')
router.register('income', views.IncomeViewSet, basename='income')
router.register('budgets', views.BudgetViewSet, basename='budget')
router.register('savings', views.SavingsGoalViewSet, basename='savings')
router.register('notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
