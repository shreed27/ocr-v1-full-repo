# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'QuestionVideo'


        # Adding field 'Question.alt_available'
        db.add_column('question_question', 'alt_available',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Question.alt_stdanswer'
        db.add_column('question_question', 'alt_stdanswer',
                      self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='alt_questions', unique=True, null=True, to=orm['question.StandardAnswer']),
                      keep_default=False)

        # Adding field 'Question.alt_stdanswertext'
        db.add_column('question_question', 'alt_stdanswertext',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_stdanswerhtml'
        db.add_column('question_question', 'alt_stdanswerhtml',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_qtext'
        db.add_column('question_question', 'alt_qtext',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_qhtml'
        db.add_column('question_question', 'alt_qhtml',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_markscheme'
        db.add_column('question_question', 'alt_markscheme',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_infocompleted'
        db.add_column('question_question', 'alt_infocompleted',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Question.alt_imagepointlist'
        db.add_column('question_question', 'alt_imagepointlist',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.alt_min_closeness_band'
        db.add_column('question_question', 'alt_min_closeness_band',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding M2M table for field accessible on 'Question'
        m2m_table_name = db.shorten_name('question_question_accessible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['question.question'], null=False)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['question_id', 'tprofile_id'])

        # Adding field 'StandardAnswer.alternative'
        db.add_column('question_standardanswer', 'alternative',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'QuestionVideo'

        # Deleting field 'Question.alt_available'
        db.delete_column('question_question', 'alt_available')

        # Deleting field 'Question.alt_stdanswer'
        db.delete_column('question_question', 'alt_stdanswer_id')

        # Deleting field 'Question.alt_stdanswertext'
        db.delete_column('question_question', 'alt_stdanswertext')

        # Deleting field 'Question.alt_stdanswerhtml'
        db.delete_column('question_question', 'alt_stdanswerhtml')

        # Deleting field 'Question.alt_qtext'
        db.delete_column('question_question', 'alt_qtext')

        # Deleting field 'Question.alt_qhtml'
        db.delete_column('question_question', 'alt_qhtml')

        # Deleting field 'Question.alt_markscheme'
        db.delete_column('question_question', 'alt_markscheme')

        # Deleting field 'Question.alt_infocompleted'
        db.delete_column('question_question', 'alt_infocompleted')

        # Deleting field 'Question.alt_imagepointlist'
        db.delete_column('question_question', 'alt_imagepointlist')

        # Deleting field 'Question.alt_min_closeness_band'
        db.delete_column('question_question', 'alt_min_closeness_band')

        # Removing M2M table for field accessible on 'Question'
        db.delete_table(db.shorten_name('question_question_accessible'))

        # Deleting field 'StandardAnswer.alternative'
        db.delete_column('question_standardanswer', 'alternative')


    models = {
        'assignment.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'assignmentname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['portal.SProfile']", 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
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
        'classroom.classroom': {
            'Meta': {'object_name': 'Classroom'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roomname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'entity.levels': {
            'Meta': {'object_name': 'Levels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levelname': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
        },
        'itempool.itempool': {
            'Meta': {'object_name': 'Itempool'},
            'accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'Item Pool'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'paper.paper': {
            'Meta': {'object_name': 'Paper'},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['assignment.Assignment']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Levels']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'papername': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'passpoint': ('django.db.models.fields.IntegerField', [], {}),
            'ptype': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'questionseq': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Subjects']", 'null': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Years']", 'null': 'True', 'blank': 'True'})
        },
        'portal.sprofile': {
            'Meta': {'object_name': 'SProfile'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classroom.Classroom']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'portal.tprofile': {
            'Meta': {'object_name': 'TProfile'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'classrooms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['classroom.Classroom']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'question.question': {
            'Meta': {'object_name': 'Question'},
            'accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'Question'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'alt_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alt_imagepointlist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'alt_infocompleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'alt_markscheme': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'alt_min_closeness_band': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'alt_qhtml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'alt_qtext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'alt_stdanswer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'alt_questions'", 'unique': 'True', 'null': 'True', 'to': "orm['question.StandardAnswer']"}),
            'alt_stdanswerhtml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'alt_stdanswertext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagepointlist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'infocompleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'itempool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['itempool.Itempool']"}),
            'markscheme': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'min_closeness_band': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'paper': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['paper.Paper']", 'null': 'True', 'blank': 'True'}),
            'qhtml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'qtext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qtype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'stdanswer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'questions'", 'unique': 'True', 'null': 'True', 'to': "orm['question.StandardAnswer']"}),
            'stdanswerhtml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stdanswertext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'question.questionimage': {
            'Meta': {'object_name': 'QuestionImage'},
            'abspath': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagename': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'iscorrect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['question.Question']"})
        },
        'question.standardanswer': {
            'Meta': {'object_name': 'StandardAnswer'},
            'alternative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fullmark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imgrulelist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pointlist': ('django.db.models.fields.TextField', [], {}),
            'rulelist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sentencelist': ('django.db.models.fields.TextField', [], {}),
            'textfdist': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['question']