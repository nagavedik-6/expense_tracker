from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('expenses', 'Category')
    defaults = [
        ('Food', 'bi-egg-fried'),
        ('Transportation', 'bi-car-front'),
        ('Shopping', 'bi-cart'),
        ('Education', 'bi-book'),
        ('Entertainment', 'bi-controller'),
        ('Healthcare', 'bi-heart-pulse'),
        ('Rent', 'bi-house'),
        ('Utilities', 'bi-lightning-charge'),
        ('Travel', 'bi-airplane'),
        ('Investments', 'bi-graph-up'),
        ('Others', 'bi-tag')
    ]
    for name, icon in defaults:
        Category.objects.create(name=name, icon=icon, is_default=True)

class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories),
    ]
