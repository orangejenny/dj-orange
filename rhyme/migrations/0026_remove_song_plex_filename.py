# Generated by Django 3.1.7 on 2022-10-23 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0025_add_indices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='plex_filename',
        ),
    ]
