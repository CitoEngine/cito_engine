# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('categoryType', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['categoryType'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('severity', models.CharField(default=b'S3', max_length=2, choices=[(b'S0', b'S0'), (b'S1', b'S1'), (b'S2', b'S2'), (b'S3', b'S3')])),
                ('status', models.BooleanField(default=True)),
                ('category', models.ForeignKey(to='cito_engine.Category')),
            ],
        ),
        migrations.CreateModel(
            name='EventAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pluginParameters', models.TextField(null=True, blank=True)),
                ('dateAdded', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('isEnabled', models.BooleanField(default=True)),
                ('threshold_count', models.IntegerField(default=1)),
                ('threshold_timer', models.IntegerField(default=60)),
                ('event', models.ForeignKey(to='cito_engine.Event')),
            ],
        ),
        migrations.CreateModel(
            name='EventActionCounter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=1)),
                ('timer', models.IntegerField(default=0)),
                ('is_triggered', models.BooleanField(default=False)),
                ('event_action', models.ForeignKey(to='cito_engine.EventAction')),
            ],
        ),
        migrations.CreateModel(
            name='EventActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dateAdded', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(default=b'No text provided')),
                ('eventAction', models.ForeignKey(to='cito_engine.EventAction')),
            ],
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('element', models.CharField(max_length=255)),
                ('status', models.CharField(default=b'Active', max_length=15, choices=[(b'Active', b'Active'), (b'Acknowledged', b'Acknowledged'), (b'Cleared', b'Cleared')])),
                ('firstEventTime', models.DateTimeField(auto_now_add=True)),
                ('lastEventTime', models.DateTimeField(null=True, blank=True)),
                ('acknowledged_time', models.DateTimeField(null=True, blank=True)),
                ('close_time', models.DateTimeField(null=True, blank=True)),
                ('total_incidents', models.IntegerField(default=0)),
                ('is_suppressed', models.BooleanField(default=False)),
                ('acknowledged_by', models.ForeignKey(related_name='+', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('closed_by', models.ForeignKey(related_name='+', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('event', models.ForeignKey(to='cito_engine.Event')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('msg', models.TextField(default=b'No text provided', max_length=255)),
                ('timestamp', models.DateTimeField()),
                ('incident', models.ForeignKey(to='cito_engine.Incident')),
            ],
        ),
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('dateAdded', models.DateTimeField(auto_now_add=True)),
                ('lastUpdated', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PluginServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('url', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('ssl_verify', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('members', models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='plugin',
            name='server',
            field=models.ForeignKey(to='cito_engine.PluginServer'),
        ),
        migrations.AddField(
            model_name='eventactionlog',
            name='incident',
            field=models.ForeignKey(to='cito_engine.Incident'),
        ),
        migrations.AddField(
            model_name='eventactioncounter',
            name='incident',
            field=models.ForeignKey(to='cito_engine.Incident'),
        ),
        migrations.AddField(
            model_name='eventaction',
            name='plugin',
            field=models.ForeignKey(to='cito_engine.Plugin'),
        ),
        migrations.AddField(
            model_name='event',
            name='team',
            field=models.ForeignKey(to='cito_engine.Team'),
        ),
    ]
