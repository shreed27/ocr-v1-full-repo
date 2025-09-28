import logging
import pickle
from datetime import datetime, timedelta
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils import simplejson
from portal.models import TProfile, SProfile
from student.models import StudentAnswer
from student.forms import StudentDetailForm, StudentModifyForm, CustomPaperForm
from canvas.models import Canvas
from portal.common import getSpById, getTpByRequest, getSpByRequest, getGroupNameByRequest, stripHTMLStrings, getStuanswers, getTakedStuanswers
from algo.answer import Answer, ImageAnswer
from django.utils.html import strip_tags
from assignment.models import Assignment
from paper.models import Paper
from classroom.models import Classroom
from question.models import Question, QuestionImage
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


@login_required
def student_index(request):
    sp, res = getSpByRequest(request, 'login')
    if not sp and res:
        return res
    teacher = sp.teacher
    curtime = datetime.now()
    warningtime = curtime + timedelta(days=1)
    try:
        assignments = Assignment.objects.filter(students=sp,
                                                deadline__lt=warningtime,
                                                deadline__gt=curtime)
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
    try:
        student, res = getSpByRequest(request, None)
        teacher = student.teacher
    except:
        student, res = None, None
    else:
        curtime = datetime.now()
        assignments = teacher.assignment_set.filter(deadline__gt=curtime,
                                                    students=student)
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
                count = sum(1 for sa in stuanswer_set if sa.taked)
            except Exception as e:
                logger.error(e)
                logger.error(a)
                logger.error(p)
                break
            if count == p.total:
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
    student, res = getSpByRequest(request, None)
    paperid = request.GET.get("paperid")
    retake = request.GET.get("retake")
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
            anscount = sum(1 for stuanswer in stuanswer_set if stuanswer.taked)
            if anscount == paper.total and paper.ptype != 'Review':
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
            if assignment.deadline < datetime.now() + timedelta(seconds=duration):
                return HttpResponse("Test time %s is due, you haven\'t enough time: %s"
                                    % (assignment.deadline, timedelta(seconds=duration)))
    else:
        assignment = None
        qnameseq = []
        # duration has to be defined
        messages.add_message(request, messages.INFO, 'Paper not found')
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


@login_required
def student_submitanswer(request):
    response_data = {'state': 'failure'}
    student, res = getSpByRequest(request, 'login')
    if not student and res:
        return res
    try:
        qid = request.POST.get('questionid')
        question = Question.objects.get(id=qid)
        stdanswer = question.stdanswer
    except:
        logger.error("question %s not exists" % qid)
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    try:
        answer_html = request.POST.get('answer_html')
        
        try:
            answer_html = answer_html.decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                answer_html = answer_html.decode("utf8").encode('ascii', 'ignore')
            except:
                pass
        anstext = stripHTMLStrings(strip_tags(std_embedded_latex(answer_html)))
        try:
            stdanswer_content['text'] = stdanswer_content['text'].decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                stdanswer_content['text'] = stdanswer_content['text'].encode('ascii', 'ignore')
            except:
                import traceback
                traceback.print_exc()
        anstext = stripHTMLStrings(strip_tags(answer_html))
        stuanswer = StudentAnswer.objects.filter(question=question,
                                                 student=student).latest('timestamp')
        stuanswer.html_answer = answer_html
        stuanswer.txt_answer = anstext
        stuanswer.save()
    except:
        logger.error("cant find stuanswer for question %s" % question)
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    try:
        thumbnail_ids = list(int(i) for i in request.POST['stuthumbnail_ids'].split(','))
    except:
        thumbnail_ids = []
        logger.debug("no img for question %s" % question)
        #stdanswer algorithm to mark stuanswer
    if not stdanswer or not stuanswer:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    else:
        textfdist = _loadlist(stdanswer.textfdist)
        slist = _loadlist(stdanswer.sentencelist)
        pointlist = _loadlist(stdanswer.pointlist)
        rulelist = _loadlist(stdanswer.rulelist)

    try:
        ans = Answer()
        mark, marklist, omitted = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
    except Exception as e:
        marklist = []
        omitted = []
        logger.error(e)

    logger.debug(mark)
    logger.debug(marklist)
    logger.debug(omitted)
    imgmark, stuansimages = __getimgmark(thumbnail_ids, question)

    try:
        stucanvaslist = Canvas.objects.filter(question=question, stuanswer=stuanswer)
        canvasmark = sum(stucanvas.mark for stucanvas in stucanvaslist)
    except Exception as e:
        logger.error(e)
        canvasmark = 0
    # save mark result
    try:
        stuanswer.mark = mark + imgmark + canvasmark
        if omitted:
            stuanswer.omitted = pickle.dumps(omitted)
        else:
            stuanswer.omitted = None
        stuanswer.pointmarklist = pickle.dumps(marklist)
        stuanswer.stuansimages = stuansimages
        stuanswer.save()
    except:
        response_data['state'] = 'failure'
    else:
        response_data['mark'] = stuanswer.mark
        response_data['state'] = 'success'
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
    except Exception as e:
        response_data['state'] = e
        logger.error(e)
    if stuanswer_set:
        totalmark = 0
        for ans in stuanswer_set:
            totalmark += ans.mark
            ans.taked = True
            ans.save()
        if totalmark < p.passpoint:
            response_data['state'] = 'failed'
        else:
            response_data['state'] = 'passed'
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


class StudentDelete(DeleteView):
    model = SProfile
    success_url = reverse_lazy("deleteview_callback")

    def get_object(self):
        pk = self.request.POST['studentid']
        return get_object_or_404(SProfile, user__id=pk)
