# Generated by Django 3.2 on 2024-10-02 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_auto_20241001_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='confirmation_number',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ]