import os
import sys
import django

# Add current workspace directory to python search path
sys.path.insert(0, os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from expenses.models import Expense, Category
from expenses.forms import ExpenseForm
import datetime

def test():
    print("Testing Add Expense form instantiation and submission...")
    
    # Get or create test user
    user, created = User.objects.get_or_create(username='testuser', email='test@example.com')
    if created:
        user.set_password('testpass')
        user.save()
        print("Created testuser.")
    else:
        print("testuser already exists.")
        
    # Get category
    category = Category.objects.filter(is_default=True).first()
    if not category:
        category = Category.objects.create(name='Food', is_default=True)
        print("Created Food category.")
    else:
        print(f"Using category: {category.name}")
        
    # Instantiate GET form
    form_get = ExpenseForm(user=user)
    print("GET Form instantiated successfully.")
    
    # Simulate POST data
    post_data = {
        'title': 'Test Lunch',
        'amount': '150.50',
        'category': category.id,
        'payment_method': 'cash',
        'date': '2026-05-30',
        'description': 'Lunch with team',
        'notes': 'Test notes'
    }
    
    form_post = ExpenseForm(post_data, user=user)
    if form_post.is_valid():
        print("POST Form is valid.")
        expense = form_post.save(commit=False)
        expense.user = user
        expense.save()
        print(f"Expense saved successfully! ID: {expense.id}")
    else:
        print("POST Form errors:", form_post.errors)

if __name__ == '__main__':
    test()
