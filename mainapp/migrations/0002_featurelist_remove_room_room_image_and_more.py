# Generated by Django 4.2.16 on 2024-09-28 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(max_length=200, null=True)),
                ('feature_images', models.ImageField(default='0.jpeg', upload_to='Feature')),
            ],
        ),
        migrations.RemoveField(
            model_name='room',
            name='room_image',
        ),
        migrations.AddField(
            model_name='room',
            name='availble_room',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='quantity',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='room_people',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_no',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_image', models.ImageField(default='0.jpeg', upload_to='media')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.room')),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='features',
            field=models.ManyToManyField(blank=True, null=True, related_name='rooms', to='mainapp.featurelist'),
        ),
    ]
