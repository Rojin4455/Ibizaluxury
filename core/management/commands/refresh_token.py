from django.core.management.base import BaseCommand
from core.services import OAuthServices

class Command(BaseCommand):
    help = "Fetch a fresh access token using the provided authorization code."

    def handle(self, *args, **kwargs):
        
        try:
            access_token = OAuthServices.refresh_access_token()
            self.stdout.write(self.style.SUCCESS(f"Successfully retrieved new access token: {access_token}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
