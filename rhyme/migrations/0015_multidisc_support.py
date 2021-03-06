# Generated by Django 2.0.5 on 2020-02-15 18:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0014_auto_20191224_2136'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disc',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('ordinal', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=255, null=True)),
                ('album', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='rhyme.Album')),
            ],
        ),
        migrations.AddField(
            model_name='track',
            name='disc',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='disc',
            unique_together={('ordinal', 'album')},
        ),
    ]
