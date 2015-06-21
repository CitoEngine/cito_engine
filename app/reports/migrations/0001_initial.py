# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.IntegerField()),
                ('team_id', models.IntegerField()),
                ('severity', models.CharField(max_length=4)),
                ('category', models.CharField(max_length=64)),
                ('day', models.DateField()),
                ('total_incidents', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='HourlyData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.IntegerField()),
                ('team_id', models.IntegerField()),
                ('severity', models.CharField(max_length=4)),
                ('category', models.CharField(max_length=64)),
                ('hour', models.DateTimeField()),
                ('total_incidents', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
