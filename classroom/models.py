# coding: utf-8

from django.db import models
import datetime

class Classroom(models.Model):
    roomname = models.CharField(max_length=30, verbose_name='RoomName')
    volume = models.IntegerField(blank=True, null=True, verbose_name='Volume')
    date_created = models.DateTimeField('date created', default=datetime.datetime.now)

    class Meta:
        verbose_name = 'ClassRoom'

    def __unicode__(self):
        return u'[ClassRoom:%s]' % self.roomname
