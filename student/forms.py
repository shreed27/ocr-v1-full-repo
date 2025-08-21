import logging
from django import forms
from django.contrib.auth.models import User
from classroom.models import Classroom
from question.models import Question
from paper.models import Paper
from portal.models import SProfile
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class StudentDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher')
        super(StudentDetailForm, self).__init__(*args, **kwargs)
        if teacher:
            classrooms = teacher.classrooms.all()
            cs = [(-1, "---------")] + [(c.id, c.roomname) for c in classrooms]
            self.fields['clazz'] = forms.ChoiceField(choices=cs, label="ClassNo")

    username = forms.CharField(label='Account Name', max_length=30)
    password1 = forms.CharField(label='Password', max_length=30,
                                widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password Confirm', max_length=30,
                                widget=forms.PasswordInput())
    email = forms.EmailField(label='Email', max_length=30)
    clazz = forms.ChoiceField(required=False)
    gender = forms.ChoiceField(choices=[("male", "male"), ("female", "female")],
                               label="Gender")

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                if password2 != "":
                    return password2
                else:
                    raise forms.ValidationError('Password cannot be empty')
            else:
                raise forms.ValidationError('Passwords Input don\'t match each other!')

    def clean_username(self):
        users = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if not users:
            return self.cleaned_data['username']
        raise forms.ValidationError('Existed username!')

    def clean_email(self):
        emails = User.objects.filter(email__iexact=self.cleaned_data['email'])
        if not emails:
            return self.cleaned_data['email']
        raise forms.ValidationError('Existed email!')

    def clean_clazz(self):
        clazz = self.cleaned_data['clazz']
        if int(clazz) == -1:
            return None
        else:
            return get_object_or_404(Classroom, id=clazz)


class StudentModifyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher')
        super(StudentModifyForm, self).__init__(*args, **kwargs)
        if teacher:
            classrooms = teacher.classrooms.all()
            cs = [(-1, "-----")] + [(c.id, c.roomname) for c in classrooms]
            self.fields['clazz'] = forms.ChoiceField(choices=cs, label="Classroom ID")

    username = forms.CharField(label='Account Name', max_length=30)
    password1 = forms.CharField(label='Password', max_length=30,
                                widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password Confirm', max_length=30,
                                widget=forms.PasswordInput())
    email = forms.EmailField(label='Email', max_length=30)
    clazz = forms.ChoiceField(required=False)
    gender = forms.ChoiceField(choices=[("male", "male"), ("female", "female")],
                               label="Gender")

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                if password2 != "":
                    return password2
                else:
                    raise forms.ValidationError('Password cannot be empty')
            else:
                raise forms.ValidationError('Passwords Input don\'t match each other!')

    '''
    def clean_email(self):
        emails = User.objects.filter(email__iexact = self.cleaned_data['email'])
        if not emails:
            return self.cleaned_data['email']
        raise forms.ValidationError('Error email format!')
    '''


class CustomPaperForm(forms.Form):

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(CustomPaperForm, self).__init__(*args, **kwargs)
        if owner:
            studentpaper = Paper.objects.filter(owner=owner)
            ps = [(p.id, p.papername) for p in studentpaper] + [(-1, "New Paper")]
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
                question = Question.objects.get(id=int(q))
            except:
                continue
            questions.append(question)
        return questions


class OCRAnswerSheetForm(forms.Form):
    """
    Form for uploading handwritten answer sheets for OCR processing
    """
    answer_sheet_image = forms.ImageField(
        label='Answer Sheet Image',
        help_text='Upload a clear image of the handwritten answer sheet (JPG, PNG, PDF supported)',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*,.pdf',
            'class': 'form-control'
        })
    )

    student = forms.ModelChoiceField(
        queryset=SProfile.objects.all(),
        label='Student',
        help_text='Select the student who submitted this answer sheet',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    question = forms.ModelChoiceField(
        queryset=Question.objects.all(),
        label='Question',
        help_text='Select the question this answer belongs to',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    manual_text_override = forms.CharField(
        label='Manual Text Override (Optional)',
        help_text='If OCR fails, you can manually enter the text here',
        widget=forms.Textarea(attrs={
            'rows': 6,
            'class': 'form-control',
            'placeholder': 'Leave empty to use OCR extraction...'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super(OCRAnswerSheetForm, self).__init__(*args, **kwargs)

        # Filter students and questions based on teacher if provided
        if teacher:
            # Filter students from teacher's classrooms
            classrooms = teacher.classrooms.all()
            students_in_classrooms = SProfile.objects.filter(classroom__in=classrooms)
            self.fields['student'].queryset = students_in_classrooms

            # Filter questions from teacher's assignments
            teacher_questions = Question.objects.filter(
                assignment__teacher=teacher
            ).distinct()
            self.fields['question'].queryset = teacher_questions

    def clean_answer_sheet_image(self):
        image = self.cleaned_data.get('answer_sheet_image')
        if image:
            # Check file size (10MB limit)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 10MB')

            # Check file format
            allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'tiff']
            file_extension = image.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f'File format not supported. Allowed formats: {", ".join(allowed_extensions)}'
                )

        return image
