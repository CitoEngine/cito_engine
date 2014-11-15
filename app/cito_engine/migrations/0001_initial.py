# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PluginServer'
        db.create_table(u'cito_engine_pluginserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('url', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('ssl_verify', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'cito_engine', ['PluginServer'])

        # Adding model 'Plugin'
        db.create_table(u'cito_engine_plugin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.PluginServer'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('dateAdded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastUpdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'cito_engine', ['Plugin'])

        # Adding model 'Category'
        db.create_table(u'cito_engine_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('categoryType', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'cito_engine', ['Category'])

        # Adding model 'Team'
        db.create_table(u'cito_engine_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'cito_engine', ['Team'])

        # Adding M2M table for field members on 'Team'
        m2m_table_name = db.shorten_name(u'cito_engine_team_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'cito_engine.team'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'user_id'])

        # Adding model 'Event'
        db.create_table(u'cito_engine_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('severity', self.gf('django.db.models.fields.CharField')(default='S3', max_length=2)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Team'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Category'])),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'cito_engine', ['Event'])

        # Adding model 'Incident'
        db.create_table(u'cito_engine_incident', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Event'])),
            ('element', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='Active', max_length=15)),
            ('firstEventTime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastEventTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('acknowledged_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('close_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('acknowledged_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, blank=True, to=orm['auth.User'])),
            ('closed_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, blank=True, to=orm['auth.User'])),
            ('total_incidents', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'cito_engine', ['Incident'])

        # Adding model 'IncidentLog'
        db.create_table(u'cito_engine_incidentlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('incident', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Incident'])),
            ('msg', self.gf('django.db.models.fields.TextField')(default='No text provided', max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'cito_engine', ['IncidentLog'])

        # Adding model 'EventAction'
        db.create_table(u'cito_engine_eventaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Event'])),
            ('plugin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Plugin'])),
            ('pluginParameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('dateAdded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('dateUpdated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('isEnabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('threshold_count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('threshold_timer', self.gf('django.db.models.fields.IntegerField')(default=60)),
        ))
        db.send_create_signal(u'cito_engine', ['EventAction'])

        # Adding model 'EventActionCounter'
        db.create_table(u'cito_engine_eventactioncounter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('incident', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Incident'])),
            ('event_action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.EventAction'])),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('timer', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_triggered', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'cito_engine', ['EventActionCounter'])

        # Adding model 'EventActionLog'
        db.create_table(u'cito_engine_eventactionlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eventAction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.EventAction'])),
            ('incident', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cito_engine.Incident'])),
            ('dateAdded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default='No text provided')),
        ))
        db.send_create_signal(u'cito_engine', ['EventActionLog'])


    def backwards(self, orm):
        # Deleting model 'PluginServer'
        db.delete_table(u'cito_engine_pluginserver')

        # Deleting model 'Plugin'
        db.delete_table(u'cito_engine_plugin')

        # Deleting model 'Category'
        db.delete_table(u'cito_engine_category')

        # Deleting model 'Team'
        db.delete_table(u'cito_engine_team')

        # Removing M2M table for field members on 'Team'
        db.delete_table(db.shorten_name(u'cito_engine_team_members'))

        # Deleting model 'Event'
        db.delete_table(u'cito_engine_event')

        # Deleting model 'Incident'
        db.delete_table(u'cito_engine_incident')

        # Deleting model 'IncidentLog'
        db.delete_table(u'cito_engine_incidentlog')

        # Deleting model 'EventAction'
        db.delete_table(u'cito_engine_eventaction')

        # Deleting model 'EventActionCounter'
        db.delete_table(u'cito_engine_eventactioncounter')

        # Deleting model 'EventActionLog'
        db.delete_table(u'cito_engine_eventactionlog')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cito_engine.category': {
            'Meta': {'ordering': "['categoryType']", 'object_name': 'Category'},
            'categoryType': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cito_engine.event': {
            'Meta': {'object_name': 'Event'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'S3'", 'max_length': '2'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Team']"})
        },
        u'cito_engine.eventaction': {
            'Meta': {'object_name': 'EventAction'},
            'dateAdded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dateUpdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Plugin']"}),
            'pluginParameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'threshold_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'threshold_timer': ('django.db.models.fields.IntegerField', [], {'default': '60'})
        },
        u'cito_engine.eventactioncounter': {
            'Meta': {'object_name': 'EventActionCounter'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'event_action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.EventAction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Incident']"}),
            'is_triggered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timer': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'cito_engine.eventactionlog': {
            'Meta': {'object_name': 'EventActionLog'},
            'dateAdded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'eventAction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.EventAction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Incident']"}),
            'text': ('django.db.models.fields.TextField', [], {'default': "'No text provided'"})
        },
        u'cito_engine.incident': {
            'Meta': {'object_name': 'Incident'},
            'acknowledged_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'acknowledged_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'close_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'element': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Event']"}),
            'firstEventTime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastEventTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Active'", 'max_length': '15'}),
            'total_incidents': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'cito_engine.incidentlog': {
            'Meta': {'object_name': 'IncidentLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.Incident']"}),
            'msg': ('django.db.models.fields.TextField', [], {'default': "'No text provided'", 'max_length': '255'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'cito_engine.plugin': {
            'Meta': {'object_name': 'Plugin'},
            'dateAdded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastUpdated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cito_engine.PluginServer']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'cito_engine.pluginserver': {
            'Meta': {'object_name': 'PluginServer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ssl_verify': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        u'cito_engine.team': {
            'Meta': {'ordering': "['name']", 'object_name': 'Team'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cito_engine']