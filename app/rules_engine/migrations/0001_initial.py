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
            name='ElementSuppressor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('element', models.CharField(max_length=255, db_index=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('suppressed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventAndElementSuppressor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('element', models.CharField(max_length=255, db_index=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(to='cito_engine.Event')),
                ('suppressed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventSuppressor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(to='cito_engine.Event')),
                ('suppressed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParentEvents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('element', models.CharField(max_length=255, db_index=True)),
                ('event', models.ForeignKey(to='cito_engine.Event')),
            ],
        ),
    ]
