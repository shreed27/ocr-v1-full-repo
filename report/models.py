from json import loads, dumps
from django.db import models

from question.models import Question
from student.models import StudentAnswer

class ClosenessReport(models.Model):
    """statistics about student answer wise closeness"""

    question = models.ForeignKey(Question, verbose_name="Question")
    student_answer = models.ForeignKey(StudentAnswer, verbose_name="Student Answer")
    alternative = models.BooleanField(default=False, verbose_name='Is it alternative closeness record?')
    # sample data in closeness
    # {'P2': False, 'P1.1': False, 'P1': False, 'P1.2': True, 'P3': True, \
    #     'wrong_pts': ['P1', 'P1.1', 'P2'], \
    #     'correct_pts': ['P', 'P', 'P1.2', 'P3'], \
    #     'closeness': {'P2': 0.5, 'P3': 0.5, 'P1': 0.5, 'P4': 0.5}}

    closeness_record = models.TextField()

    class Meta:
        verbose_name = "Closeness Report"
        verbose_name_plural = "Closeness Reports"

    def get_correct_pts(self):
        _correct_pts = loads(self.closeness_record)
        return _correct_pts['correct_pts']

    def get_wrong_pts(self):
        _wrong_pts = loads(self.closeness_record)
        return _wrong_pts['wrong_pts']

    def get_pt_value(self, pt_no):
        """
        return the value for the point no from dictionary
        """
        _closeness_stat = loads(self.closeness_record)
        return _closeness_stat.get(pt_no, None)

    def get_pt_closeness(self, pt_no):
        """
        return the closeness value for pt_no
        """
        _closeness_stat = loads(self.closeness_record)
        return _closeness_stat.get('closeness').get(pt_no, None)
