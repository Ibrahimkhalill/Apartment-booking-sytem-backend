# Generated by Django 3.2 on 2024-09-28 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_auto_20240928_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='availble_room',
        ),
        migrations.AddField(
            model_name='room',
            name='available_room',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
