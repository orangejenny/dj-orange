# Generated by Django 2.0.5 on 2018-05-29 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0002_auto_20180528_2338'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rhyme.Song')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='songtag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rhyme.Tag'),
        ),
    ]
