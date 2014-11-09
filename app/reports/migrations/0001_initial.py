# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HourlyData'
        db.create_table(u'reports_hourlydata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_id', self.gf('django.db.models.fields.IntegerField')()),
            ('team_id', self.gf('django.db.models.fields.IntegerField')()),
            ('severity', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('hour', self.gf('django.db.models.fields.DateTimeField')()),
            ('total_incidents', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'reports', ['HourlyData'])

        # Adding model 'DailyData'
        db.create_table(u'reports_dailydata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_id', self.gf('django.db.models.fields.IntegerField')()),
            ('team_id', self.gf('django.db.models.fields.IntegerField')()),
            ('severity', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('day', self.gf('django.db.models.fields.DateField')()),
            ('total_incidents', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'reports', ['DailyData'])


    def backwards(self, orm):
        # Deleting model 'HourlyData'
        db.delete_table(u'reports_hourlydata')

        # Deleting model 'DailyData'
        db.delete_table(u'reports_dailydata')


    models = {
        u'reports.dailydata': {
            'Meta': {'object_name': 'DailyData'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            'event_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'team_id': ('django.db.models.fields.IntegerField', [], {}),
            'total_incidents': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'reports.hourlydata': {
            'Meta': {'object_name': 'HourlyData'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'event_id': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'team_id': ('django.db.models.fields.IntegerField', [], {}),
            'total_incidents': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['reports']