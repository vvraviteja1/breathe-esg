import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.contrib.auth.models import User
from records.models import Tenant

# Force delete and recreate
User.objects.filter(username='analyst').delete()
u = User.objects.create_user('analyst', 'analyst@demo.com', 'demo1234')
print(f'Created user: {u.username} / demo1234')

User.objects.filter(username='admin').delete()
User.objects.create_superuser('admin', 'admin@demo.com', 'admin123')
print('Created admin user')

Tenant.objects.get_or_create(name='Demo Corp', slug='demo-corp')
print('Tenant ready')
print('Setup complete!')