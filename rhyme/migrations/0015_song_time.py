# Generated by Django 2.0.5 on 2020-02-15 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0014_auto_20191224_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='time',
            field=models.IntegerField(null=True),
        ),
    ]