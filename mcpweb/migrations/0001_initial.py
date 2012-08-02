# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TronGame'
        db.create_table('mcpweb_trongame', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player1', to=orm['auth.User'])),
            ('player2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player2', to=orm['auth.User'])),
            ('current_player', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('winner', self.gf('django.db.models.fields.CharField')(default=u'inprogress', max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(default='Waiting for player 1 to go.', max_length=50)),
            ('game_state', self.gf('django.db.models.fields.TextField')()),
            ('turn', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_played', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('player1_token', self.gf('django.db.models.fields.CharField')(default='uQEvxOsEu9', max_length=10)),
            ('player2_token', self.gf('django.db.models.fields.CharField')(default='NE3uGEFcWF', max_length=10)),
        ))
        db.send_create_signal('mcpweb', ['TronGame'])

        # Adding model 'TronGameStateHistory'
        db.create_table('mcpweb_trongamestatehistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tron_game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcpweb.TronGame'])),
            ('game_state', self.gf('django.db.models.fields.TextField')()),
            ('turn', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mcpweb', ['TronGameStateHistory'])

        # Adding unique constraint on 'TronGameStateHistory', fields ['tron_game', 'turn']
        db.create_unique('mcpweb_trongamestatehistory', ['tron_game_id', 'turn'])


    def backwards(self, orm):
        # Removing unique constraint on 'TronGameStateHistory', fields ['tron_game', 'turn']
        db.delete_unique('mcpweb_trongamestatehistory', ['tron_game_id', 'turn'])

        # Deleting model 'TronGame'
        db.delete_table('mcpweb_trongame')

        # Deleting model 'TronGameStateHistory'
        db.delete_table('mcpweb_trongamestatehistory')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mcpweb.trongame': {
            'Meta': {'object_name': 'TronGame'},
            'current_player': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Waiting for player 1 to go.'", 'max_length': '50'}),
            'game_state': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_played': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player1'", 'to': "orm['auth.User']"}),
            'player1_token': ('django.db.models.fields.CharField', [], {'default': "'EGqXCvZ8Cj'", 'max_length': '10'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player2'", 'to': "orm['auth.User']"}),
            'player2_token': ('django.db.models.fields.CharField', [], {'default': "'CkA6mQ0bsq'", 'max_length': '10'}),
            'turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'winner': ('django.db.models.fields.CharField', [], {'default': "u'inprogress'", 'max_length': '10'})
        },
        'mcpweb.trongamestatehistory': {
            'Meta': {'unique_together': "(('tron_game', 'turn'),)", 'object_name': 'TronGameStateHistory'},
            'game_state': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tron_game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcpweb.TronGame']"}),
            'turn': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['mcpweb']