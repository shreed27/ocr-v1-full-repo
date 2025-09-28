# coding: utf-8
from django.db import models
from portal.models import TProfile, SProfile
#from student.models import StudentAnswer
import datetime

class Assignment(models.Model):
    assignmentname = models.CharField(max_length=20, verbose_name='Assignment Name')
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Description')
    students = models.ManyToManyField(SProfile, blank=True, null=True,verbose_name='Students')
    teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
    date_created = models.DateTimeField('test date', default=datetime.datetime.now)
    deadline = models.DateTimeField('test deadline', blank=True, null=True)

    class Meta:
        verbose_name = 'Assignment'

    def __unicode__(self):
        return '%s' % self.assignmentname



class AssignmentFeedback(models.Model):
    Assignment = models.ForeignKey(Assignment)
    Student = models.ForeignKey(SProfile)
    feedback = models.TextField(max_length=255)
    feedback_code = models.TextField()
    
    class Meta:
        unique_together = ("Assignment", "Student")
    def __unicode__(self):
        return '%s - %s' %(self.Assignment, self.Student)