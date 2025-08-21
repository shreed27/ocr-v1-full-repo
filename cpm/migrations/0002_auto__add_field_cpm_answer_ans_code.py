# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CPM_Answer.ans_code'
        db.add_column('cpm_cpm_answer', 'ans_code',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CPM_Answer.ans_code'
        db.delete_column('cpm_cpm_answer', 'ans_code')


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
        'cpm.cpm_answer': {
            'Meta': {'object_name': 'CPM_Answer'},
            'ans_answer': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'ans_code': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'ans_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_Question']"})
        },
        'cpm.cpm_assignment': {
            'Meta': {'object_name': 'CPM_Assignment'},
            'asm_assignmentname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'asm_datecreated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'asm_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'asm_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'asm_students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['portal.SProfile']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'cpm.cpm_itempool': {
            'Meta': {'object_name': 'CPM_Itempool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itp_accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'CPM_Item Pool'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'itp_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'itp_poolname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'itp_teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'cpm.cpm_paper': {
            'Meta': {'object_name': 'CPM_Paper'},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_Assignment']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Levels']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'ppr_duration': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ppr_papername': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ppr_papertype': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ppr_passpoint': ('django.db.models.fields.IntegerField', [], {}),
            'ppr_questionseq': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ppr_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Subjects']", 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Years']", 'null': 'True', 'blank': 'True'})
        },
        'cpm.cpm_question': {
            'Meta': {'object_name': 'CPM_Question'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itempool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_Itempool']"}),
            'paper': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cpm.CPM_Paper']", 'null': 'True', 'blank': 'True'}),
            'qtn_accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'CPM_Question'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'qtn_category': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'qtn_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'qtn_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qtn_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qtn_questioncategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'qty_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qty_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qtyn_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'cpm.cpm_questioncategory': {
            'Meta': {'object_name': 'CPM_QuestionCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qct_QuestionCategory_parentid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qct_category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qct_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'qct_sequence': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qct_teacher': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['portal.TProfile']", 'null': 'True', 'blank': 'True'})
        },
        'cpm.cpm_studentanswer': {
            'Meta': {'object_name': 'CPM_StudentAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_Question']"}),
            'sta_answer': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'sta_closeness': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sta_feedback': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'sta_feedback_code': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sta_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sta_paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cpm.CPM_Paper']"}),
            'sta_pointmarklist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sta_questionseqcode': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'sta_taked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sta_timeleft': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'sta_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"})
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
        }
    }

    complete_apps = ['cpm']