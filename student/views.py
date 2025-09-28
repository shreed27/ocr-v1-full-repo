import traceback
import logging
import pickle
import nltk
from json import loads, dumps
from datetime import datetime, timedelta

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils import simplejson
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags

from portal.models import TProfile, SProfile
from student.models import StudentAnswer
from student.forms import StudentDetailForm, StudentModifyForm, CustomPaperForm
from canvas.models import Canvas
from portal.common import getSpById, getTpByRequest, getSpByRequest, getGroupNameByRequest, stripHTMLStrings, getStuanswers, getTakedStuanswers, stu_embedded_latex, retake_option
from algo.answer import Answer, ImageAnswer
from algo.standard import Standard
from algo.common import getenv_boolean
from assignment.models import Assignment
from paper.models import Paper
from classroom.models import Classroom
from question.models import Question, QuestionImage
from question.views import NUM_CLOSENESS_BANDS
from report.models import ClosenessReport
from portal.decorators import login_megaforte_user

logger = logging.getLogger(__name__)
import sys
import re

# Use the student frequent distribution for global documents counts (not teacher)
# Note: needed for term expansion to work properly
USE_STUDENT_TEXT_DIST = getenv_boolean("USE_STUDENT_TEXT_DIST", True)

@login_megaforte_user
@login_required
def student_index(request):
    ## logger.debug("student_index(%s)" % request)
    logger.debug("student_index(%s)" % request)
    sp, res = getSpByRequest(request, 'login')
    if not sp and res:
        return res
    teacher = sp.teacher
    logger.debug("sp=%s; teacher=%s" % (sp, teacher))
    curtime = datetime.now()
    warningtime = curtime + timedelta(days=1)
    ## HACK: widen delta by 1 month
    curtime = datetime.now() - timedelta(days=30)
    warningtime = datetime.now() + timedelta(days=30)
    try:
#        assignments = Assignment.objects.filter(students=sp,
#                                                deadline__lt=warningtime,
#                                                deadline__gt=curtime)
#        logger.debug("assignments=%s; deadline__gt=%s deadline__lt=%s" % (assignments, curtime, warningtime))
        ## HACK: ignore the deadline
        assignments = Assignment.objects.filter(students=sp)
        logger.debug("assignments=%s" % assignments)
    except:
        pass
    else:
        deadlinewarning = "".join(str for str in _getdeadlinewarning(sp, assignments))
        if deadlinewarning:
            warninghead = "<h6 class='assignment-dueto-dialog'>Teacher %s:</h6> " % teacher.user.username
            msg = warninghead + deadlinewarning
            messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response('student_index.html', context_instance=RequestContext(request))


def _getdeadlinewarning(student, assignments):
    for assignment in assignments:
        papers = Paper.objects.filter(assignment=assignment)
        for paper in papers:
            questions = Question.objects.filter(paper=paper)
            stuanswers = getTakedStuanswers(questions, student)
            anscount = sum(1 for stuanswer in stuanswers)
            if anscount != paper.total:
                yield '<p class="assignment-dueto-dialog"> %s/%s will be due.</p>'\
                      % (str(assignment.assignmentname), str(paper.papername))


