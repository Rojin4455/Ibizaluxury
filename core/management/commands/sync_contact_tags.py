from django.core.management.base import BaseCommand

from core.services import ContactServices


class Command(BaseCommand):
    help = (
        "Fetch all contacts from GHL and update only tags on contacts that already exist locally."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            type=str,
            help="Optional query passed to the GHL contacts API",
        )
        parser.add_argument(
            "--location-id",
            type=str,
            help="Only sync this location (default: all OAuth locations)",
        )

    def handle(self, *args, **kwargs):
        query = kwargs.get("query")
        location_id = kwargs.get("location_id")
        try:
            result = ContactServices.sync_contact_tags_from_ghl(
                query=query, location_id=location_id
            )
            for line in result:
                self.stdout.write(self.style.SUCCESS(line))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
