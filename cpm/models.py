from django.db import models
from django.contrib.auth.models import User
from portal.models import TProfile,SProfile
from django.utils.timezone import now
from entity.models import Years, Levels , Subjects
import datetime



# Create your models here.

#=============== Master Table================================================================================

#=============== End of Master Table================================================================================


class CPM_Assignment(models.Model):
	asm_assignmentname = models.CharField(max_length=20, verbose_name='Assignment Name')
	asm_description = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Description')
	asm_students = models.ManyToManyField(SProfile, blank=True, null=True,verbose_name='Students')
	teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
	asm_datecreated = models.DateTimeField('test date', default=datetime.datetime.now)
	asm_deadline = models.DateTimeField('test deadline', blank=True, null=True)
    	class Meta:
        	verbose_name = 'Assignment'

    	def __unicode__(self):
        	return '%s' % self.asm_assignmentname


class CPM_Paper(models.Model):
	ppr_papername = models.CharField(max_length=30, verbose_name='Paper Name')
	ppr_papertype = models.CharField(max_length=20, verbose_name='Paper Type')
	ppr_duration = models.CharField(max_length=20, verbose_name='Test Duration')
	ppr_passpoint = models.IntegerField(verbose_name='Pass Point')
	ppr_total = models.IntegerField(default=0, editable=False, verbose_name='Paper Total')
	ppr_questionseq = models.TextField(null=True, blank=True, verbose_name='Question Seq')
	year = models.ForeignKey(Years, null=True, blank=True)
	subject = models.ForeignKey(Subjects, null=True, blank=True, verbose_name='Subject')
	level = models.ForeignKey(Levels, null=True, blank=True, verbose_name='Level')
	owner = models.ForeignKey(User, verbose_name='Owner')
	assignment = models.ForeignKey(CPM_Assignment, verbose_name='Assignment', blank=True, null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
        	return self.ppr_papername
	class Meta:
		verbose_name_plural = "Paper"




class CPM_Itempool(models.Model):
	itp_poolname = models.CharField(max_length=30, blank=True, null=True,
		                verbose_name='Pool Name')
	itp_teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
	itp_description = models.CharField(max_length=100, blank=True, null=True,
		                   verbose_name='Description')
	 # Teachers who can access this item pool
	itp_accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='CPM_Item Pool')

	class Meta:
		verbose_name = 'Item Pool'

	def __unicode__(self):
		return '[Itempool:%s]' % self.itp_poolname


class CPM_QuestionCategory(models.Model):
	qct_category = models.CharField(max_length=30, verbose_name='Category Name')
	qct_description = models.CharField(max_length=1000, verbose_name='Description',
		                   blank=True, null=True)
	qct_teacher = models.ManyToManyField(TProfile, blank=True, null=True,verbose_name='Teachers')
	qct_sequence = models.IntegerField(default=0)
	qct_teacher = models.ManyToManyField(TProfile, blank=True, null=True,verbose_name='Teachers')
	
	qct_QuestionCategory_parentid = models.IntegerField(default=0)
	def __unicode__(self):
		return '[ID: %s , Category:%s]' % (self.id , self.qct_category)

class CPM_Question(models.Model):
	QUESTIONCOMPLETED = 1
	STDANSWERCOMPLETED = 2
	MARKSCHEMECOMPLETED = 4
	ALLCOMPLETED = 7
	qtn_name = models.CharField(max_length=30, verbose_name='Question Name')
	qtn_description = models.CharField(max_length=1000, verbose_name='description',
		                   blank=True, null=True)
	qtn_category = models.CharField(max_length=30, verbose_name='category',
		                blank=True, null=True)
	qtyn_type = models.CharField(max_length=20, verbose_name='Question Type',
		             blank=True, null=True)
	itempool = models.ForeignKey(CPM_Itempool, verbose_name='Item Pool')
	paper = models.ManyToManyField(CPM_Paper, verbose_name='Paper',
		                   blank=True, null=True)
	teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
	qtn_questioncategory = models.ForeignKey(CPM_QuestionCategory, verbose_name='Category',
		                blank=True, null=True)
	qty_text = models.TextField(blank=True, null=True,
                             verbose_name='Question Text')
    	qty_html = models.TextField(blank=True, null=True,
                             verbose_name='Question HTML')
	qtn_mark = models.IntegerField(default=0)
	qtn_accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='CPM_Question')
	class Meta:
		verbose_name = 'Question'

	def __unicode__(self):
		return '[Question:%s,Category:%s,Type:%s]' % (self.qtn_name, self.qtn_category, self.qtyn_type)
class CPM_Answer(models.Model):
	ans_code = models.TextField(max_length=255)
	ans_mark = models.IntegerField(default=0)
	question = models.ForeignKey(CPM_Question)
	ans_mark = models.IntegerField(default=0)
	ans_answer= models.TextField(max_length=255) 

class CPM_StudentAnswer(models.Model):
	student = models.ForeignKey(SProfile)
	sta_mark = models.IntegerField(default=0)
	sta_timestamp = models.DateTimeField('time taked', default=now)
	sta_pointmarklist = models.TextField(null=True, blank=True)
	sta_questionseqcode= models.TextField(max_length=255) # This is the code refering to which cloze seq
	sta_answer= models.TextField(max_length=255)
	question = models.ForeignKey(CPM_Question)
	sta_paper = models.ForeignKey(CPM_Paper)
	sta_timeleft = models.IntegerField(default=-1)
	sta_taked = models.BooleanField(verbose_name='Question Taked')
	#stuansimages = models.ManyToManyField(CPM_QuestionImage, verbose_name=u'stuansimages')
	sta_closeness = models.FloatField(default=0.0)
	sta_feedback = models.TextField(max_length=255)
	sta_feedback_code = models.TextField(null=True)

	def __unicode__(self):
		return 'StudentAnswerSheet_' + str(self.question.qtn_name) + '_' + self.student.user.username + '-----' + str(self.id)
























