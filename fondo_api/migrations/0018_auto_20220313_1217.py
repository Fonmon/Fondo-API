# Generated by Django 2.2.27 on 2022-03-13 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fondo_api', '0017_savingaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='type',
            field=models.IntegerField(choices=[(0, 'proceeding'), (1, 'presentations')]),
        ),
    ]
