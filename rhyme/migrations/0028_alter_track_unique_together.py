# Generated by Django 4.2.9 on 2024-05-17 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0027_playlistsong'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='track',
            unique_together={('song', 'album')},
        ),
    ]
