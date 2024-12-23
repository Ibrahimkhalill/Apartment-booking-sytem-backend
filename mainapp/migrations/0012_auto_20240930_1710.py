# Generated by Django 3.2 on 2024-09-30 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_rename_room_quanity_reservation_room_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='hold_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='is_on_hold',
            field=models.BooleanField(default=False),
        ),
    ]
