# Generated by Django 3.1.2 on 2020-10-29 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aircraft',
            name='state',
            field=models.CharField(choices=[('PARKED', 'Parked'), ('TAKE_OFF', 'Take-off'), ('AIRBORNE', 'Airborne'), ('APPROACH', 'Approach'), ('LANDED', 'Landed')], default='PARKED', max_length=50),
        ),
    ]
