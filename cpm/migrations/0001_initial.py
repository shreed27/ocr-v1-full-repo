# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CPM_Assignment'
        db.create_table('cpm_cpm_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asm_assignmentname', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('asm_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('asm_datecreated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('asm_deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('cpm', ['CPM_Assignment'])

        # Adding M2M table for field asm_students on 'CPM_Assignment'
        m2m_table_name = db.shorten_name('cpm_cpm_assignment_asm_students')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpm_assignment', models.ForeignKey(orm['cpm.cpm_assignment'], null=False)),
            ('sprofile', models.ForeignKey(orm['portal.sprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cpm_assignment_id', 'sprofile_id'])

        # Adding model 'CPM_Paper'
        db.create_table('cpm_cpm_paper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ppr_papername', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('ppr_papertype', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('ppr_duration', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('ppr_passpoint', self.gf('django.db.models.fields.IntegerField')()),
            ('ppr_total', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ppr_questionseq', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity.Years'], null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity.Subjects'], null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity.Levels'], null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_Assignment'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('cpm', ['CPM_Paper'])

        # Adding model 'CPM_Itempool'
        db.create_table('cpm_cpm_itempool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('itp_poolname', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('itp_teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('itp_description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('cpm', ['CPM_Itempool'])

        # Adding M2M table for field itp_accessible on 'CPM_Itempool'
        m2m_table_name = db.shorten_name('cpm_cpm_itempool_itp_accessible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpm_itempool', models.ForeignKey(orm['cpm.cpm_itempool'], null=False)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cpm_itempool_id', 'tprofile_id'])

        # Adding model 'CPM_QuestionCategory'
        db.create_table('cpm_cpm_questioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qct_category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qct_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('qct_sequence', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('qct_QuestionCategory_parentid', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('cpm', ['CPM_QuestionCategory'])

        # Adding M2M table for field qct_teacher on 'CPM_QuestionCategory'
        m2m_table_name = db.shorten_name('cpm_cpm_questioncategory_qct_teacher')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpm_questioncategory', models.ForeignKey(orm['cpm.cpm_questioncategory'], null=False)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cpm_questioncategory_id', 'tprofile_id'])

        # Adding model 'CPM_Question'
        db.create_table('cpm_cpm_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qtn_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qtn_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('qtn_category', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('qtyn_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('itempool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_Itempool'])),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('qtn_questioncategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_QuestionCategory'], null=True, blank=True)),
            ('qty_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('qty_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('qtn_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('cpm', ['CPM_Question'])

        # Adding M2M table for field paper on 'CPM_Question'
        m2m_table_name = db.shorten_name('cpm_cpm_question_paper')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpm_question', models.ForeignKey(orm['cpm.cpm_question'], null=False)),
            ('cpm_paper', models.ForeignKey(orm['cpm.cpm_paper'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cpm_question_id', 'cpm_paper_id'])

        # Adding M2M table for field qtn_accessible on 'CPM_Question'
        m2m_table_name = db.shorten_name('cpm_cpm_question_qtn_accessible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpm_question', models.ForeignKey(orm['cpm.cpm_question'], null=False)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cpm_question_id', 'tprofile_id'])

        # Adding model 'CPM_Answer'
        db.create_table('cpm_cpm_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_Question'])),
            ('ans_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ans_answer', self.gf('django.db.models.fields.TextField')(max_length=255)),
        ))
        db.send_create_signal('cpm', ['CPM_Answer'])

        # Adding model 'CPM_StudentAnswer'
        db.create_table('cpm_cpm_studentanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('sta_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sta_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('sta_pointmarklist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sta_questionseqcode', self.gf('django.db.models.fields.TextField')(max_length=255)),
            ('sta_answer', self.gf('django.db.models.fields.TextField')(max_length=255)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_Question'])),
            ('sta_paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cpm.CPM_Paper'])),
            ('sta_timeleft', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('sta_taked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sta_closeness', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('sta_feedback', self.gf('django.db.models.fields.TextField')(max_length=255)),
            ('sta_feedback_code', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('cpm', ['CPM_StudentAnswer'])


    def backwards(self, orm):
        # Deleting model 'CPM_Assignment'
        db.delete_table('cpm_cpm_assignment')

        # Removing M2M table for field asm_students on 'CPM_Assignment'
        db.delete_table(db.shorten_name('cpm_cpm_assignment_asm_students'))

        # Deleting model 'CPM_Paper'
        db.delete_table('cpm_cpm_paper')

        # Deleting model 'CPM_Itempool'
        db.delete_table('cpm_cpm_itempool')

        # Removing M2M table for field itp_accessible on 'CPM_Itempool'
        db.delete_table(db.shorten_name('cpm_cpm_itempool_itp_accessible'))

        # Deleting model 'CPM_QuestionCategory'
        db.delete_table('cpm_cpm_questioncategory')

        # Removing M2M table for field qct_teacher on 'CPM_QuestionCategory'
        db.delete_table(db.shorten_name('cpm_cpm_questioncategory_qct_teacher'))

        # Deleting model 'CPM_Question'
        db.delete_table('cpm_cpm_question')

        # Removing M2M table for field paper on 'CPM_Question'
        db.delete_table(db.shorten_name('cpm_cpm_question_paper'))

        # Removing M2M table for field qtn_accessible on 'CPM_Question'
        db.delete_table(db.shorten_name('cpm_cpm_question_qtn_accessible'))

        # Deleting model 'CPM_Answer'
        db.delete_table('cpm_cpm_answer')

        # Deleting model 'CPM_StudentAnswer'
        db.delete_table('cpm_cpm_studentanswer')


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