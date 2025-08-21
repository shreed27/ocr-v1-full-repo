import logging
from django import forms
from portal.models import SProfile

logger = logging.getLogger(__name__)

class ClassDetailForm(forms.Form):
    def __init__(self,*args,**kwargs):
        teacher = kwargs.pop('teacher')
        super(ClassDetailForm,self).__init__(*args,**kwargs)
        if teacher:
            classrooms = teacher.classrooms.all()
            cs = [(-1,"New Class")] + [(c.id,c.roomname) for c in classrooms]
            self.fields['classid'] = forms.ChoiceField(choices=cs,label="ClassNo.")
            self.fields['stulist'].required = False

    classid = forms.ChoiceField(label="ClassNo.")
    classname = forms.CharField(label = "Class Name",max_length = 30)
    volume = forms.CharField(label = "Class Volume",max_length = 30)
    stulist = forms.CharField(label = "stulist")

    def clean_stulist(self):
        stulist = self.cleaned_data['stulist']
        logger.info("stulist:%s" % stulist)
        if stulist == '':
            return []
        elif ',' in stulist:
            studentids = stulist.split(',')
        else:
            studentids = [stulist]
        logger.info("studentids:%s" % studentids)
        students = []
        for sid in studentids:
            logger.info("sid:%s" % sid)
            try:
                student = SProfile.objects.get(user__id=int(sid))
            except:
                continue
            students.append(student)
        return students
