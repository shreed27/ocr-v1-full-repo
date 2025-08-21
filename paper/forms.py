from django import forms
from paper.models import Paper
from question.models import Question
from entity.models import Years, Levels, Subjects
import re


class PaperDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher')
        super(PaperDetailForm, self).__init__(*args, **kwargs)
        if teacher:
            papers = Paper.objects.filter(owner=teacher.user)
            ps = [(-1, "New Paper")] + [(p.id, p.papername) for p in papers]
            self.fields['paperid'] = forms.ChoiceField(choices=ps, label="Paper ID")
            ls = [(l.id, l.levelname) for l in Levels.objects.all()]
            self.fields['level'] = forms.ChoiceField(choices=ls, label="Level")
            ys = [(y.id, y.yearname) for y in Years.objects.all()]
            self.fields['year'] = forms.ChoiceField(choices=ys, label="Year")
            ss = [(s.id, s.subjectname) for s in Subjects.objects.all()]
            self.fields['subject'] = forms.ChoiceField(choices=ss, label="Subject")

    paperid = forms.ChoiceField(label="Paper ID")
    papername = forms.CharField(label="Paper Name")
    ptype = forms.ChoiceField(choices=(("Review", "Review"), ("Formal", "Formal"), ("Informal", 'Informal')))
    year = forms.ChoiceField()
    level = forms.ChoiceField()
    passpoint = forms.IntegerField(min_value=0)
    duration = forms.CharField(max_length=20)
    subject = forms.ChoiceField()
    questionlist = forms.CharField(label="Questions")

    def clean_questionlist(self):
        qs = self.cleaned_data['questionlist']
        if ',' in qs:
            qids = qs.split(',')
        else:
            qids = [qs]
        questions = []
        for q in qids:
            try:
                question = Question.objects.get(id=int(q))
            except:
                continue
            questions.append(question)
        return questions

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        group = re.search(r'(0?[0-9]|1[0-9]|2[0-3]):(0?[0-9]|[1-4][0-9]|5[0-9])', duration)
        if group:
            return duration
        else:
            raise forms.ValidationError('invalid duration')

    def clean_year(self):
        yearid = self.cleaned_data['year']
        try:
            year = Years.objects.get(id=yearid)
            return year
        except:
            raise forms.ValidationError('invalid year')

    def clean_subject(self):
        subjectid = self.cleaned_data['subject']
        try:
            subject = Subjects.objects.get(id=subjectid)
            return subject
        except:
            raise forms.ValidationError('invalid subject')

    def clean_level(self):
        levelid = self.cleaned_data['level']
        try:
            level = Levels.objects.get(id=levelid)
            return level
        except:
            raise forms.ValidationError('invalid level')


class PaperSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(PaperSearchForm, self).__init__(*args, **kwargs)
        ls = [('', '----')] + [(l.levelname, l.levelname) for l in Levels.objects.all()]
        self.fields['level'] = forms.ChoiceField(choices=ls, label="Level")
        self.fields['level'].required = False
        ys = [('', '----')] + [(y.yearname, y.yearname) for y in Years.objects.all()]
        self.fields['year'] = forms.ChoiceField(choices=ys, label="Year")
        self.fields['year'].required = False
        ss = [('', '----')] + [(s.subjectname, s.subjectname) for s in Subjects.objects.all()]
        self.fields['subject'] = forms.ChoiceField(choices=ss, label="Subject")
        self.fields['subject'].required = False

    year = forms.ChoiceField()
    level = forms.ChoiceField()
    subject = forms.ChoiceField()