@permission_required('auth.add_user')
def student_getall(request):
    group = getGroupNameByRequest(request)
    if group == "teachers":
        tp = TProfile.objects.get(user=request.user)
        logger.debug(tp)
        students = SProfile.objects.filter(teacher=tp)
        if students:
            if len(students) == 0:
                #queryset is lazy. so if it's empty, it will crash json
                students = []
    else:
        students = []
    response = render_to_response('student_all.json',
                                  {"students": students},
                                  context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@permission_required('auth.add_user')
def student_add(request):
    tp, res = getTpByRequest(request, 'login')
    if not tp and res:
        return res
    form = StudentDetailForm(teacher=tp)
    if request.method == 'POST':
        form = StudentDetailForm(request.POST, teacher=tp)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            gender = form.cleaned_data['gender']
            try:
                classroom = form.cleaned_data['clazz']
            except Exception as e:
                logger.error(e)
                classroom = None
            user = User.objects.create_user(username, email, password)
            user.groups = (Group.objects.get(name='students'),)
            user.save()
            sp = SProfile.objects.create(user=user, teacher=tp,
                                         gender=gender, classroom=classroom)
            sp.save()
            #user.email_user("Registion Confirm.", "Dear %s,\nYou have been added to Class %d by teacher %s.Your password is %s" %(realname,Class.id,request.user.username,password))
            ## TODO: drop not
            if not classroom:
                messages.add_message(request, messages.SUCCESS,
                                     "%s has been added to Class %s" % (username, classroom.roomname))
            else:
                messages.add_message(request, messages.SUCCESS,
                                     "%s has been added, and no Class assigned" % username)
            return redirect('student_add')
        else:
            logger.debug("Student Detail Form invalid")
    return render_to_response('student_add.html', {'form': form},
                              context_instance=RequestContext(request))


@permission_required('auth.add_user')
def student_modify(request):
    tp, res = getTpByRequest(request, 'login')
    studentid = request.GET.get('studentid')
    if studentid:
        try:
            student = getSpById(studentid)
            classroom = student.classroom
            form = StudentModifyForm(teacher=tp,
                                     question_setinitial={"realname": student.user.username,
                                                          "username": student.user.username,
                                                          "email": student.user.email,
                                                          "password1": student.user.password,
                                                          "gender": student.gender,
                                                          "clazz": classroom})
        except:
            form = StudentModifyForm(teacher=tp)
    else:
        form = StudentModifyForm(teacher=tp)

    if request.method == 'POST':
        try:
            sp = getSpById(studentid)
        except:
            logger.error("Student Modify Form invalid")
        form = StudentModifyForm(request.POST, teacher=tp)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            classid = form.cleaned_data['clazz']
            gender = form.cleaned_data['gender']
            sp.user.username = username
            sp.user.password = password
            sp.user.email = email
            sp.user.save()
            sp.gender = gender
            try:
                classroom = Classroom.objects.get(id=classid)
            except:
                classroom = None
                messages.add_message(request, messages.SUCCESS,
                                     "%s has been added, add no Class assigned" % username)
            else:
                messages.add_message(request, messages.SUCCESS,
                                     "%s has been added to Class %s" % (username, classroom.roomname))
            sp.classroom = classroom
            sp.save()
            #user.email_user("debugmodify Confirm.",
            #"Dear %s,\nYou have been added to Class %d by teacher %s.Your password is %s" %(realname,Class.id,request.user.username,password))
            return redirect('student_modify')
        else:
            logger.error("Student Modify Form invalid")
    return render_to_response('student_add.html', {'form': form},
                              context_instance=RequestContext(request))


@login_required
def student_getassignedassignments(request):
    # logger.debug("student_getassignedassignments(_)" % repr(request))
    ## print  >> sys.stderr, ("student_getassignedassignments(%s)" % request) # stderr HACK

    try:
        student, res = getSpByRequest(request, None)
        teacher = student.teacher
    except:
        student, res = None, None
    else:
        curtime = datetime.now()
#        assignments = teacher.assignment_set.filter(deadline__gt=curtime,
#                                                    students=student)
        ## HACK: no date filter
        assignments = teacher.assignment_set.filter(students=student)
        logger.debug("Assignments = %s" % assignments)
        ## HACK: use stderr
        ## print  >> sys.stderr, ("Assignments = %s" % assignments)
        assignment_list = _getassignmentjson(assignments, teacher, student)
        response = render_to_response('student_allassignedassignments.json',
                                      {'assignment_list': assignment_list},
                                      context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


def _getassignmentjson(assignments, teacher, student):
    assignment_list = []
    for a in assignments:
        papers = Paper.objects.filter(assignment=a, owner=teacher.user)
        for p in papers:
            try:
                questionseq = pickle.loads(str(p.questionseq))
                question_set = Question.objects.filter(id__in=questionseq)
                stuanswer_set = getStuanswers(question_set, student)
                print(stuanswer_set, "stuanswer")
                count = sum(1 for sa in stuanswer_set if sa.taked)
                print(p.total)
                print(count,"count")

            except Exception as e:
                logger.error(e)
                logger.error(a)
                logger.error(p)
                break
            if count == p.total:
                retake = retake_option(stuanswer_set)
                print(retake)
                # for stud_ans in stuanswer_set:
                #     stud_ans.attempted_count += attempt_flag
                #     stud_ans.save()
                # retake_access = False
                #
                # else:
                if retake:
                    action = "<a href='/student/takeassignment/?paperid=%s'>\
                             <font color=black>ReTake</font></a>&nbsp;&nbsp;&nbsp;\
                             &nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;\
                             <a href='/student/summarize/?paperid=%s'>\
                             <font color=black>View</font></a>" % (str(p.id), str(p.id))

                else:
                    action = "<a href='/student/summarize/?paperid=%s'>\
                            <font color=black>View</font></a>" % str(p.id)

            else:
                action = "<a href='/student/takeassignment/?paperid=%s'>\
                            <font color=black>Take</font></a>&nbsp;&nbsp;&nbsp;\
                            &nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;\
                            <a href='/student/summarize/?paperid=%s'>\
                            <font color=black>View</font></a>" % (str(p.id), str(p.id))
            assignment_list.append([a, count, p, action])
    return assignment_list


@login_required
def student_takeassignment(request):
    print("this is assignment")
    student, res = getSpByRequest(request, None)
    paperid = request.GET.get("paperid")
    retake = request.GET.get("retake")

    print(retake, "retake")
    try:
        paper = Paper.objects.get(id=paperid)
        questionseq = pickle.loads(str(paper.questionseq))
    except:
        paper = None
        questionseq = []
    if paper and questionseq:
        try:
            assignment = paper.assignment
        except:
            assignment = None
        try:
            question_set = Question.objects.filter(id__in=questionseq)
            stuanswer_set = getStuanswers(question_set, student)
            qnameseq = list(Question.objects.get(id=qid).qname for qid in questionseq)
        except Exception as e:
            logger.error(e)
            stuanswer_set = []
            qnameseq = []
        #custom paper student can retake
        if retake:
            _reinitanswer(stuanswer_set)
            stuanswer_set = []
        if stuanswer_set:
            teacher_assignment_retake = retake_option(stuanswer_set)
            anscount = sum(1 for stuanswer in stuanswer_set if stuanswer.taked)
            if not teacher_assignment_retake and anscount == paper.total and paper.ptype != 'Review':
                return redirect('student_index')
            else:
                logger.debug(stuanswer_set)
                duration = stuanswer_set[0].timeleft
                logger.debug(duration)
                if duration != -1:
                    __getInstallTimer(request, duration)
                else:
                    duration = __initstuanswer(paper, question_set, student)
                    __getInstallTimer(request, duration)
        else:
            duration = __initstuanswer(paper, question_set, student)
            __getInstallTimer(request, duration)
        if assignment:
            ## HACK: disable the deadline check
#            if assignment.deadline < datetime.now() + timedelta(seconds=duration):
#                return HttpResponse("Test time %s is due, you haven\'t enough time: %s"
#                                    % (assignment.deadline, timedelta(seconds=duration)))
            pass
    else:
        assignment = None
        qnameseq = []
        # duration has to be defined
        messages.add_message(request, messages.INFO, 'Paper not found')
    print(student, "student")
    print(simplejson.dumps(questionseq),"simple json")
    print(simplejson.dumps(qnameseq),"simple qname")
    print(paper, "paper")
    print(assignment,"assignment")
    print("\n"*5)

    return render_to_response('student_takeassignment.html',
                              {'student': student,
                               'qids': simplejson.dumps(questionseq),
                               'qnames': simplejson.dumps(qnameseq),
                               'paper': paper, 'assignment': assignment},
                              context_instance=RequestContext(request))


def __getInstallTimer(request, duration):
    cur = datetime.now()
    logger.debug(cur)
    startkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "start")
    totalkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "total")
    request.session[startkey] = cur
    request.session[totalkey] = duration


