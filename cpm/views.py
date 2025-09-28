import logging
import re
import os
import hashlib
import time
import json
import random
import pickle
from django.db.models import Q
import logging
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from question.views import NUM_CLOSENESS_BANDS
from datetime import datetime, timedelta
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.conf import settings
from entity.forms import OptionDetailForm
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic.edit import DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.utils import simplejson
from portal.common import getTpByRequest, getSpByRequest,getGroupNameByRequest, stripHTMLStrings, stripBody 
from django.utils.html import strip_tags
from portal.common import getTpByRequest, getSpByRequest
from django.utils import simplejson as json
from algo.answer import Answer, ImageAnswer
from portal.models import TProfile,SProfile
from PIL import Image
logger = logging.getLogger(__name__)
logger.debug("cpm/views.py: __name__=%s" % __name__)
from cpm.models import CPM_Itempool ,CPM_Question,   CPM_Assignment, CPM_Paper,CPM_StudentAnswer,  CPM_QuestionCategory ,CPM_Answer 

from cpm.forms import CPM_CustomPaperForm , CPM_AssignmentDetailForm,CPM_ItemPoolDetailForm  , CPM_PaperDetailForm, CPM_PaperSearchForm , CPM_DetailSearchForm, CPM_FeedbackForm
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
	return render_to_response('cpm_index.html', {'form': form},
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
	

class CPM_ItempoolDelete(DeleteView):
    success_url = reverse_lazy("deleteview_callback")
    model = CPM_Itempool

    def get_object(self):
        pk = self.request.POST['itempoolid']
        return get_object_or_404(CPM_Itempool, id=pk)

@permission_required('auth.add_user')
def cpm_itempool_updatename(request):
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp:
        itempoolid = request.GET.get("itempoolid").strip()
        itempoolname = request.GET.get("itempoolname").strip()
        if itempoolid and itempoolname:
            itempool = __getItempool(itempoolid, tp)
            if itempool:
                itempool.itp_poolname = itempoolname
                itempool.save()
                response_data['itempoolid'] = itempool.id
                response_data['itempoolname'] = itempool.itp_poolname
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


def addCPMteacher(request):
	"""
	This is post method. When addteacher button clicked then selected teacher
	will come in post method. We save the teacher data in itempool and return
	the success response
	:param request:
	:return {'response':'success'} or {'response':'failure'}:
	"""
	if request.method == 'POST':
		try:
			logger.info("testing1")
			itempool_id = request.POST['itempool_id']
			teacher_ids = request.POST.get('teacher_ids')
			teacher_list = teacher_ids[1:-1].split(',')[1:]
			teacher_list = [int(i.strip('"')) for i in teacher_list]
			print(type(teacher_ids), teacher_ids)
			if int(itempool_id) != -1:
				itempool = CPM_Itempool.objects.get(id = int(itempool_id))

				print(itempool.itp_teacher.user_id)
				for teacher in teacher_list:
					if itempool.itp_teacher.user_id != int(teacher):
						teach = TProfile.objects.get(user_id=int(teacher))
						print(teach,"teacher")
						itempool.itp_accessible.add(teach)
						itempool.save()
					try:
						question_list = CPM_Question.objects.filter(itempool=itempool)
						logger.info("print question list %s" % question_list)
						for question in question_list:
							if question.teacher.user_id != int(teacher):
								teach = TProfile.objects.get(user_id=int(teacher))
								logger.info("print teacher %s" % teach)
								question.qtn_accessible.add(teach)
								question.save()
					except Exception as e:
						logger.error(e)
						#traceback.print_exec();
				return HttpResponse(json.dumps({'response':'success'}))
			else:
				return HttpResponse(json.dumps({'response':'failure'}))
		except Exception as e:
			logger.error(e)
	return HttpResponse(json.dumps({'response':'failure'}))
def __teacherJsonList(teacher, view, itempool=None, modify=None):
    """
    This function return the teacher list with select box option
    like checked=true, disabled=true, checked=false, disabled=false

    :param teacher: request user of teacher
    :param view: view condition checking parameter
    :param itempool: Check the itempool available or not
    :param modify: Modify condition checking parameter.
    :return ztreejson: List of teacher with based on conditions
    """
    ztreejson = list()
    if view:
        selected_teacher = itempool.itp_accessible.all()
        teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
    else:
        if modify:
            selected_teacher = itempool.itp_accessible.all()#.exclude(user=itempool.teacher)
            print(selected_teacher,"selected teacher")
            teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
            print(teacher_list,"modified list")
        else:
            teacher_list = TProfile.objects.all().exclude(user = teacher.user)
    teacher_head = {'name': 'Teacher', 'checked': 'false'}
    if view:
        teacher_head['disabled'] = 'true'
    else:
        teacher_head['disabled'] = 'false'
    if view:
        teacher_node_list = list()
        for teacher in itempool.itp_accessible.all():
            teacher_node_list.append({'node':teacher, 'checked':'true', 'disabled':'true'})
    else:
        if modify:
            teacher_node_list = [{'node':itempool.itp_teacher, 'checked':'true', 'disabled':'true'}]
            for teacher in itempool.itp_accessible.all().exclude(user=itempool.itp_teacher):
                teacher_node_list.append({'node':teacher, 'checked':'true', 'disabled':'false'})
        else:
            teacher_node_list = [{'node':teacher, 'checked':'true', 'disabled':'true'}]
    if teacher_list:
        for teach in teacher_list:
            teacher_node = {'node':teach, 'checked':'false'}
            if view:
                teacher_node['disabled'] = 'true'
            else:
                teacher_node['disabled'] = 'false'
            teacher_node_list.append(teacher_node)
        ztreejson.append([teacher_head, teacher_node_list])
    return ztreejson

@permission_required('auth.add_user')
def get_cpm_question(request):
    tp, res = getTpByRequest(request, None)
    questions = []
    view = 0
    if tp:
        itempoolid = request.GET.get("itempoolid")
        view = request.GET.get("view")
        if itempoolid:
            try:
                itempool = CPM_Itempool.objects.get(id=int(itempoolid))
            except:
                itempool = None
            else:
                try:
                    questions = CPM_Question.objects.filter(teacher=tp, itempool=itempool)
                except:
                     logger.info("no questions in %s" % itempool)
    if view:
        response = render_to_response('cpm_itempool_allquestions_readonly.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    else:
        response = render_to_response('cpm_itempool_allquestions.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response

def cpm_itempool_updatedesc(request):
    tp, res = getTpByRequest(request, None)
    response_data = {"state": "failure"}
    if request.method == 'POST':
        if tp:
            itempoolid = request.POST.get("itempoolid").strip()
            description = request.POST.get("description").replace('\r', '').replace('\n', '</br>').strip()
            
            if itempoolid:
                itempool = __getItempool(itempoolid, tp)
                if itempool:
                    itempool.itp_description = description
                    itempool.save()
                    response_data['description'] = itempool.itp_description.replace('</br>', '\n')
                    response_data['state'] = "success"
    else:
        itempoolid = request.GET.get("itempoolid").strip()
        if itempoolid and itempoolid != '-1':
            itempool = __getItempool(itempoolid, tp)
            response_data['description'] = itempool.itp_description.replace('</br>', '\n')
            response_data['state'] = "success"
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


		
def getCPMTeacherList(request):
    """
    This function is used for display all teacher in select box.
    If view mode it show selected teacher only with disabled function.
    If modify mode it show the selected teacher without disabled function.
    :param request:
    :return Json Response of teacher_list.json file the data.
    """
	#logger.info('fall in option 2')
    qnum = 0
    tb, res = getTpByRequest(request, None)
    view = 0
    if request.method == 'POST':
        itempool_id = request.POST['itempool_id']
        view = request.POST['view']
        ztreejson = __teacherJsonList(tb, view)
        print(ztreejson)
        response = render_to_response('cpm_teacher_list.json',
                                      {'questiontree': ztreejson,
                                       'inum': len(ztreejson), 'qnum': qnum},
                                      context_instance=RequestContext(request))
        response['Content-Type'] = 'text/plain; charset=utf-8'
        response['Cache-Control'] = 'no-cache'
        return response
    else:
        view = request.GET.get('view')
        itempool_id = request.GET.get('itempool_id')
        print(view,"view", itempool_id, "itempool_id")
        if view:# Itempool view mode selected
            itempool = CPM_Itempool.objects.get(id=int(itempool_id))
            ztreejson = __teacherJsonList(tb, view, itempool)
            print(ztreejson)
            response = render_to_response('teacher_list.json',
                                          {'mcq_questiontree': ztreejson,
                                           'inum': len(ztreejson), 'qnum': qnum},
                                          context_instance=RequestContext(request))
            response['Content-Type'] = 'text/plain; charset=utf-8'
            response['Cache-Control'] = 'no-cache'
            return response
        else:# Other than view mode either add item or modify item.
            print('yes')
            if itempool_id and int(itempool_id) != -1:
                #Modify mode of selected box
                modify = True
                itempool = CPM_Itempool.objects.get(id=int(itempool_id))
                ztreejson = __teacherJsonList(tb, view, itempool, modify)
                print(ztreejson)
                response = render_to_response('cpm_teacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response
            else: 
                #Get method of selected teacher box
                ztreejson = __teacherJsonList(tb, view)
                print(ztreejson)
                response = render_to_response('cpm_teacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response

@permission_required('auth.add_user')
def itempool_add(request):
    tp, res = getTpByRequest(request, "login")
    if not tp and res:
        return res
    if request.method == "POST":
        form = CPM_ItemPoolDetailForm(request.POST, teacher=tp)
        if form.is_valid():
            pass
    else:
        itempoolid = request.GET.get('itempoolid')
        try:
            i = CPM_Itempool.objects.get(id=itempoolid)
        except:
            form = CPM_ItemPoolDetailForm(teacher=tp)
        else:
            form = CPM_ItemPoolDetailForm(teacher=tp,
                                      initial={'itempoolid': i.id,
                                               'itempoolname': i.itp_poolname})
    return render_to_response('cpm_itempool_detail.html', {'form': form},
                              context_instance=RequestContext(request))

def __getItempool(itempoolid, tp=None):
    if not itempoolid or itempoolid == "-1":
        if tp:
            return CPM_Itempool.objects.create(itp_teacher=tp)
        else:
            return None
    return get_object_or_404( CPM_Itempool, id=int(itempoolid))



class CPM_AssignmentDelete(DeleteView):
	model = CPM_Assignment
	success_url = reverse_lazy("deleteview_callback")

	def get_object(self):
		pk = self.request.POST['assignmentid']
		return get_object_or_404(CPM_Assignment, id=pk)

@permission_required('auth.add_user')
def cpm_assignment_updatename(request):
    # logger.info("assignment updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if not tp:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    assignmentid = request.GET.get('assignmentid').strip()
    assignmentname = request.GET.get('assignmentname')
    if assignmentid and assignmentid != '-1' and assignmentname:
        try:
            assignment = CPM_Assignment.objects.get(id=int(assignmentid), teacher=tp)
        except:
            pass
        else:
            assignment.assignmentname = assignmentname
            assignment.teacher = tp
            assignment.save()
            response_data['assignmentid'] = assignment.id
            response_data['assignmentname'] = assignment.asm_assignmentname
            response_data['description'] = assignment.asm_description.replace('</br>', '\n')
            response_data['testdate'] = assignment.asm_datecreated.strftime("%m/%d/%Y %H:%M")
            response_data['testdue'] = assignment.asm_deadline.strftime("%m/%d/%Y %H:%M")
            papers = CPM_Paper.objects.filter(assignment=assignment)
            response_data['papers'] = list(p.id for p in papers)
            response_data['state'] = 'success'
            # logger.info(papers)
    elif assignmentid == '-1':
        try:
            assignment = CPM_Assignment.objects.create(teacher=tp)
        except:
            pass
        else:
            response_data['assignmentid'] = assignment.id
            response_data['assignmentname'] = assignment.asm_assignmentname
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


@permission_required('auth.add_user')
def cpm_assignment_getstudents(request):
    # logger.info("assignment_getstudents")
    if request.method == "POST":
        assignmentid = request.POST['assignmentid']
        view = request.POST.get('view', False)
        teacher, res = getTpByRequest(request, None)
        # logger.info("assignment_getstudents, teacher:%s,assignmentid:%s" % (teacher, assignmentid))
        try:
            assignment = CPM_Assignment.objects.get(id=assignmentid)
            checkedstudents = assignment.asm_students.all()
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
        # logger.info("assignment_getstudents finished")
        return render_to_response('classroom_getstudents.json',
                                  {'stu_teacher_list': stu_teacher_list,
                                   'tnum': len(stu_teacher_list)},
                                  context_instance=RequestContext(request))





@login_required
def cpm_assignment_add(request):
    teacher, res = getTpByRequest(request, None)
    if request.method == "POST":
        form = CPM_AssignmentDetailForm(request.POST, teacher=teacher)
	# logger.info('form: %s' % form)
        if form.is_valid():
            if not teacher:
                student, res = getSpByRequest(request, None)
                teacher = student.teacher
            # logger.info("assignment add:%s" % teacher)
            assignmentid = int(form.cleaned_data['assignmentid'])
            if assignmentid != -1:
                assignment = CPM_Assignment.objects.get(id=assignmentid)
                assignment.teacher = teacher
            else:
                assignment = CPM_Assignment.objects.create(asm_assignmentname=form.cleaned_data['assignmentname'],
                                                       teacher=teacher)

            # logger.info("assignment:%s" % assignment)
            assignment.asm_datecreated = form.cleaned_data['testdate']
            assignment.asm_deadline = form.cleaned_data['deadline']
            assignment.asm_description = form.cleaned_data['description']
            studentlist = form.cleaned_data['students']
            __updatestuinassignment(assignment, studentlist)
            paperlist = form.cleaned_data['papers']
            __updatepaperinassignment(assignment, paperlist)
            assignment.save()
            messages.add_message(request, messages.SUCCESS, "One Assignment Added")
            return redirect("/cpm/assignment/add?assignmentid=" + str(assignment.id))
        else:
            # logger.info("form invalid")
            messages.add_message(request, messages.SUCCESS, "You missed some values")
    else:
        assignmentid = request.GET.get('assignmentid')
        form = CPM_AssignmentDetailForm(teacher=teacher)
        if assignmentid:
            try:
                assignment = CPM_Assignment.objects.get(id=assignmentid)
            except:
                form = CPM_AssignmentDetailForm(teacher=teacher)
                # logger.info("assignment not found:%s" % assignmentid)
            else:
                # logger.info("paper:%s" % MCQ_Assignment)
                papers = CPM_Paper.objects.filter(assignment=assignment)
                form = CPM_AssignmentDetailForm(teacher=teacher,
                                            initial={'assignmentid': assignment.id,
                                                     'papername': assignment.asm_assignmentname,
                                                     'testdate': assignment.asm_datecreated,
                                                     'deadline': assignment.asm_deadline,
                                                     'description': assignment.asm_description.replace('</br>', '\n'),
                                                     'papers': papers})
    return render_to_response('cpm_assignment_detail.html',
                              {'form': form},
                              context_instance=RequestContext(request))



@login_required
def cpm_assignment_add(request):
    teacher, res = getTpByRequest(request, None)
    if request.method == "POST":
        form = CPM_AssignmentDetailForm(request.POST, teacher=teacher)
	# logger.info('form: %s' % form)
        if form.is_valid():
            if not teacher:
                student, res = getSpByRequest(request, None)
                teacher = student.teacher
            # logger.info("assignment add:%s" % teacher)
            assignmentid = int(form.cleaned_data['assignmentid'])
            if assignmentid != -1:
                assignment = CPM_Assignment.objects.get(id=assignmentid)
                assignment.teacher = teacher
            else:
                assignment = CPM_Assignment.objects.create(asm_assignmentname=form.cleaned_data['assignmentname'],
                                                       teacher=teacher)

            # logger.info("assignment:%s" % assignment)
            assignment.asm_datecreated = form.cleaned_data['testdate']
            assignment.asm_deadline = form.cleaned_data['deadline']
            assignment.asm_description = form.cleaned_data['description']
            studentlist = form.cleaned_data['students']
            __updatestuinassignment(assignment, studentlist)
            paperlist = form.cleaned_data['papers']
            __updatepaperinassignment(assignment, paperlist)
            assignment.save()
            messages.add_message(request, messages.SUCCESS, "One Assignment Added")
            return redirect("/cpm/assignment/add?assignmentid=" + str(assignment.id))
        else:
            # logger.info("form invalid")
            messages.add_message(request, messages.SUCCESS, "You missed some values")
    else:
        assignmentid = request.GET.get('assignmentid')
        form = CPM_AssignmentDetailForm(teacher=teacher)
        if assignmentid:
            try:
                assignment = CPM_Assignment.objects.get(id=assignmentid)
            except:
                form = CPM_AssignmentDetailForm(teacher=teacher)
                # logger.info("assignment not found:%s" % assignmentid)
            else:
                # logger.info("paper:%s" % MCQ_Assignment)
                papers = CPM_Paper.objects.filter(assignment=assignment)
                form = CPM_AssignmentDetailForm(teacher=teacher,
                                            initial={'assignmentid': assignment.id,
                                                     'papername': assignment.asm_assignmentname,
                                                     'testdate': assignment.asm_datecreated,
                                                     'deadline': assignment.asm_deadline,
                                                     'description': assignment.asm_description.replace('</br>', '\n'),
                                                     'papers': papers})
    return render_to_response('cpm_assignment_detail.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def __updatepaperinassignment(assignment, paperlist):
    try:
        papers = CPM_Paper.objects.filter(assignment=assignment)
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
def getall_cpm_itempool(request):
	# logger.info("mcq = itempool getall...")
	tp, res = getTpByRequest(request, "login")
	if not tp and res:
		return res
	itempools = []
	if tp:
		try:
			itempools = CPM_Itempool.objects.filter(itp_teacher=tp)
		except:
			pass
	response = render_to_response('cpm_itempool_all.json',
                                  {'itempools': itempools},
                                  context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response



@login_required
def getall_cpm_paper(request):
    if request.method == 'POST':
        pids = request.POST.get('pids')
        student, res = getSpByRequest(request, None)
        if pids and not student:
            takedpaperlist = __teachermarkreport(pids)
        elif student:
            takedpaperlist = __studentmarkreport(student)
        response = render_to_response('cpm_paper_mark.json', {'takedpaperlist': takedpaperlist},
                                      context_instance=RequestContext(request))
    else:
        forwhat = request.GET.get('forwhat')
        if forwhat == 'teacher_report':
            """
               teacher_report default datatable
            """
            try:
                papers = CPM_Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('cpm_paper_report.json',
                                          {'papers': papers},
                                          context_instance=RequestContext(request))
        else:
            """
                teacher get all paper ztree
            """
            try:
                papers = CPM_Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('cpm_paper_all.json', {'papers': papers},
                                          context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def getall_cpm_assignment(request):
	teacher, res = getTpByRequest(request, None)
	if not teacher:
		student, res = getSpByRequest(request, None)
		teacher = student.teacher
	try:
		assignments = CPM_Assignment.objects.filter(teacher=teacher)
	except Exception as e:
		assignments = []
	try:
		forwhat = request.GET.get('forwhat')
	except:
		forwhat = 'default'

	if forwhat == 'teacher_report':
		response = render_to_response('teacherreport_assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))
	else:
		response = render_to_response('cpm_assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response


@permission_required('auth.add_user')
def cpm_questioncategory_view(request):
	tp, res = getTpByRequest(request, 'login')
	strOutput = "<ul>"
	if not tp and res:
		return res
	try:	
		#if tp.user.username != "IBAlevelecons":
		if not tp.user.username in settings.MASTER_USERS:
			strOutput = mark_safe(strOutput + "</ul>")
			return render_to_response('mcq_questioncategory_denied.html',
				{'errormessage': 'Access is Denied!!!'},
				context_instance=RequestContext(request))
		lst_questioncategory = CPM_QuestionCategory.objects.filter(qct_sequence=0)
	except  Exception as e :
		logger.debug("error %s " % e)
		lst_questioncategory = []
	for rowObj in lst_questioncategory:
		strOutput = strOutput + "<li>" + cpm_questioncategory_generateSub(rowObj) + "</li>"
	
	strOutput = mark_safe(strOutput + "</ul>")
	return render_to_response('cpm_questioncategory_detail.html',
			{'testtree': strOutput},
			context_instance=RequestContext(request))

@permission_required('auth.add_user')
def cpm_question_submit(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        tp, res = getTpByRequest(request, None)
        questionid = request.POST.get('questionid')
        itempoolid = request.POST.get('itempoolid')
        question_content = request.POST.get('question_content')
        question_mark = request.POST.get('question_mark')
	question_category = request.POST.get('curquestioncategory')
	logger.info('minhong1 %s ' % question_category)
        try:
            itempool = CPM_Itempool.objects.get(itp_teacher=tp, id=int(itempoolid))
            question = CPM_Question.objects.get(id=int(questionid))
        except Exception as e:
            logger.error(e)
            itempool = None
            question = None
        else:
            logger.error('test1')
            if not question_content:
		try:
		    	logger.error('test1a')
		        #question.infocompleted &= ~Question.QUESTIONCOMPLETED
		    	logger.error('test1b')
		        question.save()
		    	logger.error('test1c')
		except Exception as Err:
			logger.debug(Err)
            else:
		try:
			try:
		            	logger.error('test2a')
				logger.info('ok...something i get this %s' % question_category)
				
		            	logger.error('test2b')
				getQuestionCategory = CPM_QuestionCategory.objects.get(id=int(question_category))
		            	logger.error('test2c')
			except:
				getQuestionCategory = None
			if question_mark == None:
				question_mark = "0"
			
	            	logger.error('test3a')
		        question.qtn_name = request.POST.get('question_name')
		        question.qtn_description = request.POST.get('question_desc')
		        question.qtyn_type = request.POST.get('question_type')
		        question.itempool = itempool
	            	logger.error('test3b')
		        question.teacher = tp
			if getQuestionCategory != None:
			        question.qtn_questioncategory = getQuestionCategory
	            	logger.error('test3c')
		        question.qty_html = stripBody(question_content)
	            	logger.error('test3d')
		        question.qtn_mark = int(question_mark)
	            	logger.error('test3e')
		        question.qty_text = stripHTMLStrings(strip_tags(question_content))
	            	logger.error('test3f')
		        question.save()
		        response_data['state'] = 'success'
		except Exception as e:
			logger.debug('%s (%s)' % (e.message, type(e)))
			response_data = {'state': 'failure'}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")
	

@permission_required('auth.add_user')
def cpm_question_add(request):
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	questionid = request.GET.get('questionid')
	selitempoolid = request.GET.get('itempoolid')
	try:
		itempools = CPM_Itempool.objects.filter(itp_teacher=tp)
	except:
		itempools = []
	try:
		questions = CPM_Question.objects.filter(teacher=tp)
	except:
		questions = []

    	questioncategory = []
	try:
		lst_teacher = [tp]
		lst_questioncategory = CPM_QuestionCategory.objects.filter(qct_sequence=0, qct_teacher__in = lst_teacher)

	except Exception as e:
		logger.info('question category exception %s' % e)
		lst_questioncategory = []
	for rowQC in lst_questioncategory: #==== Array 1 ========
		questioncategory.append([rowQC.id , rowQC.qct_description, rowQC.qct_sequence])
		#jsonTemp = __getQuestionCategory(rowQC,rowQC.qct_description, questioncategory)
		__getQuestionCategory(rowQC,rowQC.qct_description, questioncategory,tp)
		 
	return render_to_response('cpm_question_detail.html',
			{'selitempoolid': selitempoolid,
			'questioncategorys':questioncategory,
			'questionid': questionid,
			'itempools': itempools,
			'questions': questions},
			context_instance=RequestContext(request))

@permission_required('auth.add_user')
def cpm_question_updatename(request):
	response_data = {"state": "failure"}
	tp, res = getTpByRequest(request, None)
	if tp and request.method == 'POST':
		questionid = request.POST.get("questionid")
		questionname = request.POST.get("questionname")
		itempoolid = request.POST.get("itempoolid")
		questiontype = request.POST.get("questiontype")
		questionmark = request.POST.get("questionmark")
		questioncategoryid = request.POST.get("curquestioncategory")
		logger.info('questioncategoryid %s' % questioncategoryid)
		try:
			itempool = CPM_Itempool.objects.get(id=int(itempoolid))
		except:
			itempool = None
		try:
			categoryobj = CPM_QuestionCategory.objects.get(id=int(questioncategoryid))
		except Exception as e:
			logger.info("exception get question category %s " % e)
			categoryobj = None
		if questionid and questionname and itempool:
			logger.info("this is the questionid: %s" % questionid)
			if questionid == "-1":
				if categoryobj == None:
					question = CPM_Question.objects.create(teacher=tp,
								   qtn_name=questionname.strip(),
								   qtyn_type=questiontype,
								   itempool=itempool)
				else:
					question = CPM_Question.objects.create(teacher=tp,
							   qtn_name=questionname.strip(),
							   qtyn_type=questiontype,
							   itempool=itempool,
							   qtn_questioncategory=categoryobj)

			else:
				question = CPM_Question.objects.get(id=int(questionid.strip()))
				question.qtn_name = questionname.strip()
				question.qtn_category = questiontype
				question.qtn_mark = int(questionmark)
				question.qtn_questioncategory = categoryobj
				question.save()
			response_data['questionid'] = question.id
			response_data['questiontype'] = question.qtyn_type
			response_data['description'] = question.qtn_description
			response_data['state'] = "success"
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

def __getquestiondetail(questionid):
    """
    get question detais: desc, type, question_content, standard_content, itempool,
    canvas, imgthumbnails
    """
    if not questionid or questionid is '-1':
        return {'state': 'No Resource'}
    try:
	question = CPM_Question.objects.get(id=int(questionid))
	questioncat_id = 0
	try:
		questioncat_id = question.qtn_questioncategory.id
	except Exception as e:
		#logger.debug('this is error exception for get questioncat %s ' % e)
		questioncat_id= 0
        
        response_data = {'question_desc': question.qtn_description,
                         'question_type': question.qtyn_type,
                         'question_content': question.qty_html,
                         'standard_content': question.qty_text,
                         'question_questioncategory': questioncat_id,
                         'question_mark': question.qtn_mark,
                         'question_item': question.itempool.id}
	response_data['state'] = 'success'
    except Exception as e:
        return {'state': 'No Resource'}
    return response_data



@permission_required('auth.add_user')
def cpm_question_get(request):
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp and request.method == 'POST':
        questionid = request.POST.get("questionid")
        response_data = __getquestiondetail(questionid)
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

@permission_required('auth.add_user')
def cpm_question_updatename(request):
	response_data = {"state": "failure"}
	tp, res = getTpByRequest(request, None)
	if tp and request.method == 'POST':
		questionid = request.POST.get("questionid")
		questionname = request.POST.get("questionname")
		itempoolid = request.POST.get("itempoolid")
		questiontype = request.POST.get("questiontype")
		questionmark = request.POST.get("questionmark")
		questioncategoryid = request.POST.get("curquestioncategory")
		logger.info('questioncategoryid %s' % questioncategoryid)
		try:
			itempool = CPM_Itempool.objects.get(id=int(itempoolid))
		except:
			itempool = None
		try:
			categoryobj = CPM_QuestionCategory.objects.get(id=int(questioncategoryid))
		except Exception as e:
			logger.info("exception get question category %s " % e)
			categoryobj = None
		if questionid and questionname and itempool:
			logger.info("this is the questionid: %s" % questionid)
			if questionid == "-1":
				if categoryobj == None:
					question = CPM_Question.objects.create(teacher=tp,
								   qtn_name=questionname.strip(),
								   qtyn_type=questiontype,
								   itempool=itempool)
				else:
					question = CPM_Question.objects.create(teacher=tp,
							   qtn_name=questionname.strip(),
							   qtyn_type=questiontype,
							   itempool=itempool,
							   qtn_questioncategory=categoryobj)

			else:
				question = CPM_Question.objects.get(id=int(questionid.strip()))
				question.qtn_name = questionname.strip()
				question.qtn_category = questiontype
				question.qtn_mark = int(questionmark)
				question.qtn_questioncategory = categoryobj
				question.save()
			response_data['questionid'] = question.id
			response_data['questiontype'] = question.qtyn_type
			response_data['description'] = question.qtn_description
			response_data['state'] = "success"
	return HttpResponse(json.dumps(response_data), mimetype="application/json")


		
def __getQuestionCategory(parentQuestionCategory, parentDesc, lst_param,tp):
	#jsonArray = []
	lst_teacher = [tp]
	subArray = CPM_QuestionCategory.objects.filter(qct_sequence=parentQuestionCategory.qct_sequence + 1, qct_QuestionCategory_parentid= parentQuestionCategory.id, qct_teacher__in = lst_teacher)
	#logger.info("got array teacher %s " % lst_teacher)
	if subArray != None:
		for rowEach in subArray:
			#logger.info("got array rowEach %s " % rowEach)
			parentDesc =__addSpaceQuestionCategory(rowEach.qct_sequence) + "> " + rowEach.qct_description
			#logger.info('rowEach %s ' % rowEach)
			#jsonArray.append([rowEach.id, parentDesc, rowEach.qct_sequence])
			lst_param.append([rowEach.id, parentDesc, rowEach.qct_sequence])
			#jsonTemp = __getQuestionCategory(rowEach,parentDesc,lst_param)
			__getQuestionCategory(rowEach,parentDesc,lst_param,tp)
			#if jsonTemp != []:
			#	jsonArray.append(jsonTemp)
	else:
		logger.info("got array %s " % subArray)
	return ""	


def __addSpaceQuestionCategory(intLoop):
	strValue = ""
	for _ in range(intLoop):
		strValue = strValue + "="
	return strValue
		


@permission_required('auth.add_user')
def cpm_questioncategory_add(request):
	tp, res = getTpByRequest(request, 'login')
	txtid=request.GET.get('id')
	txtseq=request.GET.get('seq')
	
	return render_to_response('cpm_questioncategory_add.html',
			{'txtID': txtid,
			'txtSeq':txtseq},
			context_instance=RequestContext(request))


	
@permission_required('auth.add_user')
def cpm_questioncategory_save(request):
	response_data = {'state': 'failure'}
	tp, res = getTpByRequest(request, 'login')
	txtID=request.POST.get('txtID')
	txtQuestCat=request.POST.get('txtQuestCat')
	txtDesc=request.POST.get('txtDesc')
	txtSeq=request.POST.get('txtSeq')
	txtParentid=request.POST.get('txtParentid')
	if not tp and res:
		return res
	try:
		if txtID == "0":
			rowQuestCat = CPM_QuestionCategory.objects.create(qct_category=txtQuestCat,
							   qct_description=txtDesc,
							   qct_sequence=int(txtSeq),
							   qct_QuestionCategory_parentid=int(txtParentid))
			logger.info('new id %s ' % rowQuestCat)
			response_data['newID'] = rowQuestCat.id
		else:
			rowQuestCat = CPM_QuestionCategory.objects.get(id=int(txtID))
			rowQuestCat.qct_description = txtDesc
			logger.info('the desc: %s ' % txtDesc)
			response_data['state'] = "success"
			rowQuestCat.save()

	except Exception as E:
		rowQuestCat = None
		logger.debug(E)
	
			
	return HttpResponse(json.dumps(response_data), mimetype="application/json")		
	

def cpm_questioncategory_generateSub(rowObj):
	logger.info('generatesub %s' % rowObj)
	strOutput = " <a href='/cpm/questioncategory/edit/?row=" + str(rowObj.id) + "' >" + rowObj.qct_category + "</a>"
	try:
		lst_childCategory = CPM_QuestionCategory.objects.filter(qct_QuestionCategory_parentid=rowObj.id)
	except:
		lst_childCategory = []
	b_isEmpty = True
	if lst_childCategory != []:
		b_isEmpty = False
		strOutput = strOutput + "<ul>"
	logger.info('%s' % lst_childCategory)
	for rowchild in lst_childCategory:
		strID = ('%s' % rowchild.id)
		logger.info('strID %s' % strID)
		strOutput = strOutput + "<li> " + cpm_questioncategory_generateSub(rowchild) + " </li>"
	if b_isEmpty != True:
		strOutput = strOutput + "</ul>"
	return strOutput

@permission_required('auth.add_user')
def cpm_questioncategory_edit(request):
	tp, res = getTpByRequest(request, 'login')
	strRow=request.GET.get('row')
	if not tp and res:
		return res
	try:
		rowQuestCat = CPM_QuestionCategory.objects.get(id=int(strRow))
	except:
		rowQuestCat = None
	if rowQuestCat != None:
		logger.info('rowQuestCat %s' % rowQuestCat)
	return render_to_response('cpm_questioncategory_edit.html',
			{'rowQuestCat': rowQuestCat},
			context_instance=RequestContext(request))		
	


def getCPMCategoryTeacherList(request):
    """
    This function is used for display all teacher in select box.
    If view mode it show selected teacher only with disabled function.
    If modify mode it show the selected teacher without disabled function.
    :param request:
    :return Json Response of teacher_list.json file the data.
    """
	#logger.info('fall in option 2')
    qnum = 0
    tb, res = getTpByRequest(request, None)
    view = 0
    if request.method == 'POST': 
        questioncategory_id = request.POST['questioncategory_id']
        view = request.POST['view']
        ztreejson = __questionCategoryteacherJsonList(tb, view)
        #print ztreejson
        response = render_to_response('cpm_questioncategoryteacher_list.json',
                                      {'questiontree': ztreejson,
                                       'inum': len(ztreejson), 'qnum': qnum},
                                      context_instance=RequestContext(request))
        response['Content-Type'] = 'text/plain; charset=utf-8'
        response['Cache-Control'] = 'no-cache'
        return response
    else:
	#logger.info("getMCQCategoryTeacherList 2")
        view = request.GET.get('view')
        questioncategory_id = request.GET.get('questioncategory_id')
        #print view,"view", questioncategory_id, "questioncategory_id"
        if view:# Itempool view mode selected
	    itempool = CPM_QuestionCategory.objects.get(id=int(questioncategory_id))
            ztreejson = __questionCategoryteacherJsonList(tb, view, itempool)
            #print ztreejson
            response = render_to_response('cpm_questioncategoryteacher_list.json',
                                          {'questiontree': ztreejson,
                                           'inum': len(ztreejson), 'qnum': qnum},
                                          context_instance=RequestContext(request))
            response['Content-Type'] = 'text/plain; charset=utf-8'
            response['Cache-Control'] = 'no-cache'
            return response
        else:# Other than view mode either add item or modify item.
	    #logger.info("getMCQCategoryTeacherList 2b  [questioncategory_id: %s ] " % questioncategory_id )
            print('yes')
            if questioncategory_id and int(questioncategory_id) != -1:
	    	logger.info("getMCQCategoryTeacherList 2a1")
                #Modify mode of selected box
                modify = True
                itempool = CPM_QuestionCategory.objects.get(id=int(questioncategory_id))
                ztreejson = __questionCategoryteacherJsonList(tb, view, itempool, modify)
                response = render_to_response('cpm_questioncategoryteacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response
            else: 
                ztreejson = __questionCategoryteacherJsonList(tb, view)
                print(ztreejson)
                response = render_to_response('cpm_questioncategoryteacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response



def __questionCategoryteacherJsonList(teacher, view, questioncategory=None, modify=None):
    """
    This function return the teacher list with select box option
    like checked=true, disabled=true, checked=false, disabled=false

    :param teacher: request user of teacher
    :param view: view condition checking parameter
    :param questioncategory: Check the questioncategory available or not
    :param modify: Modify condition checking parameter.
    :return ztreejson: List of teacher with based on conditions
    """
    ztreejson = list()
    if view:
	logger.info("questionCategoryteacherJsonList 1")
        selected_teacher = questioncategory.qct_teacher.all()
        teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
    else:
        if modify:
	    logger.info("questionCategoryteacherJsonList 2")
            selected_teacher = questioncategory.qct_teacher.all()#.exclude(user=teacher.user)
	    logger.info("selected_teacher: to check the query %s " % selected_teacher)
            #==== In case is sub, we need to show only parent 's selected teacher
	    parentID = questioncategory.qct_QuestionCategory_parentid
	    if questioncategory.qct_QuestionCategory_parentid == 0:
	    	#=============================================================
		#  no parent, straight proceed to retrieve full teacher list
		#  from TProfile.
	    	#=============================================================
		teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
		logger.info("no parent")
	    else:
		parent_questioncategory = CPM_QuestionCategory.objects.get(id=questioncategory.qct_QuestionCategory_parentid)
		
		logger.info("parent_questioncategory: to check the query %s " % parent_questioncategory)
            	teacher_list = TProfile.objects.filter(user__in = parent_questioncategory.qct_teacher.all()).exclude(user__in= questioncategory.qct_teacher.all())
			
		logger.info("got parent : list is %s " % teacher_list)
	    logger.info("questioncategory ID ====== : %s " % parentID)
	    
            
            
        else:
            logger.info("questionCategoryteacherJsonList 3")
            teacher_list = TProfile.objects.all().exclude(user = teacher.user)
    teacher_head = {'name': 'Teacher', 'checked': 'false'}
    if view:
        teacher_head['disabled'] = 'true'
    else:
        teacher_head['disabled'] = 'false'
    teacher_node_list = list()
    if view:
	logger.info("questionCategoryteacherJsonList 1a")
        
        for teacher in questioncategory.qct_teacher.all():
            teacher_node_list.append({'node':teacher, 'checked':'true', 'disabled':'true'})
    else:
        if modify:
	    logger.info("questionCategoryteacherJsonList 2a")
	    #logger.info("=======%s" % teacher.user)
            #teacher_node_list = [{'node':teacher, 'checked':'true', 'disabled':'true'}]
	    filterTeacher = teacher
	    logger.info("A =======%s" % filterTeacher)
            for teacher in questioncategory.qct_teacher.all(): #.exclude(user=filterTeacher):
		#if filterTeacher.user != teacher.user:
	    	logger.info("A =======%s" % teacher.user)
	        teacher_node_list.append({'node':teacher, 'checked':'true', 'disabled':'false'})
        else:
	    #logger.info("questionCategoryteacherJsonList 3a")
            teacher_node_list = [{'node':teacher, 'checked':'true', 'disabled':'true'}]
    if teacher_list:
	#logger.info("teacher_list %s " % teacher_list)
        for teach in teacher_list:
	    
	    logger.info("b =======%s" % teach)
            teacher_node = {'node':teach, 'checked':'false'}
            if view:
                teacher_node['disabled'] = 'true'
		logger.info("b =======%s is %s" % (teach , "true"))
            else:
                teacher_node['disabled'] = 'false'
		logger.info("b =======%s is %s" % (teach , "false"))
            teacher_node_list.append(teacher_node)
	logger.info("888888teacher_node_list: %s " % teacher_node_list)
        ztreejson.append([teacher_head, teacher_node_list])
    #logger.info("ztreejson %s " % ztreejson)
    return ztreejson












def addCPMCategoryteacher(request):
	"""
	This is post method. When addteacher button clicked then selected teacher
	will come in post method. We save the teacher data in itempool and return
	the success response
	:param request:
	:return {'response':'success'} or {'response':'failure'}:
	"""
	if request.method == 'POST':
		try:
			logger.info("testing1")
			questioncategory_id = request.POST['questioncategory_id']
			teacher_ids = request.POST.get('teacher_ids')
			logger.info("question a")
			teacher_list = teacher_ids[1:-1].split(',')[1:]
			logger.info("question b %s " % teacher_list)
			teacher_list = [int(i.strip('"')) for i in teacher_list]
			logger.info("question c")
			print(type(teacher_ids), teacher_ids)
			if int(questioncategory_id) != -1:
				logger.info("question 1")
				QuestionCategory = CPM_QuestionCategory.objects.get(id = int(questioncategory_id))
				QuestionCategory.qct_teacher.clear() 
				lst_teacher = TProfile.objects.filter(user_id__in=teacher_list)
				QuestionCategory.qct_teacher.add(*lst_teacher)
				try:
					QuestionCategory.save()
				except Exception as err:
					logger.info("error while saving QuestionCategory: %s" % err)
				logger.info("count for teachers: %s" % lst_teacher) 
				return HttpResponse(json.dumps({'response':'success'}))
			else:
				return HttpResponse(json.dumps({'response':'failure'}))
		except Exception as e:
			logger.error(e)
	return HttpResponse(json.dumps({'response':'failure'}))

@permission_required('auth.add_user')
def cpm_questioncategory_delete(request):
	txtID=request.POST.get('txtID')
	response_data = {'state': 'failure'}
	
	try:
		rowQuestCat = CPM_QuestionCategory.objects.get(id=int(txtID))
		rowQuestCat.delete()
		response_data['state'] = "success"
	except Exception as E:
		rowQuestCat = None
		logger.debug(E)
	return HttpResponse(json.dumps(response_data), mimetype="application/json")



@login_required
def cpm_optionlist_getby_question(request):
	tp, res = getTpByRequest(request, "login")
	if not tp and res:
		logger.info('shit ..return')
		return res
	clozelisting = []
	if tp:
		try:
			questionid = request.GET.get("questionid")
			questionObj=CPM_Question.objects.filter(id=int(questionid))
			clozelisting = CPM_Answer.objects.filter(question=questionObj)
			logger.info('clozelisting : %s' % clozelisting)
		except Exception as e:
			logger.info('shit ..rerror %s' % e)
			pass
	response = render_to_response('cpm_clozeanswer.json',
                                  {'clozelisting': clozelisting},
                                  context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response

#class CPM_Answer(models.Model):
#	ans_code = models.TextField(max_length=255)
#	ans_mark = models.IntegerField(default=0)
#	question = models.ForeignKey(CPM_Question)
#	ans_mark = models.IntegerField(default=0)
#	ans_answer= models.TextField(max_length=255) 




@permission_required('auth.add_user')
def cpm_clozelist_add(request):
	logger.info("mcq_optionlist_add")
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	try:
		logger.info("mcq_optionlist_add 1")
		questionid = request.GET.get('questionid')
		clozelistid = request.GET.get('clozelistid')
		if clozelistid  is not None :  # if is not blank mean is modify mode.
			logger.info("mcq_optionlist_add 1a")
			optionRow = CPM_Answer.objects.get(id=int(clozelistid))
			clozelisting = CPM_Answer.objects.filter(question=optionRow.question)
		else:
			logger.info("mcq_optionlist_add 1b")
			question = CPM_Question.objects.get(id=questionid)
			clozelisting = CPM_Answer.objects.filter(question=question)
	except Exception as e:
		logger.debug('%s (%s)' % (e.message, type(e)))
		clozelisting = []

	if clozelistid  is not None : 
		logger.info("mcq_optionlist_add 2a")
		return render_to_response('cpm_clozelist_detail.html',
			{'questionid': questionid,
			'clozelisting': clozelisting,
			'clozelst':optionRow},
			context_instance=RequestContext(request))
	else:
		logger.info("mcq_optionlist_add 2b")
		return render_to_response('cpm_clozelist_detail.html',
			{'questionid': questionid,
			'clozelisting': clozelisting},
			context_instance=RequestContext(request))






@permission_required('auth.add_user')
def mcq_optionlist_add(request):
	logger.info("mcq_optionlist_add")
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	try:
		questionid = request.GET.get('questionid')
		clozelistid = request.GET.get('clozelistid')
		if clozelistid  is not None :  # if is not blank mean is modify mode.
			optionRow = CPM_Answer.objects.get(id=int(clozelistid))
			clozelisting = CPM_Answer.objects.filter(question=optionRow.question)
		else:
			question = CPM_Question.objects.get(id=questionid)
			clozelisting = CPM_Answer.objects.filter(question=question)
	except Exception as e:
		logger.debug('%s (%s)' % (e.message, type(e)))
		clozelisting = []

	if clozelistid  is not None : 
		return render_to_response('cpm_clozelist_detail.html',
			{'questionid': questionid,
			'clozelisting': clozelisting,
			'cloze':optionRow},
			context_instance=RequestContext(request))
	else:
		return render_to_response('cpm_clozelist_detail.html',
			{'questionid': questionid,
			'clozelisting': clozelisting},
			context_instance=RequestContext(request))



@permission_required('auth.add_user')
def cpm_clozelist_updatefield(request):
	tp, res = getTpByRequest(request, None)
	response_data = {"state": "failure"}
	if request.method == 'POST':
		if tp:
			
			try:
				clozeID = request.POST.get('clozelist_id')
				questionID = request.POST.get('questionid')
				clozeName = request.POST.get('clozelist_name')
				clozeMark = request.POST.get('clozelist_mark')
				clozeAnswer = request.POST.get('clozelist_answer')  
				questionObject=CPM_Question.objects.get(id=int(questionID))
				response_data["clozelist_name"]=clozeName 
				response_data["clozelist_mark"]=clozeMark
				response_data["questionid"]=questionID
				response_data["clozelist_id"]=int(clozeID)
				logger.info('2111 : %s ' % clozeName )
				if clozeID == "-1":
					clozeObject = CPM_Answer.objects.create(ans_code=clozeName.strip(),
						ans_mark=0,ans_answer=clozeAnswer ,question=questionObject)
					response_data["clozelist_id"]=clozeObject.id;
				else:
					clozeObject = CPM_Answer.objects.get(id=int(clozeID.strip()))
					clozeObject.ans_name = clozeName.strip()
					logger.info('this is clozeMark %s' % clozeMark)
					clozeObject.ans_mark = int(clozeMark)
					clozeObject.ans_answer = clozeAnswer
					question=questionObject
					clozeObject.save()
				
				response_data["state"]="success"
			except Exception as e:
				logger.debug('%s (%s)' % (e.message, type(e)))
				
				response_data = {"state": "failure"}

	return HttpResponse(json.dumps(response_data), mimetype="application/json")

 
@permission_required('auth.add_user')
def cpm_optionlist_get(request):
	tp, res = getTpByRequest(request, None)
	response_data = {"state": "failure"}
	if request.method == 'POST':
		if tp:
			try:
				optionID = request.POST.get('KEYVALUE')
				optionlisting=CPM_Answer.objects.get(id=int(optionID))
				response_data = {"clozelist_name":optionlisting.ans_code, 
					"clozelist_answer":optionlisting.ans_answer, 
					"clozelist_mark":optionlisting.ans_mark,
					"clozelist_id":optionID 
					}
			
				response_data['state'] = 'success'
			except Exception as e:
				logger.debug('%s (%s)' % (e.message, type(e)))
				
				response_data = {"state": "failure"}
	return HttpResponse(json.dumps(response_data), mimetype="application/json")



class OptionlistDelete(DeleteView):
	success_url = reverse_lazy("deleteview_callback")
	model = CPM_Answer

	def get_object(self):	
		pk = self.request.POST['optionlistid']
		return get_object_or_404(CPM_Answer, id=pk)




#============================= Paper ==================================================================

@permission_required('auth.add_user')
def cpm_paper_add(request):
	tp, res = getTpByRequest(request, None)
	if request.method == "POST":
		form = CPM_PaperDetailForm(request.POST, teacher=tp)
		if form.is_valid():
			paperid = form.cleaned_data['paperid']
			papername = form.cleaned_data['papername']
			duration = form.cleaned_data['duration']
			passpoint = form.cleaned_data['passpoint']
			year = form.cleaned_data['year']
			subject = form.cleaned_data['subject']
			level = form.cleaned_data['level']
			papertype = form.cleaned_data['ptype']
			if paperid != -1:
				try:
					paper = CPM_Paper.objects.get(id=paperid)
				except:
					paper = CPM_Paper.objects.create(ppr_papername=papername,
							 ppr_passpoint=passpoint,
							 ppr_papertype=papertype, ppr_duration=duration,
							 year=year, subject=subject,
							 level=level, owner=request.user)
				else:
					paper.ppr_papername = papername
					paper.ppr_papertype = papertype
					paper.year = year
					paper.subject = subject
					paper.level = level
					paper.ppr_duration = duration
					paper.ppr_passpoint = passpoint
			else:
				try:
					paper = CPM_Paper.objects.create(ppr_papername=papername,
						ppr_passpoint=passpoint,
						ppr_papertype=papertype, ppr_duration=duration,
						year=year, subject=subject,
						level=level, owner=request.user)
				except:
					paper = None
			questionlist = form.cleaned_data['questionlist']
			paper.ppr_total = len(questionlist)
			# logger.info("questionlist:%s" % questionlist)
			__updatequestioninpaper(questionlist, paper)
			# logger.debug('ok...ok....questionlist : %s' % questionlist)
			paper.ppr_questionseq = pickle.dumps([q.id for q in questionlist])
			paper.save()
			print(paper.ppr_questionseq)
			messages.add_message(request, messages.SUCCESS, "One Paper Added")
			# logger.info(' saved done, going to redirect page')
			return redirect("/cpm/paper/add?paperid=" + str(paper.id))
		else:
			logger.info(' ops.... got error for form.isvalid()')
	else:
		# logger.info(' ok ..inside mcq paper add get')
		paperid = request.GET.get('paperid')
		if paperid:
			try:
				p = CPM_Paper.objects.get(id=int(paperid))
			except:
				logger.info("paper not found:%s" % paperid)
				form = CPM_PaperDetailForm(teacher=tp)
			else:	
				# logger.info("paper:%s" % p.ppr_papername)
				form = CPM_PaperDetailForm(teacher=tp,
				       initial={'paperid': p.id,
				       'papername': p.ppr_papername,
				       'duration': p.ppr_duration,
				       'passpoint': p.ppr_passpoint,
				       'year': p.year,
				       'subject': p.subject,
				       'level': p.level,
				       'ptype': p.ppr_papertype})
		else:
    			form = CPM_PaperDetailForm(teacher=tp)
	return render_to_response('cpm_paper_detail.html', {"form": form},
		context_instance=RequestContext(request))
@permission_required('auth.add_user')
def cpm_paper_updatename(request):
    # logger.info("paper updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp:
        paperid = request.GET.get('paperid')
        papername = request.GET.get('papername')
        if paperid and papername:
            paper = CPM_Paper.objects.get(id=int(paperid.strip()))
            if paper:
                paper.ppr_papername = papername
                paper.owner = tp.user
                paper.save()
                response_data['paperid'] = paper.id
                response_data['papername'] = paper.ppr_papername
		response_data['passpoint'] = paper.ppr_passpoint
                response_data['ptype'] = paper.ppr_papertype
                response_data['duration'] = paper.ppr_duration
                response_data['year'] = [paper.year.id, paper.year.yearname]
                response_data['subject'] = [paper.subject.id, paper.subject.subjectname]
                response_data['level'] = [paper.level.id, paper.level.levelname]
                response_data['state'] = 'success'
        elif not paperid:
            paper = CPM_Paper.objects.create(ppr_papername=papername,
                                         ppr_papertype='Formal', owner=tp.user)
            response_data['paperid'] = paper.id
            response_data['papername'] = paper.ppr_papername
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
def __updatequestioninpaper(questionlist, paper):
	# logger.debug("i'm in __updatequestioninpaper , Paper= %s" % paper)
	questions = CPM_Question.objects.filter(paper=paper)
	temp = []
	for q in questions:
		if q not in questionlist:
			questionseq = pickle.loads(str(paper.ppr_questionseq))
			questionseq.remove(q.id)
			q.paper.remove(paper)
			q.save()
			temp.append(q)
	for q in questionlist:
		if q not in temp:
			q.paper.add(paper)
			q.save()




def __teacher_closeness_info(pids):
	"""Returns data for summarization closeness band report (in support of paper_closeness.json)"""
	# TODO: reconcile with __teachermarkreport
	if not pids:
		return []
	closeness_band_students = [[] for i in range(NUM_CLOSENESS_BANDS)]
	try:
		paperids = [int(i) for i in pids.split(',')]
		papers = CPM_Paper.objects.filter(id__in=paperids)
	except Exception as e:
		papers = []
	logger.info('__teacher_closeness_info papers %s' % papers)
	total_num_scores = 0
	for p in papers:
		try:
			students = SProfile.objects.filter(cpm_assignment=p.assignment)
		except Exception as e:
			# logger.error('error here found')
			logger.error(e)
		for student in students:
			question_set = CPM_Question.objects.filter(paper=p)
			# Note: ignores earlier responses if question was retaken
			stuanswer_set = getTakedStuanswers(question_set, student,p,False)
			if stuanswer_set:
				mark = sum(ans.sta_mark for ans in stuanswer_set)
				# Average the question closeness scores
				closeness = sum(ans.sta_closeness if ans.sta_closeness else 0.0 for ans in stuanswer_set)
				closeness /= float(len(stuanswer_set))
				band = int(closeness * NUM_CLOSENESS_BANDS - 0.001)
				closeness_band_students[band].append(student.user.username)
				total_num_scores += 1
	# Format string with closeness band report
	closeness_band_info = []
	for band in range(NUM_CLOSENESS_BANDS):
		num_in_band = len(closeness_band_students[band])
		pct_in_band = round(num_in_band * 100.0 / total_num_scores, 1) if total_num_scores else 0.0
		student_names = ", ".join(closeness_band_students[band]) if (num_in_band > 0) else "n/a"
		closeness_band_info.append([(1 + band), pct_in_band, student_names])
	return closeness_band_info


@login_required
def cpm_paper_getall_closeness(request):
	try:
		#logger.info('mcq_paper_getall_closeness')
		pids = request.POST.get('pids')
		response = render_to_response('cpm_paper_closeness.json', 
				  {'closeness_band_info': __teacher_closeness_info(pids)},
				  context_instance=RequestContext(request))
		response['Content-Type'] = 'text/plain; charset=utf-8'
		response['Cache-Control'] = 'no-cache'
		return response
	except Exception as  Err:
		logger.debug("Error: %s" % Err)


@login_required
def cpm_paper_getall(request):
	if request.method == 'POST': 
		pids = request.POST.get('pids')
		student, res = getSpByRequest(request, None)
		if pids and not student:
			logger.info('mcq_paper_getall 1 , pids: %s' % pids)
			takedpaperlist = __teachermarkreport(pids)
		elif student:
			logger.info('mcq_paper_getall 2')
			takedpaperlist = __studentmarkreport(student)
		logger.info('use mcq_paper_mark.json')
		response = render_to_response('cpm_paper_mark.json', {'takedpaperlist': takedpaperlist},
			context_instance=RequestContext(request))
	else:
		logger.info('mcq_paper_getall zone 2')
		forwhat = request.GET.get('forwhat')
		logger.info('forwhat %s' % forwhat)
		if forwhat == 'teacher_report':
			"""
			teacher_report default datatable
			"""
			try:
				papers = CPM_Paper.objects.filter(owner=request.user)
			except:
				papers = []
			logger.info('use mcq_paper_report.json')
			response = render_to_response('cpm_paper_report.json',
				{'papers': papers},
				context_instance=RequestContext(request))
		else:
			"""
			teacher get all paper ztree
			"""
			try:
				papers = CPM_Paper.objects.filter(owner=request.user)
			except:
				papers = [] 
			response = render_to_response('cpm_paper_all.json', {'papers': papers},
				context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response




@login_required
def cpm_GetPaperInfoById(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        paperid = request.POST.get("paperid")
	logger.info('paperid %s ' % paperid)
        if paperid:
            try:
                paper = CPM_Paper.objects.get(id=int(paperid))
                response_data['papername'] = paper.ppr_papername
                response_data['duration'] = paper.ppr_duration
            except Exception as e:
		logger.error('is here...')
		#logger.error("MCQ_GetPaperInfoById Error: %s" % MCQ_GetPaperInfoById)
                print(e)
            else:
		try:
		        if paper.assignment:
		            response_data['assignment'] = paper.assignment.asm_assignmentname
		        if paper.year:
		            response_data['year'] = paper.year.yearname
		        if paper.level:
		            response_data['level'] = paper.level.levelname
		        if paper.subject:
		            response_data['subject'] = paper.subject.subjectname
		except Exception as e:
			logger.error(e)
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")





@login_required
def cpm_paper_getquestions(request):
	if request.method == "POST":
		paperid = request.POST['paperid']
		try:
			view = request.POST['view']
		except:
		    	view = 0
		teacher, res = getTpByRequest(request, None)
		student = None
		if not teacher:
		    	student, res = getSpByRequest(request, None)
		    	teacher = student.teacher
		# logger.info("paper_getquestions,paperid:%s,teacher:%s" % (paperid, teacher))

		print(paperid)
		if paperid and paperid != '-1':
			# logger.info("paper_getquestion ....option 1a")
		    	try:	
				# logger.info("paper_getquestion ....option 1a_1 , with paper id: %s " % paperid)
				paper = CPM_Paper.objects.get(id=int(paperid))
				# logger.info("paper_getquestion ....option 1a_2")
				print(paper.ppr_questionseq)
				# logger.info("paper_getquestion ....option 1a_3")
				questionseq = pickle.loads(str(paper.ppr_questionseq))
				# logger.info("paper_getquestion ....option 1a_4")
		    	except:
				paper = None
				questionseq = []
			try:
			    	if paper and questionseq:
					ztreejson, qnum, checkeditempools = __buildcheckeditempooltree(questionseq, view, student)
					try:
				    		totalitempool = CPM_Itempool.objects.filter(itp_teacher=teacher)
				    		itempools = list(set(totalitempool) - set(checkeditempools))
						# logger.info("paper_getquestion ....option 1b c")
					except:
				    		itempools = []
					else:
						# logger.info("paper_getquestion ....option 1b")
				    		ztreejson += __builduncheckeditempooltree(itempools, view, student)
				
			except Exception as e:
				logger.error(e)
		elif paperid == '-1':
	    		itempools = CPM_Itempool.objects.filter(itp_teacher=teacher)
	    		ztreejson = __builduncheckeditempooltree(itempools, view, student)
	    		qnum = 0
		else:
			ztreejson = []
			qnum = 0
		response = render_to_response('cpm_paper_allquestion.json',
		                              {'questiontree': ztreejson,
		                               'inum': len(ztreejson), 'qnum': qnum},
		                              context_instance=RequestContext(request))
		response['Content-Type'] = 'text/plain; charset=utf-8'
		response['Cache-Control'] = 'no-cache'
		return response


def __buildcheckeditempooltree(questionseq, view, student):
	# for checkeditempools
	checkeditempools = []
	for qid in questionseq:
		try:
			cq = CPM_Question.objects.get(id=qid)
		except:
			pass
		else:
			if cq.itempool not in checkeditempools:
				checkeditempools.append(cq.itempool)
	ztreejson = []
	qnum = 0
	for item in checkeditempools:
		questionnodes = []
		itemnode = {'name': item.itp_poolname, 'checked': 'true'}
		if view:
			itemnode['disabled'] = 'true'
		else:
			itemnode['disabled'] = 'false'
        # checkedquestions
		if student:
			checkedquestions = CPM_Question.objects.filter(itempool=item, id__in=questionseq,
				                               qtype="Review")
		else:
			checkedquestions = CPM_Question.objects.filter(itempool=item, id__in=questionseq)
		for q in checkedquestions:
			questionnode = {'node': q, 'checked': 'true'}
			if view:
				questionnode['disabled'] = 'true'
			else:
				questionnode['disabled'] = 'false'
			qnum += 1
			questionnodes.append(questionnode)
		if student:
            		uncheckedquestions = CPM_Question.objects.filter(itempool=item,                                                        
                                                         qtype="Review").exclude(id__in=questionseq)
		else:
			uncheckedquestions = CPM_Question.objects.filter(itempool=item
		                                                 ).exclude(id__in=questionseq)
		for q in uncheckedquestions:
			questionnode = {'node': q, 'checked': 'false'}
			if view:
				questionnode['disabled'] = 'true'
			else:
				questionnode['disabled'] = 'false'
			questionnodes.append(questionnode)
		ztreejson.append([itemnode, questionnodes])
    	return ztreejson, qnum, checkeditempools
def __updatestuinassignment(assignment, studentlist):
    try:
        students = CPM_Assignment.asm_students.all()
    except Exception as e:
	pass
	for s in studentlist:
	    # logger.info('adding new student list %s' % s)
	    assignment.asm_students.add(s)
    else:
        stemp = []
        for s in students:
            if s not in studentlist:
                assignment.students.remove(s)
                stemp.append(s)
        for s in studentlist:
            if s not in stemp:
                assignment.asm_students.add(s)
	# logger.info('ok...update student assignment done %s' % assignment)
def __builduncheckeditempooltree(itempools, view, student):
    # for uncheckeditempools
	ztreejson = []
	for item in itempools:
		questionnodes = []
		itemnode = {'name': item.itp_poolname, 'checked': 'false'}
		if view:
			itemnode['disabled'] = 'true'
		else:
			itemnode['disabled'] = 'false'
		# get question: if request from student, only qtype=Review
		if student:
			#questions = MCQ_Question.objects.filter(itempool=item,
			#	#infocompleted=Question.ALLCOMPLETED,
			#	qtyn_type="Review")
			questions = CPM_Question.objects.filter(itempool=item,
				qtyn_type="Review")
		else:
			#questions = Question.objects.filter(itempool=item,
			#	infocompleted=Question.ALLCOMPLETED)
			questions = CPM_Question.objects.filter(itempool=item)
		if questions:
			for q in questions:
				questionnode = {'node': q, 'checked': 'false'}
				if view:
					questionnode['disabled'] = 'true'
				else:
					questionnode['disabled'] = 'false'
				questionnodes.append(questionnode)
			ztreejson.append([itemnode, questionnodes])
	return ztreejson


class PaperDelete(DeleteView):
	# logger.info('ok.... in PaperDelete')
	model = CPM_Paper
	success_url = reverse_lazy("deleteview_callback")

	def get_object(self):
		pk = self.request.POST['paperid']
		return get_object_or_404(CPM_Paper, id=pk)

@permission_required('auth.add_user')
def mcq_paper_updatename(request):
    # logger.info("paper updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp:
        paperid = request.GET.get('paperid')
        papername = request.GET.get('papername')
        if paperid and papername:
            paper = CPM_Paper.objects.get(id=int(paperid.strip()))
            if paper:
                paper.ppr_papername = papername
                paper.owner = tp.user
                paper.save()
                response_data['paperid'] = paper.id
                response_data['papername'] = paper.ppr_papername
		response_data['passpoint'] = paper.ppr_passpoint
                response_data['ptype'] = paper.ppr_papertype
                response_data['duration'] = paper.ppr_duration
                response_data['year'] = [paper.year.id, paper.year.yearname]
                response_data['subject'] = [paper.subject.id, paper.subject.subjectname]
                response_data['level'] = [paper.level.id, paper.level.levelname]
                response_data['state'] = 'success'
        elif not paperid:
            paper = CPM_Paper.objects.create(ppr_papername=papername,
                                         ppr_papertype='Formal', owner=tp.user)
            response_data['paperid'] = paper.id
            response_data['papername'] = paper.ppr_papername
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
#============================= End Paper ==================================================================

class CPM_AssignmentDelete(DeleteView):
	model = CPM_Assignment
	success_url = reverse_lazy("deleteview_callback")

	def get_object(self):
		pk = self.request.POST['assignmentid']
		return get_object_or_404(CPM_Assignment, id=pk)

#=============================== REPORT=========================================================================

@permission_required('auth.add_user')
def cpm_report_teacher(request):
	group = getGroupNameByRequest(request)
	if group != 'teachers':
		return redirect('teacher_index')
	form = CPM_PaperSearchForm()
	if request.method == 'POST':
		pids = request.POST.get('paperids')
		return render_to_response('cpm_report_paper.html',
			{'form': form, 'pids': pids, 'group': group },
			context_instance=RequestContext(request))
	else:
		return render_to_response('cpm_report_teacher.html',
			{'form': form},
			context_instance=RequestContext(request))


@login_required
def mcq_report_student(request):
	group = getGroupNameByRequest(request)
	if group != 'students':
		logger.info('redirect to mcq_student_index')
		return redirect('mcq_student_index')
	form = CPM_PaperSearchForm()
	logger.info('use mcq_report_paper.html')
	return render_to_response('cpm_report_paper.html',
		              {'form': form},
		              context_instance=RequestContext(request))

@login_required
def mcq_report_studentanswer(request):
    form = []
    group = getGroupNameByRequest(request)
    #pids = [int(id) for id in request.POST.get('pids')]
    #stuids = [int(id) for id in request.POST.get('stuids')]
    #print pids, stuids
    
    if request.method == "POST":
        logger.debug("request.POST: %s" % request.POST)
        #get table list of all found papers after select table step 1
        paperids = request.POST.get('paperids')
        print(paperids,"paperids paperids")
        pids = []
        stuids = []
        if paperids:
	    logger.info('enter zone 1')
            try:
		logger.info('this is all paperids: %s' % paperids)
                paper_stu = re.findall(r'\{pid\:(\d+)\,\sstuid\:(\d+)\}', paperids)
		logger.info('this is all paper_stu: %s' % paper_stu)
            except Exception as e:
                logger.error(e)
            for pid, stuid in paper_stu:
		logger.info('this is each id : %s ' % pid)
                pids.append(int(pid))
                stuids.append(int(stuid))
	    # logger.info('ok...going in CPM_DetailSearchForm')
            form = CPM_DetailSearchForm(paper=pids, student=stuids)
	    # logger.info('ok...safety landed CPM_DetailSearchForm')
            return render_to_response('mcq_report_studentanswer.html',
                                      {'form': form,
                                       'group': group,
                                       'pids': json.dumps(pids),
                                       'stuids': json.dumps(stuids),
                                       'student_id': stuids[0] if stuids else None,
                                       'paper_id': pids[0] if pids else None,                                       
                                       },
                                      context_instance=RequestContext(request))
        else:
	    logger.info('enter zone 2')
            #get specified papers of students after select table step 2
            try:
                pids = [int(id) for id in request.POST.get('pids').strip('[]').split(',')]
                stuids = [int(id) for id in request.POST.get('stuids').strip('[]').split(',')]
                form = CPM_DetailSearchForm(request.POST, paper=pids, student=stuids)
            except Exception as e:
                logger.error(e)
            if form and form.is_valid():
                student = form.cleaned_data['student']
                paper = form.cleaned_data['paper']
            else:
                if not stuids or not pids:
                    return HttpResponse("students or papers do not exist")
                # logger.info("stuids[0]:%s,pids[0]:%s ok!" % (stuids[0], pids[0]))
                try:
                    student = SProfile.objects.get(user__id=stuids[0])
                    paper = MCQ_Paper.objects.get(id=pids[0])
                except Exception as e:
                    logger.error(e)
                    student = None
                    paper = None
	    logger.info('enter zone 3')
            return render_to_response('mcq_report_studentanswer.html',
                                      {'form': form, 'student': student,
                                       'group': group, 'paper': paper,
                                       'pids': json.dumps(pids),
                                       'stuids': json.dumps(stuids),
                                       'student_id': student.user.id,
                                       'paper_id': paper.id,   
                                       },
                                      context_instance=RequestContext(request))
    else:
        #get pape:show all the report tables
	logger.info('enter zone 4')
        return render_to_response('mcq_report_studentanswer.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))


@login_required
def cpm_report_student(request):
	group = getGroupNameByRequest(request)
	if group != 'students':
		logger.info('redirect to mcq_student_index')
		return redirect('cpm_student_index')
	form = CPM_PaperSearchForm()
	logger.info('use mcq_report_paper.html')
	return render_to_response('cpm_report_paper.html',
		              {'form': form},
		              context_instance=RequestContext(request))

def getTakedStuanswers(questionset, student,paper,isRetakes):
	try:
		stuanswer_set = list(CPM_StudentAnswer.objects.filter(question=question,sta_paper=paper,
		                                  student=student, sta_taked=True).latest('sta_timestamp') for question in questionset)
		
	except Exception as e:
		#logger.info('error: %s' % e)
		stuanswer_set = []

		
		
	return stuanswer_set


def __studentmarkreport(student):
	takedpaperlist = []
	try:
		lst_assignments = CPM_Assignment.objects.filter(asm_students=student)
		lst_papers = CPM_Paper.objects.filter(assignment__in=lst_assignments).distinct()
		logger.info( ' check all lst_papers %s ' % lst_papers)
	except Exception as E:
		logger.info(' exception studentmarkreport %s ' % E)
		lst_papers = []

	for p in lst_papers:
		question_set = CPM_Question.objects.filter(paper=p)
		stuanswer_set = getTakedStuanswers(question_set, student,p,False)
		if stuanswer_set:
			mark = sum(ans.sta_mark for ans in stuanswer_set)
			closeness = sum(ans.sta_closeness if ans.sta_closeness else 0.0 for ans in stuanswer_set)
			closeness /= float(len(stuanswer_set))
			takedpaperlist.append([p, student, mark, closeness])
	return takedpaperlist


@login_required
def mcq_paper_getall_closeness(request):
	try:
		logger.info('mcq_paper_getall_closeness')
		pids = request.POST.get('pids')
		response = render_to_response('mcq_paper_closeness.json', 
				  {'closeness_band_info': __teacher_closeness_info(pids)},
				  context_instance=RequestContext(request))
		response['Content-Type'] = 'text/plain; charset=utf-8'
		response['Cache-Control'] = 'no-cache'
		return response
	except Exception as  Err:
		logger.debug("Error: %s" % Err)

def __teachermarkreport(pids):
	"""
	teacher report post pids
	"""
	takedpaperlist = []
	try:
		paperids = [int(i) for i in pids.split(',')]
		papers = CPM_Paper.objects.filter(id__in=paperids)
	except Exception as e:
		logger.debug('__teachermarkreport : %s' % e)
		print(e)
		papers = []
	for p in papers:
		logger.info('paper %s ' % p)
		if p.assignment != None:
			#============= Alternate way to get p		
			lst_assignment = CPM_Assignment.objects.filter(id=p.assignment.id).values('asm_students')
			stuid = []
			for row_assign in lst_assignment :
				logger.info("row_assign %s " % row_assign["asm_students"])
				stuid.append(int(row_assign["asm_students"]))
			logger.info('stuids: %s ' % stuid)
			students = SProfile.objects.filter(user__id__in=stuid)
			logger.info('students %s ' % students)
			for student in students:
				logger.info('student %s ' % student)
				question_set = CPM_Question.objects.filter(paper=p)
				# Note: ignores earlier responses if question was retaken
				stuanswer_set = getTakedStuanswers(question_set, student,p,False)
				if stuanswer_set:
					mark = sum(ans.sta_mark for ans in stuanswer_set)
					# Return average of the question closeness scores
					closeness = sum(ans.sta_closeness if ans.sta_closeness else 0.0 for ans in stuanswer_set)
					closeness /= float(len(stuanswer_set))
					## OLD: takedpaperlist.append([p, student, mark])
					takedpaperlist.append([p, student, mark, closeness])
	return takedpaperlist




@login_required
def mcq_paper_getall(request):
	if request.method == 'POST':
		logger.info('mcq_paper_getall zone 1')
		pids = request.POST.get('pids')
		student, res = getSpByRequest(request, None)
		if pids and not student:
			logger.info('mcq_paper_getall 1')
			takedpaperlist = __teachermarkreport(pids)
		elif student:
			logger.info('mcq_paper_getall 2')
			takedpaperlist = __studentmarkreport(student)
		logger.info('use mcq_paper_mark.json')
		response = render_to_response('cpm_paper_mark.json', {'takedpaperlist': takedpaperlist},
			context_instance=RequestContext(request))
	else:
		logger.info('mcq_paper_getall zone 2')
		forwhat = request.GET.get('forwhat')
		if forwhat == 'teacher_report':
			"""
			teacher_report default datatable
			"""
			try:
				papers = CPM_Paper.objects.filter(owner=request.user)
			except:
				papers = []
			logger.info('use mcq_paper_report.json')
			response = render_to_response('cpm_paper_report.json',
				{'papers': papers},
				context_instance=RequestContext(request))
		else:
			"""
			teacher get all paper ztree
			"""
			try:
				papers = CPM_Paper.objects.filter(owner=request.user)
			except:
				papers = []
			logger.info('use mcq_paper_all.json')
			response = render_to_response('cpm_paper_all.json', {'papers': papers},
				context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response
	


#================================================================================
#                    Student View 
#================================================================================


@login_required
def cpm_student_index(request): 
	sp, res = getSpByRequest(request, 'login')
	if not sp and res:
		return res
	teacher = sp.teacher 
	curtime = datetime.now()
	warningtime = curtime + timedelta(days=1)
	## HACK: widen delta by 1 month
	curtime = datetime.now() - timedelta(days=30)
	warningtime = datetime.now() + timedelta(days=30)
	try: 
		assignments = CPM_Assignment.objects.filter(asm_students=sp) 
	except:
		pass
	else:
		deadlinewarning = "".join(str for str in _getdeadlinewarning(sp, assignments,False))
		if deadlinewarning:
			warninghead = "<h6 class='assignment-dueto-dialog'>Teacher %s:</h6> " % teacher.user.username
			msg = warninghead + deadlinewarning
			messages.add_message(request, messages.SUCCESS, msg)
	return render_to_response('cpm_student_index.html', context_instance=RequestContext(request))




@login_required
def cpm_student_getassignedassignments(request):
	# logger.debug("mcq_student_getassignedassignments(_)" % request)
	## print  >> sys.stderr, ("student_getassignedassignments(%s)" % request) # stderr HACK
	try:
		student, res = getSpByRequest(request, None)
		teacher = student.teacher
	except:
		student, res = None, None
	else:
		# logger.debug('teacher assignemnt: %s' % teacher.mcq_assignment_set)
		curtime = datetime.now()
		#        assignments = teacher.assignment_set.filter(deadline__gt=curtime,
		#                                                    students=student)
		## HACK: no date filter
		assignments = teacher.cpm_assignment_set.filter(asm_students=student)
		# logger.debug("Assignments = %s" % assignments)
		## HACK: use stderr
		## print  >> sys.stderr, ("Assignments = %s" % assignments)
		assignment_list = _getassignmentjson(assignments, teacher, student)
		response = render_to_response('mcq_student_allsignedassignments.json',
			{'assignment_list': assignment_list},
			context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response

def _getdeadlinewarning(student, assignments,isRetake):
	for assignment in assignments:
		papers = CPM_Paper.objects.filter(assignment=assignment)
		for paper in papers:
			questions = CPM_Question.objects.filter(paper=paper)
			stuanswers = getTakedStuanswers(questions, student,paper,isRetake)
			anscount = sum(1 for stuanswer in stuanswers)
			if anscount != paper.ppr_total:
				yield '<p class="assignment-dueto-dialog"> %s/%s will be due.</p>'\
					% (str(assignment.asm_assignmentname), str(paper.ppr_papername))

def getStuanswers(questionset, student,paper):
    try:
        stuanswer_set = list(CPM_StudentAnswer.objects.filter(Q(question=question),Q(sta_paper=paper),
                                                          Q(student=student)).latest('timestamp') for question in questionset)
    except:
        stuanswer_set = list(CPM_StudentAnswer.objects.filter(Q(question__in=questionset),Q(sta_paper=paper),
                                                          Q(student=student)))
    return stuanswer_set


def _getassignmentjson(assignments, teacher, student):
	assignment_list = []
	
	for a in assignments:
		answered_wrong_answer_count = 0
		papers = CPM_Paper.objects.filter(assignment=a, owner=teacher.user) 
		for p in papers:
			try:
				questionseq = pickle.loads(str(p.ppr_questionseq))
				question_set = CPM_Question.objects.filter(id__in=questionseq)
				stuanswer_set = getStuanswers(question_set, student,p)
				count = sum(1 for sa2 in stuanswer_set if sa2.sta_taked)
				count_isExist = sum(1 for sa1 in stuanswer_set if sa1.sta_taked == True or sa1.sta_taked == False)
				# If contain incorrect answer then allowed to redo, but only once. therefore, once this button 
				# is clicked. then this paper can not redo any more for this student.
				if count != 0:	
					answered_wrong_answer_count = sum(1 for sa in stuanswer_set if sa.optionlist != None if sa.optionlist.opl_iscorrect==False)
						
				# logger.info('after miao ... this is the number %s' % count)
				
			except Exception as e:
				logger.error(e)
				# logger.error(a)
				# logger.error(p)
				break
			# logger.info('miao finsihed for ppr_total: %s' % p.ppr_total)
			str_btn_retake = "<a href='/cpm/student/takeassignment/?paperid=%s'><font color=black>Take</font></a>&nbsp;|&nbsp;" % str(p.id)
			str_btn_take = ""
			 
			action = "%s <a href='/cpm/student/summarize/?paperid=%s'><font color=black>View</font></a>" % (str_btn_retake,str(p.id))
			
				
					
			
			assignment_list.append([a, count, p, action])
	# logger.info("assignment_list  .... %s" % assignment_list)
	return assignment_list


	

@login_required
def cpm_student_takeassignment(request):
	logger.info("i'm in takeassignment")
	student, res = getSpByRequest(request, None)
	paperid = request.GET.get("paperid")
	retake = request.GET.get("retake")
	try:
		paper = CPM_Paper.objects.get(id=paperid)
		questionseq = pickle.loads(str(paper.ppr_questionseq))
	except:
		paper = None
		questionseq = []
	if paper and questionseq:
		try:
			assignment = paper.assignment
		except:
			assignment = None
			logger.info("mcq_student_takeassignment no assignment")
			
		try:
			question_set = CPM_Question.objects.filter(id__in=questionseq)
			stuanswer_set = getStuanswers(question_set, student,paper)
			qnameseq = list(CPM_Question.objects.get(id=qid).qtn_name for qid in questionseq)
		except Exception as e:
			logger.error(e)
			stuanswer_set = []
			qnameseq = []
			#custom paper student can retake
		if retake:
			_reinitanswer(stuanswer_set,paper)
			stuanswer_set = []
		if stuanswer_set:
			# logger.info('stuanswer_set option 1')
			anscount = sum(1 for stuanswer in stuanswer_set if stuanswer.sta_taked)
			if anscount == paper.ppr_total and paper.ppr_papertype != 'Review':
				return redirect('student_index')
			else:
				# logger.debug(stuanswer_set)
				duration = stuanswer_set[0].sta_timeleft
				# logger.debug(duration)
			if duration != -1:
				__getInstallTimer(request, duration)
			else:
				duration = __initstuanswer(paper, question_set, student)
				__getInstallTimer(request, duration)
		else:
			# logger.info('stuanswer_set option 2')
			duration = __initstuanswer(paper, question_set, student)
			__getInstallTimer(request, duration)
		#if assignment:
			## HACK: disable the deadline check
			#            if assignment.deadline < datetime.now() + timedelta(seconds=duration):
			#                return HttpResponse("Test time %s is due, you haven\'t enough time: %s"
			#                                    % (assignment.deadline, timedelta(seconds=duration)))
			#pass
		#MCQ_StudentTakenTracking.objects.create(stt_student=student,stt_assignment=assignment,stt_paper=paper)
	else:
		assignment = None
		logger.info('paper not found')
		qnameseq = []
		# duration has to be defined
		messages.add_message(request, messages.INFO, 'Paper not found')
	return render_to_response('cpm_student_takeassignment.html',
		{'student': student,
		'qids': simplejson.dumps(questionseq),
		'qnames': simplejson.dumps(qnameseq),
		'paper': paper, 'assignment': assignment},
		context_instance=RequestContext(request))



def __getInstallTimer(request, duration):
	cur = datetime.now()
	# logger.debug(cur)
	startkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "start")
	totalkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "total")
	request.session[startkey] = cur
	request.session[totalkey] = duration
def _reinitanswer(stuanswer_set,paper):
	mark = 0
	for ans in stuanswer_set:
		mark += ans.sta_mark
		student = ans.student
		question = ans.question
		try:
			ans = CPM_StudentAnswer.objects.get_or_create(student=student, question=question,sta_paper=paper,
				              sta_taked=False)
		except Exception as e:
			logger.error('ERRRO IN "reinitanswer" : %s' % e)
	return mark



def __initstuanswer(paper, question_set, student):
	[h, m] = paper.ppr_duration.split(':')
	duration = int(h) * 3600 + int(m) * 60
	for question in question_set:
		try:
			sa = CPM_StudentAnswer.objects.get_or_create(student=student,sta_paper=paper,
			question=question, sta_taked=True)
			sa[0].sta_timeleft = duration
			sa[0].save()
		except Exception as e:
			logger.error(e)
			pass
	return duration



@login_required
def cpm_stu_question_get(request):
	logger.info("mcq_stu_question_get")
	student, res = getSpByRequest(request, None)
	response_data = {'state': 'failure', 'clozepassage_content':''}
	str_optionlist = ""
	if request.method == 'POST':
		try:
			questionid = request.POST.get("questionid")
			paperid = request.POST.get("paperid")
			logger.info("xxxxx===========questionid:%s" % questionid)
			objQuestion = CPM_Question.objects.get(id=questionid)
			objPaper = CPM_Paper.objects.get(id=paperid)
			answer_set  = CPM_Answer.objects.filter(question=objQuestion)
			response_data['clozepassage_content']= objQuestion.qty_html
			for answer in answer_set:
				try:
					logger.info('objQuestion: %s' % objQuestion)
					logger.info('student: %s' % student)
					logger.info('objPaper: %s' % objPaper)
					logger.info('answer.ans_code: %s' % answer.ans_code)
				
					objStuAnswer = CPM_StudentAnswer.objects.get(
						question = objQuestion,
						student = student,
						sta_paper = objPaper,
						sta_questionseqcode = answer.ans_code
						)
				except Exception as e:
					logger.error("Error %s " % e)
					objStuAnswer = None
				strAnswer = ""
				logger.info('objStuAnswer: %s' % objStuAnswer)
				if objStuAnswer != None:
					strAnswer = objStuAnswer.sta_answer
				response_data['clozepassage_content'] =str.replace(response_data['clozepassage_content'], answer.ans_code ,'<input type="input" value="' + strAnswer + '"   style="width:100px;text-align:center;margin:5px;"  onblur="fillinblank(this,' + str(answer.id)  + ',' + questionid +  ',' + paperid + ');return false;" />')
			logger.info("objQuestion.qty_html %s" % response_data['clozepassage_content'])
			response_data['state']= 'success'
		except Exception as e:
			logger.error('error message : %s' % e)
		
	return HttpResponse(json.dumps(response_data), mimetype="application/json")




@login_required
def cpm_fillinanswer(request):
	student, res = getSpByRequest(request, None)
	questionseq = request.POST['questionseq']
	questionid = request.POST['questionid'] 
	paperid = request.POST['paperid']
	strAnswer = request.POST['answer']
	response_data = {'state': 'failure', 'returnvalue':''}
	try:
		logger.info("questionid %s" % questionid)
		logger.info("questionseq %s" % questionseq)
		objQuestion = CPM_Question.objects.get(id=questionid)
		objAnswer = CPM_Answer.objects.get(id=questionseq)  # to get the ans_code only, then, need to base on ans_code to get list of answer.		
		if objAnswer == None:
			return HttpResponse(json.dumps(response_data), mimetype="application/json")
		objPaper = CPM_Paper.objects.get(id=paperid)
		isCorrect = False
		decMark = 0
		tempMark = 0
		lst_answer = CPM_Answer.objects.filter(ans_code=objAnswer.ans_code)
		objStuAnswer = CPM_StudentAnswer.objects.get_or_create(
			question = objQuestion,
			student = student,
			sta_paper = objPaper,
			sta_questionseqcode = objAnswer.ans_code
			)
		for rowanswer in lst_answer:
			logger.info('testing')
			if rowanswer.ans_answer == strAnswer:
				isCorrect = True
				logger.info('answering found')
				decMark = rowanswer.ans_mark
		
				objStuAnswer[0].sta_mark = decMark
		if isCorrect == False:
			logger.info('answer not found %s' % tempMark)
			objStuAnswer[0].sta_mark = tempMark
		objStuAnswer[0].sta_taked = 1
		logger.info('strAnswer: %s' % strAnswer)
		objStuAnswer[0].sta_answer = strAnswer
		objStuAnswer[0].save()	
				
	 
			
				
			
	except Exception as e:
		logger.error('Error cpm_fillinanswer: %s' % e)
	return HttpResponse(json.dumps(response_data), mimetype="application/json")
 
@login_required
def cpm_report_studentanswer(request):
    form = []
    group = getGroupNameByRequest(request)
    #pids = [int(id) for id in request.POST.get('pids')]
    #stuids = [int(id) for id in request.POST.get('stuids')]
    #print pids, stuids
    
    if request.method == "POST":
        logger.debug("request.POST: %s" % request.POST)
        #get table list of all found papers after select table step 1
        paperids = request.POST.get('paperids')
        print(paperids,"paperids paperids")
        pids = []
        stuids = []
        if paperids:
	    logger.info('enter zone 1')
            try:
		logger.info('this is all paperids: %s' % paperids)
                paper_stu = re.findall(r'\{pid\:(\d+)\,\sstuid\:(\d+)\}', paperids)
		logger.info('this is all paper_stu: %s' % paper_stu)
            except Exception as e:
                logger.error(e)
            for pid, stuid in paper_stu:
		logger.info('this is each id : %s ' % pid)
                pids.append(int(pid))
                stuids.append(int(stuid))
	    # logger.info('ok...going in CPM_DetailSearchForm')
            form = CPM_DetailSearchForm(paper=pids, student=stuids)
	    # logger.info('ok...safety landed CPM_DetailSearchForm')
            return render_to_response('cpm_report_studentanswer.html',
                                      {'form': form,
                                       'group': group,
                                       'pids': json.dumps(pids),
                                       'stuids': json.dumps(stuids),
                                       'student_id': stuids[0] if stuids else None,
                                       'paper_id': pids[0] if pids else None,                                       
                                       },
                                      context_instance=RequestContext(request))
        else:
	    logger.info('enter zone 2')
            #get specified papers of students after select table step 2
            try:
                pids = [int(id) for id in request.POST.get('pids').strip('[]').split(',')]
                stuids = [int(id) for id in request.POST.get('stuids').strip('[]').split(',')]
                form = CPM_DetailSearchForm(request.POST, paper=pids, student=stuids)
            except Exception as e:
                logger.error(e)
            if form and form.is_valid():
                student = form.cleaned_data['student']
                paper = form.cleaned_data['paper']
            else:
                if not stuids or not pids:
                    return HttpResponse("students or papers do not exist")
                # logger.info("stuids[0]:%s,pids[0]:%s ok!" % (stuids[0], pids[0]))
                try:
                    student = SProfile.objects.get(user__id=stuids[0])
                    paper = CPM_Paper.objects.get(id=pids[0])
                except Exception as e:
                    logger.error(e)
                    student = None
                    paper = None
	    logger.info('enter zone 3')
            return render_to_response('cpm_report_studentanswer.html',
                                      {'form': form, 'student': student,
                                       'group': group, 'paper': paper,
                                       'pids': json.dumps(pids),
                                       'stuids': json.dumps(stuids),
                                       'student_id': student.user.id,
                                       'paper_id': paper.id,   
                                       },
                                      context_instance=RequestContext(request))
    else:
        #get pape:show all the report tables
	logger.info('enter zone 4')
        return render_to_response('cpm_report_studentanswer.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))





@login_required
def cpm_question_getid(request):
	logger.info('mcq_question_getid')
	response_data = {'state': 'failure'}
	if request.method == 'POST':
		paperid = request.POST.get("paperid")
	if paperid:
		try:
			paper = CPM_Paper.objects.get(id=paperid)
			qids = pickle.loads(str(paper.ppr_questionseq))
			qnames = list(CPM_Question.objects.get(id=qid).qtn_name for qid in qids)
		except Exception as e:
			logger.error(e)
		else:
			response_data['qids'] = qids
			response_data['qnames'] = qnames
			response_data['state'] = 'success'
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required
def cpm_question_getstureport(request):
	logger.debug("in question_getstureport")
	student, res = getSpByRequest(request, None)
	# note: Used for student report (see report_studentanswer.html and report_reviewquestion.js)
	response_data = {'state': 'failure'}
	stuid = request.POST.get('studentid')
	qid = request.POST.get('questionid')
	pid = request.POST.get('paperid')
	isRetake = request.POST.get('isRetake')
	b_student_has_answer = False

	response_data['optionid_stdanswer'] = 0
	response_data['optionid_stuanswer'] = 0
	stuanswer = None
	strStudentMark = 0
	try:
		question = CPM_Question.objects.get(id=qid)
		paper = CPM_Paper.objects.get(id=int(pid))
			
		#TODO: need to add each question answer and student answer. 
		answer_set  = CPM_Answer.objects.filter(question=question)
		response_data['clozepassage_content']= question.qty_html
		strIncorrectStyle=' style="width:100px;text-align:center;margin:5px;font-weight:bold;color:red; text-decoration:line-through;"'
		strCorrectStyle=' style="width:100px;text-align:center;margin:5px;font-weight:bold;color:blue;"'
		for answer in answer_set:
			strStudentAnswer = ""
			strAnswerColor="red"
			#============= here is to find the answer again to get the answer code ===============
			strLstAnswer = ""
			lst_recheck_answerlist = CPM_Answer.objects.filter(Q(question=question),Q(ans_code=answer.ans_code))
			for recheck in lst_recheck_answerlist:
				if strLstAnswer == "":
					strLstAnswer = recheck.ans_answer
				else:
					strLstAnswer = strLstAnswer + "&nbsp;&nbsp;/&nbsp;&nbsp;" + recheck.ans_answer
					
			strAnswer= '<span style="font-weight:bold;color:blue;font-style: italic;text-decoration: underline;">Correct Answer: ' + strLstAnswer + "</span>"
			
		
			try:
				objStudentAnswer = CPM_StudentAnswer.objects.get(student=student
					, sta_questionseqcode=answer.ans_code
					, question = question
					, sta_paper = paper)
				strStudentMark += objStudentAnswer.sta_mark
				strStudentAnswer = objStudentAnswer.sta_answer
			
				if objStudentAnswer.sta_mark > 0: 
					strStudentTmp = '<input disabled="true" type="input" ' + strCorrectStyle+ ' value="' + objStudentAnswer.sta_answer + '" />' 
				else:
					strStudentTmp = '<input  disabled="true" type="input" ' + strIncorrectStyle  + ' value="' + objStudentAnswer.sta_answer +'" />' + "[&nbsp;&nbsp;" + strAnswer + "&nbsp;&nbsp;]"
			except:
				objStudentAnswer= None
				strStudentTmp = '<input  disabled="true" type="input" style="font-weight:bold;color:red;" value="N/A" />' + "[&nbsp;&nbsp;" + strAnswer + "&nbsp;&nbsp;]"
			
			response_data['clozepassage_content'] =str.replace(response_data['clozepassage_content'], answer.ans_code ,strStudentTmp )
		response_data['pointmarklist'] = [] 
		response_data['omitted'] = ''
		response_data['state'] = 'success' 
		response_data['mark'] = strStudentMark		
	except Exception as e:
		logger.error('Error: %s' % e)
	return HttpResponse(json.dumps(response_data), mimetype="application/json")



@login_required
def cpm_feedback_popup(request, pid, stuid):
	group = getGroupNameByRequest(request)
	qid = request.GET.get("question_id")
	tempRow = None
	if group != 'students':
		logger.info("mcq_feedback_popup: if statement start") 
		paper = CPM_Paper.objects.get(id = pid)
		s_profile = SProfile.objects.get(user=stuid)
		fb = CPM_StudentAnswer.objects.filter( question = qid, student = s_profile, sta_paper = paper )
		logger.info("mcq_feedback_popup: if statement done") 
		for row in fb:  
			tempRow = row
			logger.info( "post method calling %s " % row.sta_timestamp )
		if request.method == 'POST':
			logger.info( "post method calling")
			form = CPM_FeedbackForm(request.POST)
			
			if form.is_valid():
				fback = request.POST['Add_Feedback']
				fb_code = request.POST['Add_Feedback_Code']
				for row in fb:  
					tempRow = row
					logger.info('tempRow:' , tempRow)
					row.sta_feedback = fback
					row.sta_feedback_code = fb_code
					row.save()
				return HttpResponse(json.dumps({
						"success": True
						})
					)
			else:
				return HttpResponse(json.dumps({
						"success": False,
						"errors": form.errors
					})
				)        
		logger.info("mcq_feedback_popup: get form feedback start ") 
		form = CPM_FeedbackForm()           
		logger.info("mcq_feedback_popup: get form feedback end") 
		return render_to_response('cpm_fb_popup.html',
				{'form':form, 'pid':pid, 'stuid': stuid,'fb':tempRow, 'qid':qid },
				context_instance=RequestContext(request)
			)

	else:
		logger.info("mcq_feedback_popup: else statement") 
		"""
		The else part is user for show the student report and able to print
		that report """
		qset = []
		student = request.user
		paper = CPM_Paper.objects.get(id = pid)
		strAnswer_HTML = ""
		strAnswer_FinalHTML = ""
		total_mark = 0
		stud_mark = 0
		questionseq = pickle.loads(str(paper.ppr_questionseq)) #question sequence are added into this part
		
		total_mark = 0
		stud_mark = 0
		strStudentMark = 0


		try:
			for q in questionseq:
				logger.info('Q is it: %s' % q)
				question = CPM_Question.objects.get(id = q)
				#TODO: need to add each question answer and student answer. 
				answer_set  = CPM_Answer.objects.filter(Q(question=question) )
				strAnswer_HTML = question.qty_html
				strIncorrectStyle=' style="width:100px;text-align:center;margin:5px;font-weight:bold;color:red; text-decoration:line-through;"'
				strCorrectStyle=' style="width:100px;text-align:center;margin:5px;font-weight:bold;color:blue;"'
				
				for answer in answer_set:
					total_mark = total_mark + answer.ans_mark
					#============= here is to find the answer again to get the answer code ===============
					strLstAnswer = ""
					lst_recheck_answerlist = CPM_Answer.objects.filter(Q(question=question),Q(ans_code=answer.ans_code))
					for recheck in lst_recheck_answerlist:
						if strLstAnswer == "":
							strLstAnswer = recheck.ans_answer
						else:
							strLstAnswer = strLstAnswer + "&nbsp;&nbsp;/&nbsp;&nbsp;" + recheck.ans_answer
							
					
					strStudentAnswer = ""
					strAnswerColor="red"
					strAnswer= '<span style="font-weight:bold;color:blue;font-style: italic;text-decoration: underline;">correct answer: ' + strLstAnswer + "</span>"
					
		
					try:
						logger.info( 'student: %s , code: %s  question : %s , paper : %s' % (student,answer.ans_code,question,paper))
						objStudentAnswer = CPM_StudentAnswer.objects.get(student=student
							, sta_questionseqcode=answer.ans_code
							, question = question
							, sta_paper = paper)
						logger.info('get objStudentAnswer  liao : %s' % objStudentAnswer )
						strStudentMark += objStudentAnswer.sta_mark
						strStudentAnswer = objStudentAnswer.sta_answer
			
						if objStudentAnswer.sta_mark > 0: 
							strStudentTmp = '<input disabled="true" type="input" ' + strCorrectStyle+ ' value="' + objStudentAnswer.sta_answer + '" />' 
							stud_mark = stud_mark + objStudentAnswer.sta_mark
						else:
							strStudentTmp = '<input  disabled="true" type="input" ' + strIncorrectStyle  + ' value="' + objStudentAnswer.sta_answer +'" />' + "[&nbsp;&nbsp;" + strAnswer + "&nbsp;&nbsp;]"
					except Exception as e:
						logger.info('ops..error %s' % e)
						objStudentAnswer= None
						strStudentTmp = '<input  disabled="true" type="input" style="font-weight:bold;color:red;" value="N/A" />' + "[&nbsp;&nbsp;" + strAnswer + "&nbsp;&nbsp;]"
			
					strAnswer_HTML =str.replace(strAnswer_HTML, answer.ans_code ,strStudentTmp )
				strAnswer_FinalHTML = strAnswer_FinalHTML + "<br/>" + strAnswer_HTML
				
		except Exception as e:
			logger.error('Error: %s' % e) 
		logger.info('strAnswer_HTML: %s' % strAnswer_FinalHTML)
		return render_to_response('cpm_report_feedback_report.html',
				{ 'answer_html': strAnswer_FinalHTML,  'user':student,'paper':paper, 
				'sum':total_mark,'smark':stud_mark,
				'print': True if request.is_ajax() else False,'len':0,
			})
































































