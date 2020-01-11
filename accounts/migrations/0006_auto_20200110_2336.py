# Generated by Django 3.0.1 on 2020-01-10 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200110_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Game'),
        ),
        migrations.AlterField(
            model_name='player',
            name='secret_code',
            field=models.IntegerField(blank=True, null=True, verbose_name='secret code'),
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('game', 'secret_code')},
        ),
    ]