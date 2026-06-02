import os
import sys
import django

# Add current workspace directory to python search path
sys.path.insert(0, os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from expenses.views import dashboard_view, expense_create
from expenses.models import Expense, Category

def test():
    print("Testing rendering of Dashboard view and Expense Creation view...")
    
    # Get or create test user
    user = User.objects.get(username='testuser')
    
    # Setup request factory
    factory = RequestFactory()
    
    # 1. Test Dashboard View
    request_dash = factory.get('/dashboard/')
    request_dash.user = user
    
    try:
        response_dash = dashboard_view(request_dash)
        print(f"Dashboard View rendered successfully! Status code: {response_dash.status_code}")
    except Exception as e:
        print("Error rendering Dashboard View:")
        import traceback
        traceback.print_exc()
        
    # 2. Test Expense Create GET View
    request_create_get = factory.get('/expenses/create/')
    request_create_get.user = user
    
    try:
        response_create_get = expense_create(request_create_get)
        print(f"Expense Create GET View rendered successfully! Status code: {response_create_get.status_code}")
    except Exception as e:
        print("Error rendering Expense Create GET View:")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test()
