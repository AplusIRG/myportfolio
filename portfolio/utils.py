# portfolio/utils.py
from django.contrib.auth import get_user_model

def create_superuser_if_none():
    """
    Creates a superuser with predefined credentials if none exists.
    Safe to run on app startup.
    """
    User = get_user_model()
    username = "robertsichomba"
    email = "sichombarobertbob@gmail.com"
    password = "17114240@Rob"

    if not User.objects.filter(username=username).exists():
        print("Creating superuser:", username)
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
    else:
        print("Superuser already exists:", username)