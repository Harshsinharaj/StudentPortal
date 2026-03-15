import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@portal.com', 'admin123')
    print("✓ Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Admin user already exists")
