# -*- coding: utf-8 -*-
import mcp

from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for game in orm['mcpweb.TronGame'].objects.all():
            self.migrate_game(game)

    def migrate_game(self, game):
        history = {}
        for h in game.trongamestatehistory_set.all():
            gs = mcp.GameState.loads(h.game_state)
            if h.turn == 0:
                history[gs.you] = 1
                history[gs.opponent] = -1
            elif h.turn % 2 == 1:
                history[gs.you] = (h.turn - 1) / 2 + 2
            else:
                history[gs.opponent] = -(h.turn / 2 + 1)
        # quick check to see if the history makes sense. If the game object is
        # from old code it will be missing history, so rather just blank out
        # the history
        count = 0
        for p, v in mcp.GameState.loads(game.game_state):
            if v == 'Clear':
                continue
            else:
                count += 1
                if p not in history:
                    count = -1
                    break
        if len(history) == count:
            history_str = '\n'.join('%d %d %d' % (p.x, p.y, t)
                                    for p, t in history.iteritems())
        else:
            print('missing history in game %d, skipping' % game.id)
            history_str = ''
        game.game_history = history_str
        game.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        raise RuntimeError('Not implemented!')

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
            'Meta': {'ordering': "['-date_created']", 'object_name': 'TronGame'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Waiting for player 1 to go.'", 'max_length': '50'}),
            'game_history': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'game_state': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_played': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player1'", 'to': "orm['auth.User']"}),
            'player1_token': ('django.db.models.fields.CharField', [], {'default': "'XdiUofuDokE1'", 'max_length': '10'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player2'", 'to': "orm['auth.User']"}),
            'player2_token': ('django.db.models.fields.CharField', [], {'default': "'dDYMr1BpDavm'", 'max_length': '10'}),
            'turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'winner': ('django.db.models.fields.CharField', [], {'default': "u'inprogress'", 'max_length': '10'})
        },
        'mcpweb.trongamestatehistory': {
            'Meta': {'ordering': "['tron_game', 'turn']", 'unique_together': "(('tron_game', 'turn'),)", 'object_name': 'TronGameStateHistory'},
            'game_state': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tron_game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcpweb.TronGame']"}),
            'turn': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['mcpweb']
    symmetrical = True
