# Generated by Django 2.0.12 on 2020-12-04 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kilo', '0003_rename_workout_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='seconds',
            field=models.FloatField(null=True),
        ),
    ]
