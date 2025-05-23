# Generated by Django 5.1.7 on 2025-04-21 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_xmlfeedlink_updated_at'),
        ('core', '0005_customfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='properties',
            field=models.ManyToManyField(blank=True, related_name='contacts', to='accounts.property'),
        ),
        migrations.AddField(
            model_name='contact',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='selec_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
