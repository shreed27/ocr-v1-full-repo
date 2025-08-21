from django.db import models
from django.contrib.auth.models import User
from portal.models import TProfile,SProfile
from django.utils.timezone import now
from entity.models import Years, Levels , Subjects
import datetime

# Create your models here.

#=============== Master Table================================================================================

#=============== End of Master Table================================================================================


class MCQ_Assignment(models.Model):
	asm_assignmentname = models.CharField(max_length=20, verbose_name=u'Assignment Name')
	asm_description = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Description')
	asm_students = models.ManyToManyField(SProfile, blank=True, null=True,verbose_name=u'Students')
	teacher = models.ForeignKey(TProfile, verbose_name=u'Teacher')
	asm_datecreated = models.DateTimeField('test date', default=datetime.datetime.now)
	asm_deadline = models.DateTimeField('test deadline', blank=True, null=True)
    	class Meta:
        	verbose_name = u'Assignment'

    	def __unicode__(self):
        	return u'%s' % self.asm_assignmentname


class MCQ_Paper(models.Model):
	ppr_papername = models.CharField(max_length=30, verbose_name=u'Paper Name')
	ppr_papertype = models.CharField(max_length=20, verbose_name=u'Paper Type')
	ppr_duration = models.CharField(max_length=20, verbose_name=u'Test Duration')
	ppr_passpoint = models.IntegerField(verbose_name=u'Pass Point')
	ppr_total = models.IntegerField(default=0, editable=False, verbose_name=u'Paper Total')
	ppr_questionseq = models.TextField(null=True, blank=True, verbose_name=u'Question Seq')
	year = models.ForeignKey(Years, null=True, blank=True)
	subject = models.ForeignKey(Subjects, null=True, blank=True, verbose_name=u'Subject')
	level = models.ForeignKey(Levels, null=True, blank=True, verbose_name=u'Level')
	owner = models.ForeignKey(User, verbose_name=u'Owner')
	assignment = models.ForeignKey(MCQ_Assignment, verbose_name=u'Assignment', blank=True, null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
        	return self.ppr_papername
	class Meta:
		verbose_name_plural = "Paper"




class MCQ_Itempool(models.Model):
	itp_poolname = models.CharField(max_length=30, blank=True, null=True,
		                verbose_name='Pool Name')
	itp_teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
	itp_description = models.CharField(max_length=100, blank=True, null=True,
		                   verbose_name='Description')
	 # Teachers who can access this item pool
	itp_accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='MCQ_Item Pool')

	class Meta:
		verbose_name = u'Item Pool'

	def __unicode__(self):
		return u'[Itempool:%s]' % self.itp_poolname


class MCQ_QuestionCategory(models.Model):
	qct_category = models.CharField(max_length=30, verbose_name='Category Name')
	qct_description = models.CharField(max_length=1000, verbose_name=u'Description',
		                   blank=True, null=True)
	qct_teacher = models.ManyToManyField(TProfile, blank=True, null=True,verbose_name=u'Teachers')
	qct_sequence = models.IntegerField(default=0)
	qct_teacher = models.ManyToManyField(TProfile, blank=True, null=True,verbose_name=u'Teachers')
	
	qct_QuestionCategory_parentid = models.IntegerField(default=0)
	def __unicode__(self):
		return u'[ID: %s , Category:%s]' % (self.id , self.qct_category)

