# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Years'
        db.create_table('entity_years', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('yearname', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('entity', ['Years'])

        # Adding model 'Levels'
        db.create_table('entity_levels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('levelname', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('entity', ['Levels'])

        # Adding model 'Subjects'
        db.create_table('entity_subjects', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subjectname', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('entity', ['Subjects'])

        # Adding model 'Randomcode'
        db.create_table('entity_randomcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('randomcode', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('entity', ['Randomcode'])


    def backwards(self, orm):
        # Deleting model 'Years'
        db.delete_table('entity_years')

        # Deleting model 'Levels'
        db.delete_table('entity_levels')

        # Deleting model 'Subjects'
        db.delete_table('entity_subjects')

        # Deleting model 'Randomcode'
        db.delete_table('entity_randomcode')


    models = {
        'entity.levels': {
            'Meta': {'object_name': 'Levels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levelname': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'entity.randomcode': {
            'Meta': {'object_name': 'Randomcode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'randomcode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'entity.subjects': {
            'Meta': {'object_name': 'Subjects'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subjectname': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'entity.years': {
            'Meta': {'object_name': 'Years'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'yearname': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['entity']