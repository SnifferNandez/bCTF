# Generated by Django 2.1.2 on 2018-10-15 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='attendant',
            field=models.BooleanField(default=False),
        ),
    ]
