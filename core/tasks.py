from celery import shared_task
from core.services import OAuthServices

@shared_task
def refresh_token_task():
    results = OAuthServices.refresh_all_tokens()
    for location_id, status, message in results:
        print(f"[{location_id}] {status.upper()}: {message}")
    return "Token refresh task executed."