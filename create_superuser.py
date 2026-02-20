import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myportfolio.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Read environment variables
username = os.environ.get('ADMIN_USERNAME', 'robertsichomba')
email = os.environ.get('ADMIN_EMAIL', 'sichombarobertbob@gmail.com')
password = os.environ.get('ADMIN_PASSWORD', '17114240@Rob')

# Create superuser if it doesn't exist
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")