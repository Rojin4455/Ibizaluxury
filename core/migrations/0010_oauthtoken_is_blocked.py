# Generated by Django 5.1.7 on 2025-05-01 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_oauthtoken_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthtoken',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
