import django.utils.timezone
from django.db import migrations, models


MODELS = ['album', 'artist', 'playlist', 'playlistsong', 'song', 'tag']


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0028_alter_track_unique_together'),
    ]

    operations = [
        op
        for model in MODELS
        for op in [
            migrations.AddField(
                model_name=model,
                name='created_at',
                field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
                preserve_default=False,
            ),
            migrations.AddField(
                model_name=model,
                name='updated_at',
                field=models.DateTimeField(auto_now=True),
            ),
        ]
    ]
