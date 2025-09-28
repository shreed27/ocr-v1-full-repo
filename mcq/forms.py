from django import forms
import re
import logging
from django.utils.safestring import mark_safe
from portal.models import TProfile,SProfile
from mcq.models import MCQ_Itempool, MCQ_Paper, MCQ_Question, MCQ_Assignment
from entity.models import Years, Levels, Subjects
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)
logger.debug("mcq/question/forms.py: __name__=%s" % __name__)

class MCQ_CustomPaperForm(forms.Form):

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(MCQ_CustomPaperForm, self).__init__(*args, **kwargs)
        if owner:
            studentpaper = MCQ_Paper.objects.filter(owner=owner)
            ps = [(p.id, p.ppr_papername) for p in studentpaper] + [(-1, "New Paper")]
            self.fields['paperid'] = forms.ChoiceField(choices=ps, label="Paper ID")

    paperid = forms.ChoiceField(label="Paper ID")
    papername = forms.CharField(max_length=20, label='Paper Name')
    questionlist = forms.CharField(label='questionlist')
    duration = forms.CharField(max_length=20,
                               widget=forms.TextInput(attrs={"style": "width:130px;"}))

    def clean_questionlist(self):
        qs = self.cleaned_data['questionlist']
        if ',' in qs:
            qids = qs.split(',')
        else:
            qids = [qs]
        questions = []
        for q in qids:
            try:
                question = MCQ_Question.objects.get(id=int(q))
            except:
                continue
            questions.append(question)
        return questions

class MCQ_DetailSearchForm(forms.Form):
	def __init__(self,*args,**kwargs):
		pids = kwargs.pop('paper')
		stuids = kwargs.pop('student')
		super(MCQ_DetailSearchForm,self).__init__(*args,**kwargs)
		try:
			papers = MCQ_Paper.objects.filter(id__in = pids)
			ss = [(-1,'----')] + list(set([(p.subject.id, p.subject.subjectname) for p in papers]))
			papers = [(-1,'----')] +  [(p.id, p.ppr_papername)\
				for p in MCQ_Paper.objects.filter(id__in = pids)]
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
    



class MCQ_PaperSearchForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(MCQ_PaperSearchForm, self).__init__(*args, **kwargs)
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
		return rendered + mark_safe('''<script type="text/javascript">
		    $(document).ready(function afterReady() {
			var elem = $('#id_%(name)s');
			elem.multiselect();
		    });
		    </script>''' % {'name':name})


class MCQ_AssignmentDetailForm(forms.Form):
	def __init__(self,*args,**kwargs):
		teacherValue = kwargs.pop('teacher')
		logger.info('MCQ_AssignmentDetailForm 1')
		super(MCQ_AssignmentDetailForm,self).__init__(*args,**kwargs)
		logger.info('MCQ_AssignmentDetailForm 2')
		assignments = MCQ_Assignment.objects.filter(teacher = teacherValue)
		logger.info('MCQ_AssignmentDetailForm 3')
		es = [(-1,"New Assignment")]+[(e.id,e.asm_assignmentname) for e in assignments]
		papers = MCQ_Paper.objects.filter(owner = teacherValue.user)
		ps = [(p.id, p.ppr_papername) for p in papers]
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
		logger.info('clean-student:%s' % sids)
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
		logger.info('clean-paperids:%s' % paperids)
		papers = MCQ_Paper.objects.filter(id__in = paperids)
		return papers

	def clean_description(self):
		desc = self.cleaned_data['description'].replace('\r', '').replace('\n', '</br>').strip()
		logger.info('clean-desc:%s' % desc)
		print(desc)
		return desc
class MCQ_ItemPoolDetailForm(forms.Form):
    def __init__(self,*args,**kwargs):
        teacher = kwargs.pop('teacher')
        super(MCQ_ItemPoolDetailForm,self).__init__(*args,**kwargs)
        if teacher:
            itempools = MCQ_Itempool.objects.filter(itp_teacher = teacher)
            ips = [(-1,"New Item Pool")] + [(ip.id,ip.itp_poolname) for ip in itempools]
            self.fields['itempoolid'] = forms.ChoiceField(choices=ips,label="Item Pool ID")

    itempoolid = forms.ChoiceField(label="Item Pool ID")
    itempoolname = forms.CharField(label = "Item Pool Name",max_length = 30)
    description = forms.CharField(widget = forms.Textarea(attrs={'cols': 22, 'rows': 3}),
                                  label = 'Description', required = False)

class MCQ_PaperDetailForm(forms.Form):
	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(MCQ_PaperDetailForm, self).__init__(*args, **kwargs)
		if teacher:
			papers = MCQ_Paper.objects.filter(owner=teacher.user)
			ps = [(-1, "New Paper")] + [(p.id, p.ppr_papername) for p in papers]
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
		logger.info(qs)
		if ',' in qs:
			qids = qs.split(',')
		else:
			qids = [qs]
		questions = []
		for q in qids:
			try:
				question = MCQ_Question.objects.get(id=int(q))
			except Exception as e:
				logger.debug('exception to search for question: %s' % q)
				logger.error(e)
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





class MCQ_FeedbackForm(forms.Form):
    Add_Feedback      = forms.CharField(widget = forms.Textarea(attrs={'cols': 60, 'rows': 8,'size': '10'}))
    Add_Feedback_Code = forms.CharField(widget = forms.Textarea())






