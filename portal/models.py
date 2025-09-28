from django.db import models
from django.contrib.auth.models import User, Group
from classroom.models import Classroom

class TProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='UserID')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name='Gender')
    cellphone = models.CharField(default='', max_length=16, blank=True, null=True,	verbose_name='Cellphone')
    classrooms = models.ManyToManyField(Classroom, verbose_name='RelatedClassrooms')
    api_key = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="API Key")
    class Meta:
        verbose_name = 'teacher'

    def save(self, *args, **kwargs):
        self.user.groups = (Group.objects.get(name = 'teachers'),)
        super(TProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return '[Teacher:%s]' % self.user.username

class SProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='UserID')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name='Gender')
    cellphone = models.CharField(default='', max_length=16, blank=True,
                                 null=True,	verbose_name='Cellphone')
    classroom = models.ForeignKey(Classroom, blank=True, null=True,
                                  verbose_name='RelatedClassroom',on_delete=models.SET_NULL)
    teacher = models.ForeignKey(TProfile, blank=True, null=True,
                                 verbose_name='RelatedTeacher',on_delete=models.SET_NULL)
    api_key = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="API Key")
    class Meta:
        verbose_name = 'student'

    def save(self, *args, **kwargs):
        self.user.groups = (Group.objects.get(name = 'students'),)
        super(SProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return '[Student:%s]' % self.user.username
