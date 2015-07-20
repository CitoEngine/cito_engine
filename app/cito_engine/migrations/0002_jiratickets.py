# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cito_engine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JIRATickets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.CharField(max_length=64, verbose_name=b'JIRA Ticket ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('incident', models.ForeignKey(to='cito_engine.Incident')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
