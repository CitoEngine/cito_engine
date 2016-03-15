# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules_engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementsuppressor',
            name='end_time',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='elementsuppressor',
            name='start_time',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='eventandelementsuppressor',
            name='end_time',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='eventandelementsuppressor',
            name='start_time',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='eventsuppressor',
            name='end_time',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='eventsuppressor',
            name='start_time',
            field=models.DateTimeField(default=None),
        ),
    ]
