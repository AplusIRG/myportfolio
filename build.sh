#!/usr/bin/env bash
set -o errexit

echo "=== Starting Render Build ==="

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate --noinput

# Create admin user if not exists
python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myportfolio.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=admin_user).exists():
    User.objects.create_superuser(admin_user, admin_email, admin_password)
    print(f"✓ Created admin user: {admin_user}")
else:
    print(f"✓ Admin user {admin_user} already exists")
END

# Collect static files
python manage.py collectstatic --noinput --clear

echo "=== Build Completed Successfully ==="