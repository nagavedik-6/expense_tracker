from django.urls import path
from . import views

urlpatterns = [
    path('', views.income_list, name='income_list'),
    path('create/', views.income_create, name='income_create'),
    path('<int:pk>/update/', views.income_update, name='income_update'),
    path('<int:pk>/delete/', views.income_delete, name='income_delete'),
]
