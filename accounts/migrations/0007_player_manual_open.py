# Generated by Django 3.0.1 on 2020-01-10 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200110_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='manual_open',
            field=models.BooleanField(default=False, verbose_name='manual open'),
        ),
    ]
