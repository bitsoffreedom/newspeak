# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FeedEnclosure.href'
        db.alter_column('newspeak_feedenclosure', 'href', self.gf('django.db.models.fields.URLField')(max_length=512))

    def backwards(self, orm):

        # Changing field 'FeedEnclosure.href'
        db.alter_column('newspeak_feedenclosure', 'href', self.gf('django.db.models.fields.URLField')(max_length=330))

    models = {
        'newspeak.feed': {
            'Meta': {'object_name': 'Feed'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'content_language': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content_mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content_xpath': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enclosure_mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enclosure_xpath': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'error_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'error_description': ('django.db.models.fields.TextField', [], {}),
            'error_state': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'etag': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['newspeak.KeywordFilter']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '330', 'blank': 'True'}),
            'modified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'summary_override': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'summary_xpath': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '330'})
        },
        'newspeak.feedcontent': {
            'Meta': {'object_name': 'FeedContent'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content'", 'to': "orm['newspeak.FeedEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'newspeak.feedenclosure': {
            'Meta': {'object_name': 'FeedEnclosure'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'enclosures'", 'to': "orm['newspeak.FeedEntry']"}),
            'href': ('django.db.models.fields.URLField', [], {'max_length': '512'}),
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