from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Ensure a default superuser exists'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('ADMIN_EMAIL', 'sichombarobertbob@gmail.com')
        username = os.environ.get('ADMIN_USERNAME', 'robertsichomba')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.WARNING('ADMIN_PASSWORD not set, skipping'))
            return
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))