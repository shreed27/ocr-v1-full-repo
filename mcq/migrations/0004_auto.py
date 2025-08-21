# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field qtn_accessible on 'MCQ_Question'
        m2m_table_name = db.shorten_name('mcq_mcq_question_qtn_accessible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_question', models.ForeignKey(orm['mcq.mcq_question'], null=False)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_question_id', 'tprofile_id'])


    def backwards(self, orm):
        # Removing M2M table for field qtn_accessible on 'MCQ_Question'
        db.delete_table(db.shorten_name('mcq_mcq_question_qtn_accessible'))


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
        'mcq.mcq_assignment': {
            'Meta': {'object_name': 'MCQ_Assignment'},
            'asm_assignmentname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'asm_datecreated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'asm_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'asm_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'asm_students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['portal.SProfile']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'mcq.mcq_canvas': {
            'Meta': {'object_name': 'MCQ_Canvas'},
            'axismap': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'drawopts': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'markscheme': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pointlist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"}),
            'rulelist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stdoption': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Optionlist']", 'null': 'True', 'blank': 'True'}),
            'stuanswer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_StudentAnswer']", 'null': 'True', 'blank': 'True'})
        },
        'mcq.mcq_itempool': {
            'Meta': {'object_name': 'MCQ_Itempool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itp_accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'MCQ_Item Pool'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'itp_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'itp_poolname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'itp_teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'mcq.mcq_optionlist': {
            'Meta': {'object_name': 'MCQ_Optionlist'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opl_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'opl_iscorrect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'opl_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'opl_option': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'opl_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"})
        },
        'mcq.mcq_paper': {
            'Meta': {'object_name': 'MCQ_Paper'},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Assignment']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
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
        'mcq.mcq_question': {
            'Meta': {'object_name': 'MCQ_Question'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itempool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Itempool']"}),
            'paper': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mcq.MCQ_Paper']", 'null': 'True', 'blank': 'True'}),
            'qtn_accessible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'MCQ_Question'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['portal.TProfile']"}),
            'qtn_category': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'qtn_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'qtn_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qtn_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qtn_questioncategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_QuestionCategory']", 'null': 'True', 'blank': 'True'}),
            'qty_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qty_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'qtyn_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']"})
        },
        'mcq.mcq_questioncategory': {
            'Meta': {'object_name': 'MCQ_QuestionCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qct_QuestionCategory_parentid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qct_category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qct_description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'qct_sequence': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mcq.mcq_questionimage': {
            'Meta': {'object_name': 'MCQ_QuestionImage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qti_abspath': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'qti_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'qti_digest': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'qti_imagename': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qti_iscorrect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"})
        },
        'mcq.mcq_studentachocexam': {
            'Meta': {'object_name': 'MCQ_StudentAchocExam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sae_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sae_optionlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Optionlist']", 'null': 'True'}),
            'sae_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"}),
            'sae_student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"}),
            'sae_student_answer_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mcq.MCQ_QuestionImage']", 'symmetrical': 'False'})
        },
        'mcq.mcq_studentanswer': {
            'Meta': {'object_name': 'MCQ_StudentAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optionlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Optionlist']", 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"}),
            'sta_closeness': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sta_feedback': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'sta_feedback_code': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sta_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sta_pointmarklist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sta_taked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sta_timeleft': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'sta_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'stuansimages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mcq.MCQ_QuestionImage']", 'symmetrical': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"})
        },
        'mcq.mcq_studentretakeanswer': {
            'Meta': {'object_name': 'MCQ_StudentRetakeAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'srta_mark': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'srta_optionlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Optionlist']", 'null': 'True'}),
            'srta_pointmarklist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'srta_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Question']"}),
            'srta_stuansimages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mcq.MCQ_QuestionImage']", 'symmetrical': 'False'}),
            'srta_student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"}),
            'srta_taked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'srta_timeleft': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'srta_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'mcq.mcq_studentretakentracking': {
            'Meta': {'object_name': 'MCQ_StudentReTakenTracking'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'strt_assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Assignment']"}),
            'strt_paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Paper']"}),
            'strt_student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"}),
            'strt_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'mcq.mcq_studenttakentracking': {
            'Meta': {'object_name': 'MCQ_StudentTakenTracking'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stt_assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Assignment']"}),
            'stt_paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mcq.MCQ_Paper']"}),
            'stt_student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.SProfile']"}),
            'stt_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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

    complete_apps = ['mcq']