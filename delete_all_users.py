# delete_all_users.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myportfolio.settings")
django.setup()

from django.contrib.auth.models import User

# DELETE ALL USERS
User.objects.all().delete()

# CREATE NEW SUPERUSER
User.objects.create_superuser(
    username="admin",
    email="admin@example.com",
    password="StrongPassword123"
)

print("All users deleted and new superuser created.")
