from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_contact_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="last_shared_property_ids",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
