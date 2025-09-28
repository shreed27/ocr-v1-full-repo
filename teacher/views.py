import logging
import pickle
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from entity.forms import OptionDetailForm
from entity.models import Years, Levels, Subjects
from portal.models import SProfile
from question.models import Question
from student.models import StudentAnswer
from django.utils import simplejson
from django.http import HttpResponse

logger = logging.getLogger(__name__)


@permission_required('auth.add_user')
def index(request):
    form = OptionDetailForm()
    if request.method == 'POST':
        form = OptionDetailForm(request.POST)
        response = {"state": "failure"}
        if form.is_valid():
            years = form.cleaned_data['year']
            levels = form.cleaned_data['level']
            subjects = form.cleaned_data['subject']
            if __updateyear(years) and __updatelevel(levels) and __updatesubject(subjects):
                response['state'] = 'success'
        else:
            response = form.errors_as_json()
            return HttpResponse(simplejson.dumps(response), mimetype='application/json')
    return render_to_response('teacher_index.html', {'form': form},
                              context_instance=RequestContext(request))


def __updateyear(years):
    year_set = Years.objects.all()
    temp = []
    for year in year_set:
        if year.yearname in years:
            temp.append(year.yearname)
        else:
            year.delete()
    try:
        for yearname in years:
            if yearname not in temp:
                Years.objects.create(yearname=yearname)
    except:
        return False
    else:
        return True


def __updatelevel(levels):
    level_set = Levels.objects.all()
    temp = []
    for level in level_set:
        if level.levelname in levels:
            temp.append(level.levelname)
        else:
            level.delete()
    try:
        for levelname in levels:
            if levelname not in temp:
                Levels.objects.create(levelname=levelname)
    except:
        return False
    else:
        return True


def __updatesubject(subjects):
    subject_set = Subjects.objects.all()
    temp = []
    for subject in subject_set:
        if subject.subjectname in subjects:
            temp.append(subject.subjectname)
        else:
            subject.delete()
    try:
        for subjectname in subjects:
            if subjectname not in temp:
                Subjects.objects.create(subjectname=subjectname)
    except:
        return False
    else:
        return True


@permission_required('auth.add_user')
def updatemark(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        studentid = request.POST.get('studentid')
        questionid = request.POST.get('questionid')
        modifiedmark = request.POST.get('mark')
        try:
            student = SProfile.objects.get(user__id=int(studentid))
            question = Question.objects.get(id=int(questionid))
            stuanswer = StudentAnswer.objects.get(student=student, question=question)
            fullmark = question.stdanswer.fullmark
        except Exception as e:
            print(e, 'stuanswer not found')
        else:
            try:
                mark = int(modifiedmark)
                stuanswer.mark = mark if mark < fullmark else fullmark
                stuanswer.save()
            except:
                response_data['mark'] = stuanswer.mark
                response_data['state'] = 'format error'
            else:
                response_data['mark'] = stuanswer.mark
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')


@permission_required('auth.add_user')
def updateomitted(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        studentid = request.POST.get('studentid')
        questionid = request.POST.get('questionid')
        omitted = request.POST.get('omitted')
        try:
            student = SProfile.objects.get(user__id=int(studentid))
            question = Question.objects.get(id=int(questionid))
            stuanswer = StudentAnswer.objects.get(student=student, question=question)
        except Exception as e:
            print(e, 'stuanswer not found')
        else:
            try:
                parsedomitted = list(filter(bool, omitted.replace('<p>', '').replace('</p>', '\n').split('\n')))
                stuanswer.omitted = pickle.dumps(parsedomitted)
                stuanswer.save()
            except:
                response_data['omitted'] = pickle.loads(str(stuanswer.omitted))
                response_data['state'] = 'format error'
            else:
                response_data['omitted'] = omitted
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
