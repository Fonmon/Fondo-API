# Generated by Django 2.1.11 on 2020-01-12 16:38

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fondo_api', '0008_loan_disbursement_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchedulerTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'NOTIFICATIONS')])),
                ('run_date', models.DateTimeField()),
                ('payload', django.contrib.postgres.fields.hstore.HStoreField()),
                ('processed', models.BooleanField(default=False)),
            ],
        ),
    ]