from django.db import models
from question.models import Question, StandardAnswer
from student.models import StudentAnswer


# Create your models here.
class Canvas(models.Model):
    question = models.ForeignKey(Question, verbose_name='Question')
    stdanswer = models.ForeignKey(StandardAnswer, null=True, blank=True)
    stuanswer = models.ForeignKey(StudentAnswer, null=True, blank=True)
    name = models.CharField(max_length=20)
    axismap = models.TextField(null=True, blank=True)
    drawopts = models.TextField(null=True, blank=True)
    rulelist = models.TextField(null=True, blank=True)
    markscheme = models.TextField(null=True, blank=True)
    pointlist = models.TextField(null=True, blank=True)
    mark = models.IntegerField(default=0)

    # alternative canvas fields added for Alternative Standard Answer
    # alt_available = models.BooleanField(default=False, verbose_name='Is alternate Canvas available?')
    # axismap = models.TextField(null=True, blank=True)
    # drawopts = models.TextField(null=True, blank=True)
    # rulelist = models.TextField(null=True, blank=True)
    # markscheme = models.TextField(null=True, blank=True)
    # pointlist = models.TextField(null=True, blank=True)
    # mark = models.IntegerField(default=0)

    def __unicode__(self):
        return 'Canvas id:%d name:%s question:%s std:%s stu:%s' % (self.id, self.name, self.question, self.stdanswer, self.stuanswer)
