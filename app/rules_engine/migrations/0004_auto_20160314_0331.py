# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules_engine', '0003_auto_20160314_0330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementsuppressor',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='elementsuppressor',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eventsuppressor',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eventsuppressor',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
