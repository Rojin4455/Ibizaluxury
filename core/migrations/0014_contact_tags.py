from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_contact_webhook_custom_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="tags",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
