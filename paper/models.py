# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from assignment.models import Assignment
from entity.models import Years, Subjects, Levels


class Paper(models.Model):
    papername = models.CharField(max_length=30, verbose_name=u'Paper Name')
    assignment = models.ForeignKey(Assignment, verbose_name=u'Assignment', blank=True,
                                   null=True, on_delete=models.SET_NULL)
    ptype = models.CharField(max_length=20, verbose_name=u'Paper Type')
    duration = models.CharField(max_length=20, verbose_name=u'Test Duration')
    owner = models.ForeignKey(User, verbose_name=u'Owner')
    passpoint = models.IntegerField(verbose_name=u'Pass Point')
    total = models.IntegerField(default=0, editable=False, verbose_name=u'Paper Total')
    questionseq = models.TextField(null=True, blank=True, verbose_name=u'Question Seq')
    year = models.ForeignKey(Years, null=True, blank=True, verbose_name=u'Year')
    subject = models.ForeignKey(Subjects, null=True, blank=True, verbose_name=u'Subject')
    level = models.ForeignKey(Levels, null=True, blank=True, verbose_name=u'Level')
   
    
    class Meta:
        verbose_name = u'Paper'

    def __unicode__(self):
        return u'[Paper:%s,Type:%s,Owner:%s]' % (self.papername, self.ptype, self.owner)
