# coding: utf-8
from django.db import models
from itempool.models import Itempool
from paper.models import Paper
from portal.models import TProfile
import settings
import os

def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    file = filename.split('.')[0]
    filename = "std__%s__video.%s" % (file, ext)
    return os.path.join('static', 'questionvideos', filename)


class StandardAnswer(models.Model):
    name = models.CharField(max_length=50)
    fullmark = models.IntegerField(default=0)
    textfdist = models.TextField()
    sentencelist = models.TextField()
    rulelist = models.TextField(null=True, blank=True)
    imgrulelist = models.TextField(null=True, blank=True)
    pointlist = models.TextField()
    alternative = models.BooleanField(default=False, verbose_name='Is alternative Standard Answer?')

    def __unicode__(self):
        return 'StandardAnswer_%s' % self.name


class Question(models.Model):
    QUESTIONCOMPLETED = 1
    STDANSWERCOMPLETED = 2
    MARKSCHEMECOMPLETED = 4
    ALLCOMPLETED = 7
    qname = models.CharField(max_length=100, verbose_name='Question Name')
    description = models.CharField(max_length=1000, verbose_name='description',
                                   blank=True, null=True)
    category = models.CharField(max_length=30, verbose_name='category',
                                blank=True, null=True)
    qtype = models.CharField(max_length=20, verbose_name='Question Type',
                             blank=True, null=True)
    itempool = models.ForeignKey(Itempool, verbose_name='Item Pool')
    paper = models.ManyToManyField(Paper, verbose_name='Paper',
                                   blank=True, null=True)
    teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
    stdanswer = models.OneToOneField(StandardAnswer, blank=True, null=True,
                                     verbose_name='Standard Answer',
                                     related_name='questions')
    stdanswertext = models.TextField(blank=True, null=True,
                                     verbose_name='Standard Answer Text')
    stdanswerhtml = models.TextField(blank=True, null=True,
                                     verbose_name='Standard Answer HTML')
    qtext = models.TextField(blank=True, null=True,
                             verbose_name='Question Text')
    qhtml = models.TextField(blank=True, null=True,
                             verbose_name='Question HTML')
    markscheme = models.TextField(blank=True, null=True,
                                  verbose_name='Mark Scheme')
    infocompleted = models.IntegerField(default=0)
    imagepointlist = models.TextField(null=True, blank=True)
    min_closeness_band = models.IntegerField(default=0)
    accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='Question')

    # alternate answer fields
    alt_available = models.BooleanField(default=False, verbose_name="Is alternative answer available")

    alt_stdanswer = models.OneToOneField(StandardAnswer, blank=True, null=True,
                                     verbose_name='Alternate Standard Answer',
                                     related_name='alt_questions')
    alt_stdanswertext = models.TextField(blank=True, null=True,
                                     verbose_name='Alternate Standard Answer Text')
    alt_stdanswerhtml = models.TextField(blank=True, null=True,
                                     verbose_name='Alternate Standard Answer HTML')
    alt_qtext = models.TextField(blank=True, null=True,
                             verbose_name='Alternate Question Text')
    alt_qhtml = models.TextField(blank=True, null=True,
                             verbose_name='Alternate Question HTML')
    alt_markscheme = models.TextField(blank=True, null=True,
                                  verbose_name='Alternate Mark Scheme')
    alt_infocompleted = models.IntegerField(default=0)
    alt_imagepointlist = models.TextField(null=True, blank=True)
    alt_min_closeness_band = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Question'

    def __unicode__(self):
        return '[Question:%s,Category:%s,Type:%s]' % (self.qname, self.category, self.qtype)

    #


class QuestionImage(models.Model):
    imagename = models.CharField(max_length=30, verbose_name='Image Name')
    description = models.CharField(max_length=100, verbose_name='Description', blank=True, null=True)
    iscorrect = models.BooleanField(verbose_name='Is Correct')
    abspath = models.CharField(max_length=50, verbose_name='Absulte Path')
    question = models.ForeignKey(Question, verbose_name='Question')
    digest = models.CharField(max_length=100, blank=True, null=True, verbose_name='md5')

    class Meta:
        verbose_name = 'Question Image'

    def __unicode__(self):
        return '[Image Name:%s, IsCorrect:%s, Abspath:%s]' % (self.imagename, self.iscorrect, self.abspath)


class QuestionVideo(models.Model):
    question = models.ForeignKey(Question, verbose_name='Question')
    videoupload = models.FileField(upload_to=content_file_name)
    src = models.CharField(max_length=400, verbose_name='Video Source')