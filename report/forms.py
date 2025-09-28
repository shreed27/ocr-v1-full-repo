from django import forms
from paper.models import Paper
from portal.models import SProfile

class DetailSearchForm(forms.Form):
    def __init__(self,*args,**kwargs):
        pids = kwargs.pop('paper')
        stuids = kwargs.pop('student')
        super(DetailSearchForm,self).__init__(*args,**kwargs)
        try:
            papers = Paper.objects.filter(id__in = pids)
            ss = [(-1,'----')] + list(set([(p.subject.id, p.subject.subjectname) for p in papers]))
            papers = [(-1,'----')] +  [(p.id, p.papername)\
                    for p in Paper.objects.filter(id__in = pids)]
            students = [(-1,'----')] +  [(s.user.id, s.user.username)\
                        for s in SProfile.objects.filter(user__id__in = stuids)]
            self.fields['subject'] = forms.ChoiceField(choices=ss, label = "Subject")
            self.fields['subject'].required = False
            self.fields['paper'] = forms.ChoiceField(choices=papers, label='Paper')
            self.fields['paper'].required = False
            self.fields['student'] = forms.ChoiceField(choices=students, label='students')
            self.fields['student'].required = False
        except Exception as e:
            print(e)

    paper = forms.ChoiceField()
    student = forms.ChoiceField()
    subject = forms.ChoiceField()

    def clean_student(self):
        sid = self.cleaned_data['student']
        if sid != -1:
            try:
                return SProfile.objects.get(user__id = sid)
            except:
                pass
        raise forms.ValidationError('not checked')


    def clean_paper(self):
        pid = self.cleaned_data['paper']
        if pid != -1:
            try:
                return Paper.objects.get(id = pid)
            except:
                pass
        raise forms.ValidationError('not checked') 
    
    
class FeedbackForm(forms.Form):
    Add_Feedback      = forms.CharField(widget = forms.Textarea(attrs={'cols': 60, 'rows': 8,'size': '10'}))
    Add_Feedback_Code = forms.CharField(widget = forms.Textarea())
