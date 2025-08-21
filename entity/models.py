from django.db import models

# Create your models here.
class Years(models.Model):
    yearname = models.CharField(max_length=10, verbose_name='YearName')
    def __unicode__(self):
        return self.yearname

    class Meta:
        verbose_name_plural = "Years"

class Levels(models.Model):
    levelname = models.CharField(max_length=10, verbose_name='LevelName')
    def __unicode__(self):
        return self.levelname

    class Meta:
        verbose_name_plural = "Levels"

class Subjects(models.Model):
    subjectname = models.CharField(max_length=10, verbose_name='SubjectName')
    def __unicode__(self):
        return self.subjectname

    class Meta:
        verbose_name_plural = "Subjects"

class Randomcode(models.Model):
    randomcode = models.CharField(unique = True, max_length = 10, verbose_name='RandomCode')
    used = models.BooleanField()
    def __unicode__(self):
        return self.randomcode

    def is_notused(self):
        if self.used:
            return False
        else:
            return True
