# Generated by Django 3.0.1 on 2020-01-12 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_player_manual_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='in_progress',
            field=models.BooleanField(default=False, verbose_name='in progess'),
        ),
    ]