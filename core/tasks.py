from celery import shared_task
from .services import OAuthServices

@shared_task
def refresh_token_task():
    OAuthServices.refresh_access_token()
    print("Token refresh task executed.")