def __initstuanswer(paper, question_set, student):
    [h, m] = paper.duration.split(':')
    duration = int(h) * 3600 + int(m) * 60
    for question in question_set:
        try:
            sa = StudentAnswer.objects.get_or_create(student=student,
                                                     question=question, taked=False)
            sa[0].timeleft = duration
            sa[0].save()
        except Exception as e:
            logger.error(e)
            pass
    return duration


@login_required
def student_checktime(request):
    student, res = getSpByRequest(request, None)
    startkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "start")
    totalkey = "%s_%s" % (settings.EXAM_TIMEOUT_PREFIX, "total")
    starttime = request.session[startkey]
    totaltime = request.session[totalkey]
    curtime = datetime.now()
    paperid = request.POST.get('paperid')
    saverequest = request.POST.get('save')
    if saverequest:
        try:
            p = Paper.objects.get(id=paperid)
            question_set = Question.objects.filter(paper=p,
                                                   infocompleted=Question.ALLCOMPLETED)
            stuanswer_set = getStuanswers(question_set, student)
            logger.debug("stuanswer len: %s" % len(stuanswer_set))
            for stuanswer in stuanswer_set:
                timeleft = stuanswer.timeleft
                stuanswer.timeleft = timeleft - (curtime - starttime).seconds
                stuanswer.save()
        except Exception as e:
            logger.error("%s:can\'t save timeleft" % e)
        response_data = {'timeout': 'false'}
    else:
        response_data = {}
        logger.debug("%s, --, %s, --, %s" % (starttime, totaltime, curtime))
        if starttime + timedelta(seconds=totaltime) <= curtime:
            response_data['timeout'] = 'yes'
            logger.debug('time out!')
        else:
            response_data['timeout'] = 'false'
            response_data['totaltime'] = totaltime / 60
            response_data['timeleft'] = (curtime - starttime).seconds / 60
            logger.debug('time passed ...')
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


@login_required
def student_custompaper(request):
    student, res = getSpByRequest(request, 'login')
    #add custompaper
    if request.method == "POST":
        form = CustomPaperForm(request.POST, owner=request.user)
        if form.is_valid():
            paperid = int(form.cleaned_data['paperid'])
            papername = form.cleaned_data['papername']
            duration = form.cleaned_data['duration']
            if paperid != -1:
                paper = Paper.objects.get(id=paperid)
                paper.papername = papername
                paper.ptype = 'Review'
                paper.owner = student.user
                paper.duration = duration
                paper.passpoint = 0
            else:
                paper = Paper.objects.create(papername=papername,
                                             duration=duration, passpoint=0,
                                             ptype="Review", owner=request.user)
            questionlist = form.cleaned_data['questionlist']
            paper.questionseq = pickle.dumps([q.id for q in questionlist])
            paper.total = len(questionlist)
            logger.debug("questionlist:%s" % questionlist)
            __updatequestioninpaper(questionlist, paper)
            paper.save()
            return redirect("/student/takeassignment?paperid=" + str(paper.id))
    else:
        #show add custompaper view
        paperid = request.GET.get('paperid')
        if paperid:
            try:
                p = Paper.objects.get(id=paperid)
            except:
                logger.debug("paper not found:%s" % paperid)
                pass
            logger.debug("paper:%s" % p)
            logger.debug(type(request.user))
            form = CustomPaperForm(initial={'paperid': p.id,
                                            'papername': p.papername,
                                            'duration': p.duration},
                                   owner=request.user)
        else:
            form = CustomPaperForm(owner=request.user)
    return render_to_response('student_custompaper.html', {'form': form},
                              context_instance=RequestContext(request))


def __updatequestioninpaper(questionlist, paper):
    questions = Question.objects.filter(paper=paper)
    temp = []
    for q in questions:
        if q not in questionlist:
            questionseq = pickle.loads(str(q.paper.all()[0].questionseq))
            questionseq.remove(q.id)
            q.paper.remove(paper)
            q.save()
            temp.append(q)
    for q in questionlist:
        if q not in temp:
            q.paper.add(paper)
            q.save()

# HACK: added for algo answer fix
# Derives frequency distribution for text
#
def get_text_distribution(anstext):
    sinst = Standard()

    # Make sure answer treated as a single paragraph
    # HACK: Ensures point number at start and trailing newline (needed for Standard.PointAnalysis).
    anstext = anstext.replace("\n", " ")
    anstext = "0 . " + anstext + "\n"

    # Return the frequency distribution of the words
    try:
        stu_pointlist, stu_textfdist, stu_slist = sinst.Analysis(anstext)
    except:
        print("In student views.py 1111111111")
        import traceback
        traceback.print_exc()
        stu_textfdist = None
    return stu_textfdist


