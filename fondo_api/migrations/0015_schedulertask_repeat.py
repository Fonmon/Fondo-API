# Generated by Django 2.2.10 on 2020-04-12 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fondo_api', '0014_auto_20200412_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulertask',
            name='repeat',
            field=models.IntegerField(choices=[(0, 'NONE'), (1, 'DAILY'), (2, 'WEEKLY'), (3, 'MONTHLY'), (4, 'YEARLY')], default=0),
        ),
    ]