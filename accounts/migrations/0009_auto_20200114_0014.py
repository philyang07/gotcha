# Generated by Django 3.0.1 on 2020-01-13 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_game_in_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='access_code',
            field=models.CharField(max_length=5, unique=True, verbose_name='access code'),
        ),
    ]