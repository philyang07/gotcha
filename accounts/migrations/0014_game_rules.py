# Generated by Django 3.0.1 on 2020-01-15 18:51

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_remove_game_rules'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='rules',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]