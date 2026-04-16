from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_contact_price_value_bounds"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="is_active",
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
