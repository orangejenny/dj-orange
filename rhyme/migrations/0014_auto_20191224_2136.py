# Generated by Django 2.0.5 on 2019-12-24 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0013_song_time'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='songtag',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='songtag',
            name='song',
        ),
        migrations.RemoveField(
            model_name='songtag',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='song',
            name='time',
        ),
        migrations.AddField(
            model_name='tag',
            name='songs',
            field=models.ManyToManyField(to='rhyme.Song'),
        ),
        migrations.DeleteModel(
            name='SongTag',
        ),
    ]
