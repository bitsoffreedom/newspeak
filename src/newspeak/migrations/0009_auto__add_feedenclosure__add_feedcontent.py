# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedEnclosure'
        db.create_table('newspeak_feedenclosure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='enclosures', to=orm['newspeak.FeedEntry'])),
            ('href', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('length', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('newspeak', ['FeedEnclosure'])

        # Adding model 'FeedContent'
        db.create_table('newspeak_feedcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content', to=orm['newspeak.FeedEntry'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('newspeak', ['FeedContent'])


    def backwards(self, orm):
        # Deleting model 'FeedEnclosure'
        db.delete_table('newspeak_feedenclosure')

        # Deleting model 'FeedContent'
        db.delete_table('newspeak_feedcontent')


    models = {
        'newspeak.feed': {
            'Meta': {'object_name': 'Feed'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'error_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'error_description': ('django.db.models.fields.TextField', [], {}),
            'error_state': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'etag': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['newspeak.KeywordFilter']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'newspeak.feedcontent': {
            'Meta': {'object_name': 'FeedContent'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content'", 'to': "orm['newspeak.FeedEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'newspeak.feedenclosure': {
            'Meta': {'object_name': 'FeedEnclosure'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'enclosures'", 'to': "orm['newspeak.FeedEntry']"}),
            'href': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'newspeak.feedentry': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'FeedEntry'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entry_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['newspeak.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '330', 'db_index': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'newspeak.keywordfilter': {
            'Meta': {'object_name': 'KeywordFilter'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'filter_inclusive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filter_summary': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filter_title': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['newspeak']