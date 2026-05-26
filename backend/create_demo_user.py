import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.contrib.auth.models import User
from records.models import Tenant
if not User.objects.filter(username='analyst').exists():
    User.objects.create_user('analyst', 'analyst@demo.com', 'demo1234')
    print('Created analyst user')
if not Tenant.objects.filter(slug='demo-corp').exists():
    Tenant.objects.create(name='Demo Corp', slug='demo-corp')
    print('Created tenant')
print('Setup complete!')