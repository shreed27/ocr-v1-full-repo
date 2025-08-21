# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MCQ_Assignment'
        db.create_table('mcq_mcq_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asm_assignmentname', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('asm_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('asm_datecreated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('asm_deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_Assignment'])

        # Adding M2M table for field asm_students on 'MCQ_Assignment'
        m2m_table_name = db.shorten_name('mcq_mcq_assignment_asm_students')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_assignment', models.ForeignKey(orm['mcq.mcq_assignment'], null=False)),
            ('sprofile', models.ForeignKey(orm['portal.sprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_assignment_id', 'sprofile_id'])

        # Adding model 'MCQ_Paper'
        db.create_table('mcq_mcq_paper', (
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
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Assignment'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_Paper'])

        # Adding model 'MCQ_Itempool'
        db.create_table('mcq_mcq_itempool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('itp_poolname', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('itp_teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('itp_description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_Itempool'])

        # Adding model 'MCQ_QuestionCategory'
        db.create_table('mcq_mcq_questioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qct_category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qct_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('qct_sequence', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('qct_QuestionCategory_parentid', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mcq', ['MCQ_QuestionCategory'])

        # Adding model 'MCQ_Question'
        db.create_table('mcq_mcq_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qtn_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qtn_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('qtn_category', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('qtyn_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('itempool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Itempool'])),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'])),
            ('qtn_questioncategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_QuestionCategory'], null=True, blank=True)),
            ('qty_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('qty_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('qtn_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mcq', ['MCQ_Question'])

        # Adding M2M table for field paper on 'MCQ_Question'
        m2m_table_name = db.shorten_name('mcq_mcq_question_paper')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_question', models.ForeignKey(orm['mcq.mcq_question'], null=False)),
            ('mcq_paper', models.ForeignKey(orm['mcq.mcq_paper'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_question_id', 'mcq_paper_id'])

        # Adding model 'MCQ_Optionlist'
        db.create_table('mcq_mcq_optionlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('opl_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('opl_description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('opl_option', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('opl_iscorrect', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('opl_question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Question'])),
        ))
        db.send_create_signal('mcq', ['MCQ_Optionlist'])

        # Adding model 'MCQ_QuestionImage'
        db.create_table('mcq_mcq_questionimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qti_imagename', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qti_description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('qti_iscorrect', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('qti_abspath', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Question'])),
            ('qti_digest', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_QuestionImage'])

        # Adding model 'MCQ_StudentTakenTracking'
        db.create_table('mcq_mcq_studenttakentracking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stt_student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('stt_assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Assignment'])),
            ('stt_paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Paper'])),
            ('stt_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('mcq', ['MCQ_StudentTakenTracking'])

        # Adding model 'MCQ_StudentReTakenTracking'
        db.create_table('mcq_mcq_studentretakentracking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('strt_student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('strt_assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Assignment'])),
            ('strt_paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Paper'])),
            ('strt_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('mcq', ['MCQ_StudentReTakenTracking'])

        # Adding model 'MCQ_StudentRetakeAnswer'
        db.create_table('mcq_mcq_studentretakeanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('srta_student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('srta_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('srta_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('srta_pointmarklist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('srta_optionlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Optionlist'], null=True)),
            ('srta_question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Question'])),
            ('srta_timeleft', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('srta_taked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mcq', ['MCQ_StudentRetakeAnswer'])

        # Adding M2M table for field srta_stuansimages on 'MCQ_StudentRetakeAnswer'
        m2m_table_name = db.shorten_name('mcq_mcq_studentretakeanswer_srta_stuansimages')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_studentretakeanswer', models.ForeignKey(orm['mcq.mcq_studentretakeanswer'], null=False)),
            ('mcq_questionimage', models.ForeignKey(orm['mcq.mcq_questionimage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_studentretakeanswer_id', 'mcq_questionimage_id'])

        # Adding model 'MCQ_StudentAnswer'
        db.create_table('mcq_mcq_studentanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('sta_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sta_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('sta_pointmarklist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('optionlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Optionlist'], null=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Question'])),
            ('sta_timeleft', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('sta_taked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sta_closeness', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('sta_feedback', self.gf('django.db.models.fields.TextField')(max_length=255)),
            ('sta_feedback_code', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_StudentAnswer'])

        # Adding M2M table for field stuansimages on 'MCQ_StudentAnswer'
        m2m_table_name = db.shorten_name('mcq_mcq_studentanswer_stuansimages')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_studentanswer', models.ForeignKey(orm['mcq.mcq_studentanswer'], null=False)),
            ('mcq_questionimage', models.ForeignKey(orm['mcq.mcq_questionimage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_studentanswer_id', 'mcq_questionimage_id'])

        # Adding model 'MCQ_StudentAchocExam'
        db.create_table('mcq_mcq_studentachocexam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sae_student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.SProfile'])),
            ('sae_question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Question'])),
            ('sae_mark', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sae_optionlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mcq.MCQ_Optionlist'], null=True)),
        ))
        db.send_create_signal('mcq', ['MCQ_StudentAchocExam'])

        # Adding M2M table for field sae_student_answer_images on 'MCQ_StudentAchocExam'
        m2m_table_name = db.shorten_name('mcq_mcq_studentachocexam_sae_student_answer_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mcq_studentachocexam', models.ForeignKey(orm['mcq.mcq_studentachocexam'], null=False)),
            ('mcq_questionimage', models.ForeignKey(orm['mcq.mcq_questionimage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mcq_studentachocexam_id', 'mcq_questionimage_id'])


    def backwards(self, orm):
        # Deleting model 'MCQ_Assignment'
        db.delete_table('mcq_mcq_assignment')

        # Removing M2M table for field asm_students on 'MCQ_Assignment'
        db.delete_table(db.shorten_name('mcq_mcq_assignment_asm_students'))

        # Deleting model 'MCQ_Paper'
        db.delete_table('mcq_mcq_paper')

        # Deleting model 'MCQ_Itempool'
        db.delete_table('mcq_mcq_itempool')

        # Deleting model 'MCQ_QuestionCategory'
        db.delete_table('mcq_mcq_questioncategory')

        # Deleting model 'MCQ_Question'
        db.delete_table('mcq_mcq_question')

        # Removing M2M table for field paper on 'MCQ_Question'
        db.delete_table(db.shorten_name('mcq_mcq_question_paper'))

        # Deleting model 'MCQ_Optionlist'
        db.delete_table('mcq_mcq_optionlist')

        # Deleting model 'MCQ_QuestionImage'
        db.delete_table('mcq_mcq_questionimage')

        # Deleting model 'MCQ_StudentTakenTracking'
        db.delete_table('mcq_mcq_studenttakentracking')

        # Deleting model 'MCQ_StudentReTakenTracking'
        db.delete_table('mcq_mcq_studentretakentracking')

        # Deleting model 'MCQ_StudentRetakeAnswer'
        db.delete_table('mcq_mcq_studentretakeanswer')

        # Removing M2M table for field srta_stuansimages on 'MCQ_StudentRetakeAnswer'
        db.delete_table(db.shorten_name('mcq_mcq_studentretakeanswer_srta_stuansimages'))

        # Deleting model 'MCQ_StudentAnswer'
        db.delete_table('mcq_mcq_studentanswer')

        # Removing M2M table for field stuansimages on 'MCQ_StudentAnswer'
        db.delete_table(db.shorten_name('mcq_mcq_studentanswer_stuansimages'))

        # Deleting model 'MCQ_StudentAchocExam'
        db.delete_table('mcq_mcq_studentachocexam')

        # Removing M2M table for field sae_student_answer_images on 'MCQ_StudentAchocExam'
        db.delete_table(db.shorten_name('mcq_mcq_studentachocexam_sae_student_answer_images'))


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
        'mcq.mcq_itempool': {
            'Meta': {'object_name': 'MCQ_Itempool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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