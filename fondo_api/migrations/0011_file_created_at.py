# Generated by Django 2.2.10 on 2020-02-23 19:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fondo_api', '0010_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
