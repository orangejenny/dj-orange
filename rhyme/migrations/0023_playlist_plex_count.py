# Generated by Django 2.0.12 on 2020-07-19 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0022_playlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='plex_count',
            field=models.IntegerField(default=0),
        ),
    ]
