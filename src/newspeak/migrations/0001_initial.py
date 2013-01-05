# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KeywordFilter'
        db.create_table('newspeak_keywordfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('django.db.models.fields.TextField')()),
            ('filter_title', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filter_summary', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('newspeak', ['KeywordFilter'])

        # Adding model 'Feed'
        db.create_table('newspeak_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
        ))
        db.send_create_signal('newspeak', ['Feed'])

        # Adding M2M table for field filters on 'Feed'
        db.create_table('newspeak_feed_filters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feed', models.ForeignKey(orm['newspeak.feed'], null=False)),
            ('keywordfilter', models.ForeignKey(orm['newspeak.keywordfilter'], null=False))
        ))
        db.create_unique('newspeak_feed_filters', ['feed_id', 'keywordfilter_id'])

        # Adding model 'FeedEntry'
        db.create_table('newspeak_feedentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['newspeak.Feed'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('entry_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('published', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('newspeak', ['FeedEntry'])


    def backwards(self, orm):
        # Deleting model 'KeywordFilter'
        db.delete_table('newspeak_keywordfilter')

        # Deleting model 'Feed'
        db.delete_table('newspeak_feed')

        # Removing M2M table for field filters on 'Feed'
        db.delete_table('newspeak_feed_filters')

        # Deleting model 'FeedEntry'
        db.delete_table('newspeak_feedentry')


    models = {
        'newspeak.feed': {
            'Meta': {'object_name': 'Feed'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['newspeak.KeywordFilter']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'newspeak.feedentry': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'FeedEntry'},
            'entry_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['newspeak.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'newspeak.keywordfilter': {
            'Meta': {'object_name': 'KeywordFilter'},
            'filter_summary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['newspeak']