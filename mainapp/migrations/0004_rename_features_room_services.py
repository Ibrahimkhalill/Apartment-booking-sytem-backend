# Generated by Django 4.2.16 on 2024-09-28 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_images_room_alter_room_features'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='features',
            new_name='services',
        ),
    ]
