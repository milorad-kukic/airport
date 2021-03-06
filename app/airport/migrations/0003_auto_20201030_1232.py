# Generated by Django 3.1.2 on 2020-10-30 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0002_aircraft_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='aircraft',
            name='altitude',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='heading',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='longitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='aircraft',
            name='type',
            field=models.CharField(choices=[('AIRLINER', 'Airliner'), ('PRIVATE', 'Private')], default='PRIVATE', max_length=50),
        ),
    ]
