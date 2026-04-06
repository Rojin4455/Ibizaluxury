from decimal import Decimal
import re
from decimal import InvalidOperation

from django.db import migrations, models


def _clean_price_value(price_str):
    if not price_str:
        return None
    price_str = str(price_str).lower().strip()
    if price_str.endswith("m"):
        try:
            return Decimal(price_str[:-1]) * 1000000
        except InvalidOperation:
            return None
    if price_str.endswith("k"):
        try:
            return Decimal(price_str[:-1]) * 1000
        except InvalidOperation:
            return None
    cleaned = re.sub(r"[^\d.]", "", price_str)
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def backfill_price_bounds(apps, schema_editor):
    Contact = apps.get_model("core", "Contact")
    for row in Contact.objects.iterator(chunk_size=500):
        mn = _clean_price_value(row.min_price) if row.min_price else None
        mx = _clean_price_value(row.max_price) if row.max_price else None
        Contact.objects.filter(pk=row.pk).update(min_price_value=mn, max_price_value=mx)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_contact_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="min_price_value",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=20, null=True
            ),
        ),
        migrations.AddField(
            model_name="contact",
            name="max_price_value",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=20, null=True
            ),
        ),
        migrations.RunPython(backfill_price_bounds, migrations.RunPython.noop),
    ]
