# portfolio/apps.py
from django.apps import AppConfig

class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio'

    def ready(self):
        """
        Runs when the app is ready.
        Used here to create a superuser if none exists.
        """
        # Avoid circular imports
        from .utils import create_superuser_if_none
        try:
            create_superuser_if_none()
        except Exception as e:
            # Prevent app crash if DB is not ready yet
            print("Superuser creation skipped:", str(e))