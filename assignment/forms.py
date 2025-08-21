from django import forms
from assignment.models import Assignment
from paper.models import Paper
from portal.models import SProfile
from django.utils.safestring import mark_safe

def make_custom_datefield(f):
    if isinstance(f, forms.DateTimeField):
        f.widget.format = '%m/%d/%Y %H:%M'
        f.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
    return f

class MultiSelectWidget(forms.SelectMultiple):
    def __init__(self, language=None, attrs=None):
        super(MultiSelectWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(MultiSelectWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $(document).ready(function afterReady() {
                var elem = $('#id_%(name)s');
                elem.multiselect();
            });
            </script>''' % {'name':name})

class AssignmentDetailForm(forms.Form):
    def __init__(self,*args,**kwargs):
        teacher = kwargs.pop('teacher')
        super(AssignmentDetailForm,self).__init__(*args,**kwargs)
        assignments = Assignment.objects.filter(teacher = teacher)
        es = [(-1,"New Assignment")]+[(e.id,e.assignmentname) for e in assignments]
        papers = Paper.objects.filter(owner = teacher.user)
        ps = [(p.id, p.papername) for p in papers]
        self.fields['assignmentid'] = forms.ChoiceField(choices=es,label="Assignment ID")
        self.fields['papers'] = forms.MultipleChoiceField(choices=ps, label="Papers")

    assignmentid=forms.CharField(label = 'Assignment ID')
    assignmentname=forms.CharField(label = 'Assignment Name')
    testdate = make_custom_datefield(forms.DateTimeField())
    deadline = make_custom_datefield(forms.DateTimeField())
    description = forms.CharField(widget = forms.Textarea(attrs={'cols': 32, 'rows': 4}),
                                  label = 'Description', required = False)
    papers= forms.MultipleChoiceField(widget=MultiSelectWidget)
    students = forms.CharField(label = 'students')

    def clean_students(self):
        sids = self.cleaned_data['students']
        if ',' in sids:
            students = sids.split(',')
        else:
            students = [sids]
        sp = []
        for s in students:
            sp.append(SProfile.objects.get(user__id=int(s)))
        return sp

    def clean_papers(self):
        paperids = self.cleaned_data['papers']
        papers = Paper.objects.filter(id__in = paperids)
        return papers

    def clean_description(self):
        desc = self.cleaned_data['description'].replace('\r', '').replace('\n', '</br>').strip()
        print desc
        return desc
