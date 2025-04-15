# Generated by Django 5.1.7 on 2025-04-15 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthtoken',
            name='LocationId',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='access_token',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='companyId',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='refresh_token',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='scope',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='userId',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='userType',
            field=models.CharField(max_length=100),
        ),
    ]