class MCQ_Question(models.Model):
	QUESTIONCOMPLETED = 1
	STDANSWERCOMPLETED = 2
	MARKSCHEMECOMPLETED = 4
	ALLCOMPLETED = 7
	qtn_name = models.CharField(max_length=30, verbose_name='Question Name')
	qtn_description = models.CharField(max_length=1000, verbose_name=u'description',
		                   blank=True, null=True)
	qtn_category = models.CharField(max_length=30, verbose_name='category',
		                blank=True, null=True)
	qtyn_type = models.CharField(max_length=20, verbose_name=u'Question Type',
		             blank=True, null=True)
	itempool = models.ForeignKey(MCQ_Itempool, verbose_name=u'Item Pool')
	paper = models.ManyToManyField(MCQ_Paper, verbose_name=u'Paper',
		                   blank=True, null=True)
	teacher = models.ForeignKey(TProfile, verbose_name=u'Teacher')
	qtn_questioncategory = models.ForeignKey(MCQ_QuestionCategory, verbose_name=u'Category',
		                blank=True, null=True)
	qty_text = models.TextField(blank=True, null=True,
                             verbose_name=u'Question Text')
    	qty_html = models.TextField(blank=True, null=True,
                             verbose_name=u'Question HTML')
	qtn_mark = models.IntegerField(default=0)
	qtn_accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='MCQ_Question')
	class Meta:
		verbose_name = u'Question'

	def __unicode__(self):
		return u'[Question:%s,Category:%s,Type:%s]' % (self.qtn_name, self.qtn_category, self.qtyn_type)



class MCQ_Optionlist(models.Model):
	
	opl_name = models.CharField(max_length=30, verbose_name='Answer Name')
	opl_description = models.CharField(max_length=1000, verbose_name=u'Description',
		                   blank=True, null=True)
	opl_option = models.CharField(max_length=1000, verbose_name=u'Option',
		                   blank=True, null=True)
	opl_iscorrect = models.BooleanField(verbose_name=u'Is Correct')
	opl_question = models.ForeignKey(MCQ_Question, verbose_name=u'Question')
	
	
	class Meta:
		verbose_name = u'Answer'

	def __unicode__(self):
		return u'[Name:%s,Is Corrrect:%s]' % (self.opl_name,  self.opl_iscorrect)

	def __iter__(self):
		return [ self.opl_name, 
		         self.opl_description, 
		         self.opl_option, 
		         self.opl_iscorrect, 
		         self.opl_question] 

class MCQ_QuestionImage(models.Model):
	qti_imagename = models.CharField(max_length=30, verbose_name=u'Image Name')
	qti_description = models.CharField(max_length=100, verbose_name=u'Description', blank=True, null=True)
	qti_iscorrect = models.BooleanField(verbose_name=u'Is Correct')
	qti_abspath = models.CharField(max_length=50, verbose_name=u'Absulte Path')
	question = models.ForeignKey(MCQ_Question, verbose_name=u'Question')
	qti_digest = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'md5')

	class Meta:
		verbose_name = u'Question Image'

	def __unicode__(self):
		return u'[Image Name:%s, IsCorrect:%s, Abspath:%s]' % (self.qti_imagename, self.qti_iscorrect, self.qti_abspath)
class MCQ_StudentTakenTracking(models.Model):
	stt_student = models.ForeignKey(SProfile)
	stt_assignment = models.ForeignKey(MCQ_Assignment)
	stt_paper = models.ForeignKey(MCQ_Paper)
	stt_timestamp = models.DateTimeField('time taked', default=now)
	def __unicode__(self):
		return u'Tracking Assingment taken' + str(self.id)

class MCQ_StudentReTakenTracking(models.Model):
	strt_student = models.ForeignKey(SProfile)
	strt_assignment = models.ForeignKey(MCQ_Assignment)
	strt_paper = models.ForeignKey(MCQ_Paper)
	strt_timestamp = models.DateTimeField('time taked', default=now)
	def __unicode__(self):
		return u'Tracking Assingment taken' + str(self.id)
class MCQ_StudentRetakeAnswer(models.Model):
	srta_student = models.ForeignKey(SProfile)
	srta_mark = models.IntegerField(default=0)
	srta_timestamp = models.DateTimeField('time taked', default=now)
	srta_pointmarklist = models.TextField(null=True, blank=True)
	srta_optionlist = models.ForeignKey(MCQ_Optionlist,null=True,)
	srta_question = models.ForeignKey(MCQ_Question)
	srta_paper = models.ForeignKey(MCQ_Paper)
	srta_timeleft = models.IntegerField(default=-1)
	srta_taked = models.BooleanField(verbose_name=u'Question Taked')
	srta_stuansimages = models.ManyToManyField(MCQ_QuestionImage, verbose_name=u'stuansimages')

	def __unicode__(self):
		return u'StudentAnswerSheet_' + str(self.srta_question.qtn_name) + u'_' + self.srta_student.user.username + '-----' + str(self.id)