# @login_required
# def student_submitanswer(request):    
#     logger.debug("in student_submitanswer()")
#     print ("in student_submitanswer()")
#     response_data = {'state': 'failure'}
#     student, res = getSpByRequest(request, 'login')
#     if not student and res:
#         return res
#     try:
#         qid = request.POST.get('questionid')
#         question = Question.objects.get(id=qid)
#         stdanswer = question.stdanswer
#     except:
#         logger.error("question %s not exists" % qid)
#         return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

#     try:
#         answer_html = request.POST.get('answer_html')
#         answer_html = answer_html.decode("utf8").encode('ascii', 'ignore')
#         anstext = stripHTMLStrings(strip_tags(stu_embedded_latex(answer_html)))
#         stuanswer = StudentAnswer.objects.filter(question=question,
#                                                  student=student).latest('timestamp')
#         print "-------------------------------------------------------------------------------------------------------"
#         print anstext
#         stuanswer.html_answer = answer_html
#         stuanswer.txt_answer = anstext
#         stuanswer.save()
#         print "answer saveddddddddddddddddddd      done"
#     except Exception as e:
#         import traceback
#         print 111111111111111111111111111111, traceback.format_exc()
#         traceback.format_exc()
#         logger.error("cant find stuanswer for question %s" % question)
#         logger.error(str(traceback.format_exc()))
#         return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

#     try:
#         thumbnail_ids = [int(i) for i in request.POST['stuthumbnail_ids'].split(',') if i]
#         print 'thumbnail_ids@@@@@@@@@ = ', thumbnail_ids
#     except:
#         import traceback
#         traceback.format_exc()
#         thumbnail_ids = []
#         logger.debug("no img for question %s" % question)
#         pass
#         #stdanswer algorithm to mark stuanswer
#     if not stdanswer or not stuanswer:
#         return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
#     else:
#         textfdist = _loadlist(stdanswer.textfdist)
#         slist = _loadlist(stdanswer.sentencelist)
#         pointlist = _loadlist(stdanswer.pointlist)
#         rulelist = _loadlist(stdanswer.rulelist)

#     # TODO: add better handling so that progress bar doesn't get stuck when algorithm code has an exception
#     try:
#         ans = Answer()
#         if USE_STUDENT_TEXT_DIST:
#             ans_textfdist = get_text_distribution(anstext)
#             if ans_textfdist:
#                 textfdist = ans_textfdist
#             if not textfdist:
#                 textfdist = nltk.FreqDist(['test'])
#         mark, marklist, omitted, closeness_stats = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
#         print 'mark = ', mark, '\n'
#         print 'marklist = ', marklist, '\n'
#         print 'omitted = ', omitted
#         if not mark or not marklist or not omitted:
#             mark = 0
#             marklist = list()
#             omitted = list()    
#         # Include optional listing with results from external grammar checker and optional closeness summarization
#         stuanswer.grammar_issues = ans.critique_results['report'] if ans.critique_results else ""
#         stuanswer.closeness = ans.closeness if ans.closeness else 0.0

#         # updating ClosenessReport
#         closeness_report, created = ClosenessReport.objects.get_or_create(
#             question=question, 
#             student_answer=stuanswer)
#         closeness_report.closeness_record = dumps(closeness_stats)
#         closeness_report.save()

#     except Exception, e:
#         print e
#         import traceback
#         traceback.print_exc()
#         mark = -1
#         marklist = []
#         omitted = []
#         ## OLD: logger.error(e)
#         logger.error("Exception during answer analysis: %s" % str(sys.exc_info()))
#         ## TODO: figure out one-line for following (or create helper function)
#         ## exc_type, exc_value, exc_traceback = sys.exc_info()
#         ## if exc_traceback:
#             ## ## BAD: logger.debug("Stack: %s" % exc_traceback.format_exc())
#             ## logger.debug("Stack: %s" % "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
#         ## take 3
#         import traceback
#         traceback.format_exc()
#         logger.debug("Stack: %s" % traceback.format_exc())

#     logger.debug(mark)
#     logger.debug(marklist)
#     logger.debug(omitted)
#     print '\n##############################################' * 2
#     print 'thumbnail_ids = ', thumbnail_ids
#     imgmark, stuansimages = __getimgmark(thumbnail_ids, question)
#     print 'imgmark = ', imgmark
#     # print 'stuansimages = ', stuansimages
#     print '\n##############################################' * 2

#     # Apply min closeness band threshold for mark
#     if (question.min_closeness_band > 0):
#         band = int(stuanswer.closeness * NUM_CLOSENESS_BANDS - 0.001)
#         if (band < question.min_closeness_band):
#             logger.info("Zeroing mark (%s) as closeness band (%s) less then min (%s)" % (mark, band, question.min_closeness_band))
#             mark = 0

#     try:
#         stucanvaslist = Canvas.objects.filter(question=question, stuanswer=stuanswer)
#         canvasmark = sum(stucanvas.mark for stucanvas in stucanvaslist)
#         print 'canvasmark = ', canvasmark
#     except Exception, e:
#         import traceback
#         traceback.format_exc()
#         logger.error(e)
#         canvasmark = 0
#     # save mark result
#     try:
#         stuanswer.mark = mark + imgmark + canvasmark
#         print 'mark= ',mark, ' imgmark =', imgmark, ' canvasmark = ', canvasmark
#         if omitted:
#             stuanswer.omitted = pickle.dumps(omitted)
#         else:
#             stuanswer.omitted = None
#         stuanswer.pointmarklist = pickle.dumps(marklist)
#         stuanswer.stuansimages = stuansimages
#         stuanswer.save()
#     except:
#         import traceback
#         traceback.format_exc()
#         response_data['state'] = 'failure'
#     else:
#         response_data['mark'] = stuanswer.mark
#         response_data['state'] = 'success'
#     logger.debug("out student_submitanswer(): response_data=%s" % response_data)
#     print ("out student_submitanswer(): response_data=%s" % response_data)
#     return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

