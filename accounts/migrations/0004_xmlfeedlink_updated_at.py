# Generated by Django 5.1.7 on 2025-04-17 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_xmlfeedlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='xmlfeedlink',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
