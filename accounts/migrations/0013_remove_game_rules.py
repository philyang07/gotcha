# Generated by Django 3.0.1 on 2020-01-15 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20200116_0025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='rules',
        ),
    ]