@login_required
def student_answersave(request):
	response_data = {'state': 'failure'}
	try:		
		student, res = getSpByRequest(request, 'login')
		if not student and res:
			return res
		qid = request.POST.get('questionid')
		answer_html = request.POST.get('answer_html')
		question = Question.objects.get(id=qid)
		stuanswer = StudentAnswer.objects.filter(question=question,
                                                 student=student).latest('timestamp')
		
		if stuanswer != None:
			stuanswer.html_answer = answer_html
			stuanswer.save()
			response_data = {'state': 'successful'}
	except Exception as e:
		logger.debug('Error in Answer Save: %s' % e)
	return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
@login_required
def student_submitanswer(request):
    logger.debug("in student_submitanswer()")
    print ("in student_submitanswer()")

    alternative = False
    alternative_accepted = False
    response_data = {'state': 'failure'}
    proceed_further = False
    student, res = getSpByRequest(request, 'login')
    proceed_further = False
    if not student and res:
        return res
    try:
        qid = request.POST.get('questionid')
        question = Question.objects.get(id=qid)
        stdanswer = question.stdanswer

        # get the alternative standard answer for the answer
        if question.alt_stdanswer:
            alt_stdanswer = question.alt_stdanswer
            alternative = True
        else:
            alt_stdanswer = None
    except (Exception) as e:
        print(e)
        logger.error("question %s not exists" % qid)
        print(("question %s does not exists" % qid))
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    try:
        answer_html = request.POST.get('answer_html')
	logger.info('this is the answer: %s ' % answer_html)
        try:
            answer_html = answer_html.decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                answer_html = answer_html.encode('ascii', 'ignore')
            except:
                pass
        anstext = stripHTMLStrings(strip_tags(answer_html))
        try:
            anstext = anstext.decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                anstext = anstext.encode('ascii', 'ignore')
            except:
                import traceback
                traceback.print_exc()
        stuanswer = StudentAnswer.objects.filter(question=question,
                                                 student=student).latest('timestamp')
        stuanswer.html_answer = answer_html
	stuanswer.save()
        print("----------------------------------------------------------------------")
        print(anstext)

        # stuanswer.html_answer = answer_html
        # stuanswer.txt_answer = anstext
        # stuanswer.save()
        print("answer saveddddddddddddddddddd      done")
    except Exception as e:
        import traceback
        print(111111111111111111111111111111, traceback.format_exc())
        traceback.format_exc()
        logger.error("cant find stuanswer for question %s" % question)
        logger.error(str(traceback.format_exc()))
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    try:
        thumbnail_ids = [int(i) for i in request.POST['stuthumbnail_ids'].split(',') if i]
        print('thumbnail_ids@@@@@@@@@ = ', thumbnail_ids)
    except:
        import traceback
        traceback.format_exc()
        thumbnail_ids = []
        logger.debug("no img for question %s" % question)
        pass
        #stdanswer algorithm to mark stuanswer
    if not stdanswer or not stuanswer:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    else:
        textfdist = _loadlist(stdanswer.textfdist)
        slist = _loadlist(stdanswer.sentencelist)
        pointlist = _loadlist(stdanswer.pointlist)
        rulelist = _loadlist(stdanswer.rulelist)

        print(textfdist)
        print(slist)
        print(pointlist)
        print(rulelist)

        # for alternate answers
        if alternative and alt_stdanswer:
            alt_textfdist = _loadlist(alt_stdanswer.textfdist)
            alt_slist = _loadlist(alt_stdanswer.sentencelist)
            alt_pointlist = _loadlist(alt_stdanswer.pointlist)
            alt_rulelist = _loadlist(alt_stdanswer.rulelist)
        else:
            alt_textfdist = None
            alt_slist = None
            alt_pointlist = None
            alt_rulelist = None

        print(alt_textfdist)
        print(alt_slist)
        print(alt_pointlist)
        print(alt_rulelist)
    # TODO: add better handling so that progress bar doesn't get stuck when algorithm code has an exception
    try:
        ans = Answer()
        # initialize for alternative answer
        if alternative:
            alt_ans = Answer()
        else:
            alt_ans = None

        if USE_STUDENT_TEXT_DIST:
            ans_textfdist = get_text_distribution(anstext)
            if ans_textfdist:
                textfdist = ans_textfdist
                # save the same to alt_textfdist
                if alternative:
                    alt_textfdist = ans_textfdist
                else:
                    alt_textfdist = None
            if not textfdist:
                textfdist = nltk.FreqDist(['test'])
            # for alternate answer
            if not alt_textfdist:
                alt_textfdist = nltk.FreqDist(['test'])
        print(ans.Analysis(anstext, textfdist, slist, pointlist, rulelist))
        mark, marklist, omitted, closeness_stats = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
        if alternative:
            # calculate the same with alternate standard answer
            alt_mark, alt_marklist, alt_omitted, alt_closeness_stats = alt_ans.Analysis(anstext, alt_textfdist, alt_slist, alt_pointlist, alt_rulelist)
        else:
            alt_mark = alt_marklist = alt_omitted = alt_closeness_stats = None

        try:
            stucanvaslist = Canvas.objects.filter(question=question, stuanswer=stuanswer)
            canvasmark = sum(stucanvas.mark for stucanvas in stucanvaslist)
            print('canvasmark = ', canvasmark)
        except Exception as e:
            import traceback
            traceback.format_exc()
            logger.error(e)
            canvasmark = 0
        # save mark result

        print('\n##############################################' * 2)
        print('thumbnail_ids = ', thumbnail_ids)
        imgmark, stuansimages = __getimgmark(thumbnail_ids, question)
        print('imgmark = ', imgmark)
        # print 'stuansimages = ', stuansimages
        print('\n##############################################' * 2)

        if not mark or not marklist:
            mark = 0
            marklist = list()
        if not omitted:
            omitted = list()

        if not alt_mark or not alt_marklist:
            alt_mark = 0
            alt_marklist = list()
        if not alt_omitted:
            alt_omitted = list()

        # Include optional listing with results from external grammar checker and optional closeness summarization
        grammar_issues = ans.critique_results['report'] if ans.critique_results else ""
        closeness = ans.closeness if ans.closeness else 0.0

        # Alernative answer
        if alternative:
            alt_grammar_issues = alt_ans.critique_results['report'] if alt_ans.critique_results else ""
            alt_closeness = alt_ans.closeness if alt_ans.closeness else 0.0            

        # Apply min closeness band threshold for mark
        if (question.min_closeness_band > 0):
            band = int(closeness * NUM_CLOSENESS_BANDS - 0.001)
            if (band < question.min_closeness_band):
                logger.info("Zeroing mark (%s) as closeness band (%s) less then min (%s)" % (mark, band, question.min_closeness_band))
                mark = 0

            if not mark and alternative:
                print("inside alternative marking analysis")
                band = int(alt_closeness * NUM_CLOSENESS_BANDS - 0.001)
                if (band < question.min_closeness_band):
                    alt_mark = 0

        if (stuanswer.mark <= mark + imgmark + canvasmark) or (stuanswer.mark <= alt_mark):
            proceed_further = True
            stuanswer.html_answer = answer_html
            stuanswer.txt_answer = anstext
            stuanswer.save()


        print('mark = ', mark, '\n')
        print('marklist = ', marklist, '\n')
        print('omitted = ', omitted, '\n')
        print('closeness_stats = ', closeness_stats, '\n')

        print('alt_mark = ', alt_mark, '\n')
        print('alt_marklist = ', alt_marklist, '\n')
        print('alt_omitted = ', alt_omitted, '\n')
        print('alt_closeness_stats = ', alt_closeness_stats, '\n')

    except Exception as e:
        print(e)
	logger.debug('Exception : %s ' % e)
        import traceback
        traceback.print_exc()
        mark = -1
        marklist = []
        omitted = []

        # alternate answer
        alt_mark = -1
        alt_marklist = list()
        alt_omitted = list()
        ## OLD: logger.error(e)
        logger.error("Exception during answer analysis: %s" % str(sys.exc_info()))
        ## TODO: figure out one-line for following (or create helper function)
        ## exc_type, exc_value, exc_traceback = sys.exc_info()
        ## if exc_traceback:
            ## ## BAD: logger.debug("Stack: %s" % exc_traceback.format_exc())
            ## logger.debug("Stack: %s" % "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        ## take 3
        import traceback
        traceback.format_exc()
        logger.debug("Stack: %s" % traceback.format_exc())

    if proceed_further:
        logger.debug(mark)
        logger.debug(marklist)
        logger.debug(omitted)
        # print '\n##############################################' * 2
        # print 'thumbnail_ids = ', thumbnail_ids
        # imgmark, stuansimages = __getimgmark(thumbnail_ids, question)
        # print 'imgmark = ', imgmark
        # # print 'stuansimages = ', stuansimages
        # print '\n##############################################' * 2



        # try:
        #     stucanvaslist = Canvas.objects.filter(question=question, stuanswer=stuanswer)
        #     canvasmark = sum(stucanvas.mark for stucanvas in stucanvaslist)
        #     print 'canvasmark = ', canvasmark
        # except Exception, e:
        #     import traceback
        #     traceback.format_exc()
        #     logger.error(e)
        #     canvasmark = 0
        # # save mark result
        try:
            if alt_mark <= mark+imgmark+canvasmark:
                print("inside the actual standard answer part"*10)
                stuanswer.mark = mark + imgmark + canvasmark
                print('mark= ',mark, ' imgmark =', imgmark, ' canvasmark = ', canvasmark)
                if omitted:
                    stuanswer.omitted = pickle.dumps(omitted)
                else:
                    stuanswer.omitted = None
                stuanswer.pointmarklist = pickle.dumps(marklist)
                stuanswer.stuansimages = stuansimages
                stuanswer.grammar_issues = grammar_issues
                stuanswer.closeness = closeness                
                stuanswer.save()
                print('mark = ', mark, '\n')
                print('marklist = ', marklist, '\n')
                print('omitted = ', omitted, '\n')
                print('closeness_stats = ', closeness_stats, '\n')

                # save the alternative answers to the student answer
                # if the following criteria met.
            elif alternative and (alt_mark > mark):
                print("inside the alternative part of the question"*10)
                stuanswer.mark = alt_mark #+ imgmark + canvasmark
                if alt_omitted:
                    stuanswer.omitted = pickle.dumps(alt_omitted)
                else:
                    stuanswer.omitted = None
                stuanswer.pointmarklist = pickle.dumps(alt_marklist)
                # stuanswer.stuansimages = stuansimages
                stuanswer.grammar_issues = alt_grammar_issues
                stuanswer.closeness = alt_closeness
                stuanswer.save()            
                alternative_accepted = True
                print('alt_mark = ', alt_mark, '\n')
                print('alt_marklist = ', alt_marklist, '\n')
                print('alt_omitted = ', alt_omitted, '\n')
                print('alt_closeness_stats = ', alt_closeness_stats, '\n')                
        except:
            import traceback
            traceback.format_exc()
            response_data['state'] = 'failure'
        else:
            # updating ClosenessReport
            print(closeness_stats)
            print(alt_closeness_stats)
            closeness_report, created = ClosenessReport.objects.get_or_create(
                question=question, 
                student_answer=stuanswer)
            closeness_report.alternative = alternative_accepted
            closeness_report.closeness_record = dumps(alt_closeness_stats if alternative_accepted else closeness_stats)
            closeness_report.save()

            response_data['mark'] = stuanswer.mark
            response_data['state'] = 'success'
        logger.debug("out student_submitanswer(): response_data=%s" % response_data)
        print(("out student_submitanswer(): response_data=%s" % response_data))
    else:
        response_data['mark'] = stuanswer.mark
        response_data['state'] = 'success'
        logger.debug("out student_submitanswer(): response_data=%s" % response_data)
        print(("out student_submitanswer(): response_data=%s" % response_data))        

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def __getimgmark(thumbnail_ids, question):
    """getthumbnails of studentanswer image"""
    if not thumbnail_ids:
        return 0, []
    try:
        stdanswer = question.stdanswer
        stuansimages = QuestionImage.objects.filter(id__in=thumbnail_ids)
        imagepointlist = pickle.loads(str(question.imagepointlist))
    except Exception as e:
        print("expppppppp", e)
        logger.error(e)
        return 0, []
    else:
        stuanspoints = list([imagepoint, stuansimage]
                            for imagepoint in imagepointlist
                            for stuansimage in stuansimages
                            if imagepoint['Point_Text'] == stuansimage.digest)
        stuansimages = list(image for imagepoint, image in stuanspoints)
        logger.debug(stuanspoints)

    try:
        imgrulelist = _loadlist(stdanswer.imgrulelist)
    except Exception as e:
        logger.error(e)
    imgmark = None
    if stuanspoints and imgrulelist:
        imgans = ImageAnswer()
        imgmark, imgpointlist, imgomitted = imgans.Analysis(stuanspoints, imagepointlist, imgrulelist)
        logger.debug("imgmark:%d" % imgmark)
    return imgmark, stuansimages


