import logging
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from assignment.models import Assignment
from paper.models import Paper
from assignment.forms import AssignmentDetailForm
from portal.models import SProfile
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from portal.common import getTpByRequest, getSpByRequest
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


@login_required
def assignment_getall(request):
    teacher, res = getTpByRequest(request, None)
    if not teacher:
        student, res = getSpByRequest(request, None)
        teacher = student.teacher
    logger.info("assignment getall:%s" % teacher)
    try:
        assignments = Assignment.objects.filter(teacher=teacher)
    except Exception as e:
        logger.error(e)
        assignments = []
    logger.info("assignments %s" % assignments)
    try:
        forwhat = request.GET.get('forwhat')
    except:
        forwhat = 'default'

    if forwhat == 'teacher_report':
        response = render_to_response('teacherreport_assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))
    else:
        response = render_to_response('assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))

    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def assignment_add(request):
    teacher, res = getTpByRequest(request, None)
    if request.method == "POST":
        form = AssignmentDetailForm(request.POST, teacher=teacher)
        if form.is_valid():
            if not teacher:
                student, res = getSpByRequest(request, None)
                teacher = student.teacher
            logger.info("assignment add:%s" % teacher)
            assignmentid = int(form.cleaned_data['assignmentid'])
            if assignmentid != -1:
                assignment = Assignment.objects.get(id=assignmentid)
                assignment.teacher = teacher
            else:
                assignment = Assignment.objects.create(
                    assignmentname=form.cleaned_data['assignmentname'],
                    teacher=teacher
                )

            logger.info("assignment:%s" % assignment)
            assignment.date_created = form.cleaned_data['testdate']
            assignment.deadline = form.cleaned_data['deadline']
            assignment.description = form.cleaned_data['description']
            studentlist = form.cleaned_data['students']
            __updatestuinassignment(assignment, studentlist)
            paperlist = form.cleaned_data['papers']
            __updatepaperinassignment(assignment, paperlist)
            assignment.save()
            messages.add_message(request, messages.SUCCESS, "One Assignment Added")
            return redirect("/assignment/add?assignmentid=" + str(assignment.id))
        else:
            logger.info("form invalid")
            messages.add_message(request, messages.SUCCESS, "You missed some values")
    else:
        assignmentid = request.GET.get('assignmentid')
        form = AssignmentDetailForm(teacher=teacher)
        if assignmentid:
            try:
                assignment = Assignment.objects.get(id=assignmentid)
            except:
                form = AssignmentDetailForm(teacher=teacher)
                logger.info("assignment not found:%s" % assignmentid)
            else:
                logger.info("paper:%s" % Assignment)
                papers = Paper.objects.filter(assignment=assignment)
                form = AssignmentDetailForm(teacher=teacher,
                                            initial={'assignmentid': assignment.id,
                                                     'papername': assignment.assignmentname,
                                                     'testdate': assignment.date_created,
                                                     'deadline': assignment.deadline,
                                                     'description': assignment.description.replace('</br>', '\n'),
                                                     'papers': papers})
    return render_to_response('assignment_detail.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def __updatestuinassignment(assignment, studentlist):
    try:
        students = assignment.students.all()
    except:
        pass
    else:
        stemp = []
        for s in students:
            if s not in studentlist:
                assignment.students.remove(s)
                stemp.append(s)
        for s in studentlist:
            if s not in stemp:
                assignment.students.add(s)


def __updatepaperinassignment(assignment, paperlist):
    try:
        papers = Paper.objects.filter(assignment=assignment)
    except:
        pass
    else:
        ptemp = []
        for p in papers:
            if p not in paperlist:
                p.assignment = None
                p.save()
                ptemp.append(p)
        for p in paperlist:
            if p not in ptemp:
                p.assignment = assignment
                p.save()


@permission_required('auth.add_user')
def assignment_getstudents(request):
    logger.info("assignment_getstudents")
    if request.method == "POST":
        assignmentid = request.POST['assignmentid']
        view = request.POST.get('view', False)
        teacher, res = getTpByRequest(request, None)
        logger.info("assignment_getstudents, teacher:%s,assignmentid:%s" % (teacher, assignmentid))
        try:
            assignment = Assignment.objects.get(id=assignmentid)
            checkedstudents = assignment.students.all()
        except:
            checkedstudents = []

        stu_teacher_list = []
        teachernode = {'name': teacher.user.username, 'checked': 'true'}
        if view:
            teachernode['disabled'] = 'true'
        else:
            teachernode['disabled'] = 'false'

        stunodes = []
        try:
            students = SProfile.objects.filter(teacher=teacher)
        except:
            students = []
        for stu in students:
            stunode = {'node': stu, 'sid': stu.user.id, 'disabled': 'false'}
            if checkedstudents and stu in checkedstudents:
                stunode['checked'] = 'true'
            else:
                stunode['checked'] = 'false'
            if view:
                stunode['disabled'] = 'true'
            stunodes.append(stunode)
        stu_teacher_list.append([teachernode, stunodes])
        logger.info("assignment_getstudents finished")
        return render_to_response('classroom_getstudents.json',
                                  {'stu_teacher_list': stu_teacher_list,
                                   'tnum': len(stu_teacher_list)},
                                  context_instance=RequestContext(request))


class AssignmentDelete(DeleteView):
    model = Assignment
    success_url = reverse_lazy("deleteview_callback")

    def get_object(self):
        pk = self.request.POST['assignmentid']
        return get_object_or_404(Assignment, id=pk)


@permission_required('auth.add_user')
def assignment_updatename(request):
    logger.info("assignment updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if not tp:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    assignmentid = request.GET.get('assignmentid').strip()
    assignmentname = request.GET.get('assignmentname')
    if assignmentid and assignmentid != '-1' and assignmentname:
        try:
            assignment = Assignment.objects.get(id=int(assignmentid), teacher=tp)
        except:
            pass
        else:
            assignment.assignmentname = assignmentname
            assignment.teacher = tp
            assignment.save()
            response_data['assignmentid'] = assignment.id
            response_data['assignmentname'] = assignment.assignmentname
            response_data['description'] = assignment.description.replace('</br>', '\n')
            response_data['testdate'] = assignment.date_created.strftime("%m/%d/%Y %H:%M")
            response_data['testdue'] = assignment.deadline.strftime("%m/%d/%Y %H:%M")
            papers = Paper.objects.filter(assignment=assignment)
            response_data['papers'] = list(p.id for p in papers)
            response_data['state'] = 'success'
            logger.info(papers)
    elif assignmentid == '-1':
        try:
            assignment = Assignment.objects.create(teacher=tp)
        except:
            pass
        else:
            response_data['assignmentid'] = assignment.id
            response_data['assignmentname'] = assignment.assignmentname
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
