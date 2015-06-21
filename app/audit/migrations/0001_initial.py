# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cito_engine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('level', models.CharField(default=b'info', max_length=5, choices=[(b'info', b'info'), (b'warn', b'warn'), (b'error', b'error')])),
            ],
        ),
        migrations.CreateModel(
            name='IncidentAuditLog',
            fields=[
                ('auditlog_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='audit.AuditLog')),
                ('incident', models.ForeignKey(to='cito_engine.Incident')),
            ],
            bases=('audit.auditlog',),
        ),
    ]
