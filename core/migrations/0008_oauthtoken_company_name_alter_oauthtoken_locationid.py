# Generated by Django 5.1.7 on 2025-04-22 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_contact_properties'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthtoken',
            name='company_name',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='LocationId',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
