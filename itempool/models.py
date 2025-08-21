# coding: utf-8
from django.db import models
from portal.models import TProfile

class Itempool(models.Model):
    poolname = models.CharField(max_length=30, blank=True, null=True,
                                verbose_name='Pool Name')
    teacher = models.ForeignKey(TProfile, verbose_name='Teacher')
    description = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name='Description')
    # Teachers who can access this item pool
    accessible = models.ManyToManyField(TProfile, null=True, blank=True, related_name='Item Pool')

    class Meta:
        verbose_name = u'Item Pool'

    def __unicode__(self):
        return u'[Itempool:%s]' % self.poolname

    # def save(self, *args, **kwargs):
    #     # custom save method to provide `accessible` value
    #     # to include the teacher profile.
    #     # print self.accessible.values().count(),"true"
    #     # self.save()
    #     if not self.accessible.values().count(): # faster query
    #         # _teacher = TProfile.objects.get(pk=self.teacher.pk)
    #         _teacher = TProfile.objects.get(pk=self.teacher_id)
    #         self.accessible.add(_teacher)
    #         #self.accessible.add(self.teacher)
    #     super(Itempool, self).save(*args, **kwargs)
