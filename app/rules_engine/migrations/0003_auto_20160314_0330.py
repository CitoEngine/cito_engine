# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules_engine', '0002_auto_20160313_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventandelementsuppressor',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eventandelementsuppressor',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
