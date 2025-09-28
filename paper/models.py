# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from assignment.models import Assignment
from entity.models import Years, Subjects, Levels


class Paper(models.Model):
    papername = models.CharField(max_length=30, verbose_name='Paper Name')
    assignment = models.ForeignKey(Assignment, verbose_name='Assignment', blank=True,
                                   null=True, on_delete=models.SET_NULL)
    ptype = models.CharField(max_length=20, verbose_name='Paper Type')
    duration = models.CharField(max_length=20, verbose_name='Test Duration')
    owner = models.ForeignKey(User, verbose_name='Owner')
    passpoint = models.IntegerField(verbose_name='Pass Point')
    total = models.IntegerField(default=0, editable=False, verbose_name='Paper Total')
    questionseq = models.TextField(null=True, blank=True, verbose_name='Question Seq')
    year = models.ForeignKey(Years, null=True, blank=True, verbose_name='Year')
    subject = models.ForeignKey(Subjects, null=True, blank=True, verbose_name='Subject')
    level = models.ForeignKey(Levels, null=True, blank=True, verbose_name='Level')
   
    
    class Meta:
        verbose_name = 'Paper'

    def __unicode__(self):
        return '[Paper:%s,Type:%s,Owner:%s]' % (self.papername, self.ptype, self.owner)