class MCQ_StudentAnswer(models.Model):
	student = models.ForeignKey(SProfile)
	sta_mark = models.IntegerField(default=0)
	sta_timestamp = models.DateTimeField('time taked', default=now)
	sta_pointmarklist = models.TextField(null=True, blank=True)
	optionlist = models.ForeignKey(MCQ_Optionlist,null=True,)
	question = models.ForeignKey(MCQ_Question)
	sta_paper = models.ForeignKey(MCQ_Paper)
	sta_timeleft = models.IntegerField(default=-1)
	sta_taked = models.BooleanField(verbose_name=u'Question Taked')
	stuansimages = models.ManyToManyField(MCQ_QuestionImage, verbose_name=u'stuansimages')
	sta_closeness = models.FloatField(default=0.0)
	sta_feedback = models.TextField(max_length=255)
	sta_feedback_code = models.TextField(null=True)

	def __unicode__(self):
		return u'StudentAnswerSheet_' + str(self.question.qtn_name) + u'_' + self.student.user.username + '-----' + str(self.id)

# Temporary table for student achoc request exam. and it will delete all the time.
class MCQ_StudentAchocExam(models.Model):
	sae_student = models.ForeignKey(SProfile)
	sae_question = models.ForeignKey(MCQ_Question)
	sae_student_answer_images = models.ManyToManyField(MCQ_QuestionImage, verbose_name=u'stuansimages')
	sae_mark = models.IntegerField(default=0)
	sae_optionlist = models.ForeignKey(MCQ_Optionlist,null=True,)
	


class MCQ_Canvas(models.Model):
    question = models.ForeignKey(MCQ_Question, verbose_name=u'Question')
    stdoption = models.ForeignKey(MCQ_Optionlist, null=True, blank=True)
    stuanswer = models.ForeignKey(MCQ_StudentAnswer, null=True, blank=True)
    name = models.CharField(max_length=20)
    axismap = models.TextField(null=True, blank=True)
    drawopts = models.TextField(null=True, blank=True)
    rulelist = models.TextField(null=True, blank=True)
    markscheme = models.TextField(null=True, blank=True)
    pointlist = models.TextField(null=True, blank=True)
    mark = models.IntegerField(default=0)
 
    def __unicode__(self):
        return u'Canvas id:%d name:%s question:%s std:%s stu:%s' % (self.id, self.name, self.question, self.stdanswer, self.stuanswer)



class MCQ_OptionCanvas(models.Model):
    option = models.ForeignKey(MCQ_Optionlist, null=True, blank=True)
    name = models.CharField(max_length=20)
    axismap = models.TextField(null=True, blank=True)
    drawopts = models.TextField(null=True, blank=True)
    rulelist = models.TextField(null=True, blank=True)
    markscheme = models.TextField(null=True, blank=True)
    pointlist = models.TextField(null=True, blank=True)
    mark = models.IntegerField(default=0)
 
    def __unicode__(self):
        return u'Canvas id:%d name:%s optoin:%s  ' % (self.id, self.name, self.option)

class MCQ_OptionImage(models.Model):
	qti_imagename = models.CharField(max_length=30, verbose_name=u'Image Name')
	qti_description = models.CharField(max_length=100, verbose_name=u'Description', blank=True, null=True)
	qti_iscorrect = models.BooleanField(verbose_name=u'Is Correct')
	qti_abspath = models.CharField(max_length=50, verbose_name=u'Absulte Path')
	option = models.ForeignKey(MCQ_Optionlist, verbose_name=u'Option')
	qti_digest = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'md5')

	class Meta:
		verbose_name = u'Question Image'

	def __unicode__(self):
		return u'[Image Name:%s, IsCorrect:%s, Abspath:%s]' % (self.qti_imagename, self.qti_iscorrect, self.qti_abspath)























