from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_alter_contact_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="budget",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="checkin_date",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="checkout_date",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="preferred_location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="property_status",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="rental_property_type",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="weekly_price_range",
            field=models.TextField(blank=True, null=True),
        ),
    ]
