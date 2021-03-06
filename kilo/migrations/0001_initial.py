# Generated by Django 2.0.5 on 2019-01-02 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('notes', models.CharField(max_length=1024, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(max_length=32)),
                ('time', models.SmallIntegerField(null=True)),
                ('distance', models.FloatField(null=True)),
                ('distance_unit', models.CharField(choices=[('mi', 'mi'), ('km', 'km'), ('m', 'm')], default='mi', max_length=3, null=True)),
                ('sets', models.SmallIntegerField(null=True)),
                ('reps', models.SmallIntegerField(null=True)),
                ('weight', models.SmallIntegerField(null=True)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kilo.Day')),
            ],
        ),
    ]
