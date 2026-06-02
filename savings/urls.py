from django.urls import path
from . import views

urlpatterns = [
    path('', views.savings_list, name='savings_list'),
    path('create/', views.savings_create, name='savings_create'),
    path('<int:pk>/update/', views.savings_update, name='savings_update'),
    path('<int:pk>/delete/', views.savings_delete, name='savings_delete'),
    path('<int:pk>/contribute/', views.savings_contribute, name='savings_contribute'),
]