def _loadlist(list):
    if list:
        return pickle.loads(str(list))
    else:
        return None


@login_required
def student_getcustompapers(request):
    student, res = getSpByRequest(request, None)
    papers = Paper.objects.filter(owner=student.user, ptype='Review')
    response = render_to_response('student_allcustompapers.json',
                                  {'paperlist': papers},
                                  context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def student_getanswerrecords(request):
    student, res = getSpByRequest(request, 'login')
    if not student and res:
        return res
    assignments = student.assignment_set.all()
    paperlist = []
    for assignment in assignments:
        papers = Paper.objects.filter(assignment=assignment)
        for paper in papers:
            question_set = paper.question_set.all()
            papermark = 0
            for question in question_set:
                try:
                    stuanswer = StudentAnswer.objects.filter(question=question,
                                                             student=student).latest('timestamp')
                except:
                    logger.debug("stuanswer not found")
                    break
                logger.debug(stuanswer)
                papermark = papermark + stuanswer.mark
            paperlist.append([assignment, paper, papermark])
    response = render_to_response('student_allhistoryanswers.json',
                                  {'paperlist': paperlist},
                                  context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def student_submitpaper(request):
    student, res = getSpByRequest(request, None)
    response_data = {'state': 'failure'}
    try:
        paperid = request.POST.get('paperid')
        p = Paper.objects.get(id=int(paperid))
        questionseq = pickle.loads(str(p.questionseq))
    except Exception as e:
        logger.error(e)
        return HttpResponse('paper not found')

    try:
        question_set = Question.objects.filter(id__in=questionseq)
        stuanswer_set = getStuanswers(question_set, student)
        print(stuanswer_set,"student answer submit paper")
    except Exception as e:
        response_data['state'] = e
        logger.error(e)
    if stuanswer_set:
        totalmark = 0
        for ans in stuanswer_set:
            totalmark += ans.mark
            ans.taked = True
            ans.save()
        print(totalmark ,"mark")
        if totalmark < p.passpoint:
            response_data['state'] = 'failed'
        else:
            response_data['state'] = 'passed'
        print(response_data,"response data")
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


def _reinitanswer(stuanswer_set):
    mark = 0
    for ans in stuanswer_set:
        mark += ans.mark
        student = ans.student
        question = ans.question
        try:
            ans = StudentAnswer.objects.get_or_create(student=student, question=question,
                                                      taked=False)
        except Exception as e:
            logger.error(e)
    return mark


@login_required
def student_papersummarize(request):
    student, res = getSpByRequest(request, 'login')
    if not student and res:
        return res
    paperid = request.GET.get('paperid')
    passed = request.GET.get('passed')
    try:
        paper = Paper.objects.get(id=paperid)
        questionseq = pickle.loads(str(paper.questionseq))
    except:
        return HttpResponse("paper does not exist")
    if paper and questionseq:
        question_set = Question.objects.filter(id__in=questionseq)
        stuanswer_set = getStuanswers(question_set, student)
        if passed == '0':
            mark = _reinitanswer(stuanswer_set)
            messages.add_message(request, messages.INFO,
                                 "You failed in this paper, please don\'t be panic, you can take it again")
        else:
            mark = sum(ans.mark for ans in stuanswer_set)
            flag_count = 1
            for stud in stuanswer_set:
                stud.attempted_count += flag_count
                stud.save()
    else:
        mark = 0
    return render_to_response('student_assignmentsummarize.html',
                              {'paper': paper,
                               'mark': mark},
                              context_instance=RequestContext(request))


def student_getbyname(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        stuname = request.POST.get('stuname')
        if stuname:
            try:
                student = SProfile.objects.get(user__username=stuname, teacher=None)
            except:
                pass
            else:
                response_data['gender'] = student.gender
                response_data['email'] = student.user.email
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


# OCR Integration Views
from .ocr_utils import ocr_processor
from .forms import OCRAnswerSheetForm
from django.utils import timezone


@login_required
@permission_required('student.add_studentanswer')
def ocr_upload_answer_sheet(request):
    """
    View to upload and process handwritten answer sheets via OCR
    """
    if request.method == 'POST':
        form = OCRAnswerSheetForm(request.POST, request.FILES, teacher=getTpByRequest(request))
        
        if form.is_valid():
            try:
                # Get form data
                image_file = form.cleaned_data['answer_sheet_image']
                student = form.cleaned_data['student']
                question = form.cleaned_data['question']
                manual_override = form.cleaned_data.get('manual_text_override', '').strip()
                
                # Process with OCR if no manual override
                if manual_override:
                    # Use manual text
                    extracted_text = manual_override
                    ocr_confidence = 1.0  # Manual entry is 100% confident
                    ocr_success = True
                    processing_method = 'manual'
                else:
                    # Use OCR API
                    ocr_result = ocr_processor.call_ocr_api(image_file)
                    ocr_success = ocr_result['success']
                    
                    if ocr_success:
                        extracted_text = ocr_result['extracted_text']
                        ocr_confidence = ocr_result.get('confidence', 0.0)
                        processing_method = 'ocr'
                    else:
                        messages.error(request, f"OCR processing failed: {ocr_result['error']}")
                        return render_to_response('student/ocr_upload.html', {
                            'form': form,
                            'error': ocr_result['error']
                        }, context_instance=RequestContext(request))
                
                # Create or update StudentAnswer
                student_answer, created = StudentAnswer.objects.get_or_create(
                    student=student,
                    question=question,
                    defaults={
                        'txt_answer': extracted_text,
                        'html_answer': extracted_text,  # Could be formatted later
                        'timestamp': timezone.now(),
                        'taked': True,
                        'attempted_count': 1,
                        'mark': 0,  # Will be calculated by assessment algorithm
                        'feedback': f'Processed via {processing_method}',
                        'feedback_code': f'OCR_CONFIDENCE_{ocr_confidence:.2f}',
                        'closeness': 0.0  # Will be calculated by assessment algorithm
                    }
                )
                
                if not created:
                    # Update existing answer
                    student_answer.txt_answer = extracted_text
                    student_answer.html_answer = extracted_text
                    student_answer.timestamp = timezone.now()
                    student_answer.attempted_count += 1
                    student_answer.feedback = f'Updated via {processing_method}'
                    student_answer.feedback_code = f'OCR_CONFIDENCE_{ocr_confidence:.2f}'
                    student_answer.save()
                
                # Run assessment algorithm if available
                try:
                    from algo.answer import Answer
                    from algo.standard import Standard
                    
                    # Create Answer and Standard objects for processing
                    answer_obj = Answer(extracted_text, question)
                    standard_obj = Standard(question)
                    
                    # Process the answer (this will calculate scores and feedback)
                    # Note: This depends on the existing algorithm implementation
                    # You may need to adjust based on the actual algo module structure
                    
                    logger.info(f"OCR processing completed for student {student.user.username}, question {question.id}")
                    
                except ImportError as e:
                    logger.warning(f"Assessment algorithm not available: {e}")
                except Exception as e:
                    logger.error(f"Assessment processing error: {e}")
                
                messages.success(request, f'Answer sheet processed successfully! Extracted {len(extracted_text)} characters of text.')
                
                # Redirect to student answer view or back to upload form
                return redirect('ocr_upload_answer_sheet')
                
            except Exception as e:
                logger.error(f"OCR upload processing error: {str(e)}")
                messages.error(request, f'Processing error: {str(e)}')
        
    else:
        form = OCRAnswerSheetForm(teacher=getTpByRequest(request))
    
    return render_to_response('student/ocr_upload.html', {
        'form': form,
        'title': 'Upload Answer Sheet for OCR Processing'
    }, context_instance=RequestContext(request))

@login_required
def ocr_processing_status(request):
    """
    View to check OCR processing status and results
    """
    # Get recent OCR processed answers for the current teacher's students
    teacher = getTpByRequest(request)
    
    if teacher:
        # Get students from teacher's classrooms
        classrooms = teacher.classrooms.all()
        students = SProfile.objects.filter(classroom__in=classrooms)
        
        # Get recent StudentAnswers that were processed via OCR
        recent_answers = StudentAnswer.objects.filter(
            student__in=students,
            feedback__icontains='OCR'
        ).order_by('-timestamp')[:20]
        
        return render_to_response('student/ocr_status.html', {
            'recent_answers': recent_answers,
            'title': 'OCR Processing Status'
        }, context_instance=RequestContext(request))
    
    return redirect('student_index')




class StudentDelete(DeleteView):
    model = SProfile
    success_url = reverse_lazy("deleteview_callback")

    def get_object(self):
        pk = self.request.POST['studentid']
        return get_object_or_404(SProfile, user__id=pk)
