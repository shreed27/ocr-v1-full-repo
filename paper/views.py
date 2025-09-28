import logging
import pickle
import traceback
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from paper.models import Paper
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from paper.forms import PaperDetailForm
from itempool.models import Itempool
from question.models import Question
from question.views import NUM_CLOSENESS_BANDS
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import DeleteView
from portal.common import getTpByRequest, getSpByRequest, getTakedStuanswers
from portal.models import SProfile
from django.http import HttpResponse
from django.utils import simplejson
from assignment.models import Assignment
from paper.models import Paper
from student.models import StudentAnswer
logger = logging.getLogger(__name__)


@login_required
def getPaperInfoById(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        paperid = request.POST.get("paperid")
        if paperid:
            try:
                paper = Paper.objects.get(id=int(paperid))
                response_data['papername'] = paper.papername
                response_data['duration'] = paper.duration
            except Exception as e:
                print(e)
            else:
                if paper.assignment:
                    response_data['assignment'] = paper.assignment.assignmentname
                if paper.year:
                    response_data['year'] = paper.year.yearname
                if paper.level:
                    response_data['level'] = paper.level.levelname
                if paper.subject:
                    response_data['subject'] = paper.subject.subjectname
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


@login_required
def paper_getall(request):
    logger.debug("paper_getall(_): method=%s" % request.method)
    if request.method == 'POST':
        logger.debug("request.POST: %s" % request.POST)
        pids = request.POST.get('pids')
        student, res = getSpByRequest(request, None)
        takedpaperlist = list()
        if pids and not student:
            takedpaperlist = __teachermarkreport(pids)
        elif student:
            takedpaperlist = __studentmarkreport(student)
        logger.info("takedpaperlist: %s" % takedpaperlist)
        response = render_to_response('paper_mark.json', {'takedpaperlist': takedpaperlist},
                                      context_instance=RequestContext(request))
    else:
        logger.debug("request.GET: %s" % request.GET)
        forwhat = request.GET.get('forwhat')
        report_type = request.GET.get('report_type')
        if forwhat == 'teacher_report':
            """
               teacher_report default datatable
            """
            try:
                papers = Paper.objects.filter(owner=request.user)
            except:
                papers = []

            if not report_type == "closeness_report":
                response = render_to_response('paper_report.json',
                                              {'papers': papers},
                                              context_instance=RequestContext(request))
            else:
                response = render_to_response('paper_report_closeness.json',
                                              {'papers': papers},
                                              context_instance=RequestContext(request))

        else:
            """
                teacher get all paper ztree
            """
            try:
                papers = Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('paper_all.json', {'papers': papers},
                                          context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    logger.debug("response=%s" % response)
    return response

@login_required
def paper_getall_closeness(request):
    "Return closeness band information"
    pids = request.POST.get('pids')
    response = render_to_response('paper_closeness.json',
                                  {'closeness_band_info': __teacher_closeness_info(pids)},
                                  context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    logger.debug("response=%s" % response)
    return response


def __teachermarkreport(pids):
    """
    teacher report post pids
    """
    takedpaperlist = []
    try:
        paperids = [int(i) for i in pids.split(',')]
        papers = Paper.objects.filter(id__in=paperids)
    except Exception as e:
        print(e)
        papers = []
    for p in papers:
        # Performs equivalent of 'SELECT DISTINCT paper_paper.id, auth_user.username, student_studentanswer.question_id, student_studentanswer.mark FROM student_studentanswer, question_question_paper, paper_paper, assignment_assignment_students, portal_sprofile, auth_user WHERE paper_paper.assignment_id = assignment_assignment_students.assignment_id AND assignment_assignment_students.sprofile_id = portal_sprofile.user_id AND auth_user.id = portal_sprofile.user_id AND question_question_paper.paper_id = paper_paper.id;'
        # TODO student_studentanswer.mark => mark where mark = SELECT SUM(student_studentanswer.mark) from student_studentanswer WHERE student_studentanswer.question_id = question_question_paper.question_id AND question_question_paper.paper_id = paper_paper.id
        students = SProfile.objects.filter(assignment=p.assignment)
        for student in students:
            question_set = Question.objects.filter(paper=p)
            # Note: ignores earlier responses if question was retaken
            stuanswer_set = getTakedStuanswers(question_set, student)
            if stuanswer_set:
                mark = sum(ans.mark for ans in stuanswer_set)
                # Return average of the question closeness scores
                closeness = sum(ans.closeness if ans.closeness else 0.0 for ans in stuanswer_set)
                closeness /= float(len(stuanswer_set))
                ## OLD: takedpaperlist.append([p, student, mark])
                takedpaperlist.append([p, student, mark, closeness])
    logger.debug("__teachermarkreport(%s) => %s" % (pids, takedpaperlist))
    return takedpaperlist


def __teacher_closeness_info(pids):
    """Returns data for summarization closeness band report (in support of paper_closeness.json)"""
    # TODO: reconcile with __teachermarkreport
    if not pids:
        logger.debug("__teacher_closeness_info(%s): no paper id's" % pids)
        return []
    closeness_band_students = [[] for i in range(NUM_CLOSENESS_BANDS)]
    try:
        paperids = [int(i) for i in pids.split(',')]
        papers = Paper.objects.filter(id__in=paperids)
    except Exception as e:
        ## OLD: print e
        papers = []
    total_num_scores = 0
    for p in papers:
        students = SProfile.objects.filter(assignment=p.assignment)
        for student in students:
            question_set = Question.objects.filter(paper=p)
            # Note: ignores earlier responses if question was retaken
            stuanswer_set = getTakedStuanswers(question_set, student)
            if stuanswer_set:
                mark = sum(ans.mark for ans in stuanswer_set)
                # Average the question closeness scores
                closeness = sum(ans.closeness if ans.closeness else 0.0 for ans in stuanswer_set)
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
    logger.debug("__teacher_closeness_info(%s) => %s" % (pids, closeness_band_info))
    return closeness_band_info


def __studentmarkreport(student):
    """
        student report post none
    """
    takedpaperlist = []
    try:
        assignments = Assignment.objects.filter(students=student)
        papers = list(Paper.objects.filter(assignment__in=assignments))
        papers.extend(list(Paper.objects.filter(owner=student.user, ptype='Review')))
    except Exception as e:
        print(e)
        papers = []
    for p in papers:
        question_set = Question.objects.filter(paper=p)
        stuanswer_set = getTakedStuanswers(question_set, student)
        if stuanswer_set:
            mark = sum(ans.mark for ans in stuanswer_set)
            # Return average of the question closeness scores
            closeness = sum(ans.closeness if ans.closeness else 0.0 for ans in stuanswer_set)
            closeness /= float(len(stuanswer_set))
            ## OLD: takedpaperlist.append([p, student, mark])
            takedpaperlist.append([p, student, mark, closeness])
    logger.debug("__studentmarkreport(%s) => %s" % (student, takedpaperlist))
    return takedpaperlist


@permission_required('auth.add_user')
def paper_add(request):
    tp, res = getTpByRequest(request, None)
    if request.method == "POST":
        form = PaperDetailForm(request.POST, teacher=tp)
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
                    paper = Paper.objects.get(id=paperid)
                except:
                    paper = Paper.objects.create(papername=papername,
                                                 passpoint=passpoint,
                                                 ptype=papertype, duration=duration,
                                                 year=year, subject=subject,
                                                 level=level, owner=request.user)
                else:
                    paper.papername = papername
                    paper.ptype = papertype
                    paper.year = year
                    paper.subject = subject
                    paper.level = level
                    paper.duration = duration
                    paper.passpoint = passpoint
            else:
                try:
                    paper = Paper.objects.create(papername=papername,
                                                 passpoint=passpoint,
                                                 ptype=papertype, duration=duration,
                                                 year=year, subject=subject,
                                                 level=level, owner=request.user)
                except:
                    paper = None
            questionlist = form.cleaned_data['questionlist']
            paper.total = len(questionlist)
            logger.info("questionlist:%s" % questionlist)
            __updatequestioninpaper(questionlist, paper)
            paper.questionseq = pickle.dumps([q.id for q in questionlist])
            paper.save()
            print(paper.questionseq)
            messages.add_message(request, messages.SUCCESS, "One Paper Added")
            return redirect("/paper/add?paperid=" + str(paper.id))
    else:
        paperid = request.GET.get('paperid')
        if paperid:
            try:
                p = Paper.objects.get(id=int(paperid))
            except:
                logger.info("paper not found:%s" % paperid)
                form = PaperDetailForm(teacher=tp)
            else:
                logger.info("paper:%s" % p.papername)
                form = PaperDetailForm(teacher=tp,
                                       initial={'paperid': p.id,
                                       'papername': p.papername,
                                       'duration': p.duration,
                                       'passpoint': p.passpoint,
                                       'year': p.year,
                                       'subject': p.subject,
                                       'level': p.level,
                                       'ptype': p.ptype})
        else:
            form = PaperDetailForm(teacher=tp)
    return render_to_response('paper_detail.html', {"form": form},
                              context_instance=RequestContext(request))


def __updatequestioninpaper(questionlist, paper):
    questions = Question.objects.filter(paper=paper)
    temp = []
    for q in questions:
        if q not in questionlist:
            questionseq = pickle.loads(str(paper.questionseq))
            questionseq.remove(q.id)
            q.paper.remove(paper)
            q.save()
            temp.append(q)
    for q in questionlist:
        if q not in temp:
            q.paper.add(paper)
            q.save()


@login_required
def paper_getquestions(request):
    try:
        if request.method == "POST":
            ztreejson = []
            qnum = 0
            paperid = request.POST['paperid']
            try:
                view = request.POST['view']
            except:
                view = 0
            print(view,"view")
            teacher, res = getTpByRequest(request, None)
            student = None
            if not teacher:
                student, res = getSpByRequest(request, None)
                teacher = student.teacher
            logger.info("paper_getquestions,paperid:%s,teacher:%s" % (paperid, teacher))
            def inital_ztree():
                print(1111111111111111111)
                #itempools = Itempool.objects.filter(teacher=teacher)
                itempools = Itempool.objects.filter(accessible=teacher)
                ztreejson = __builduncheckeditempooltree(itempools, view, student)
                return ztreejson
            print(paperid)
            if paperid and paperid != '-1':
                try:
                    paper = Paper.objects.get(id=int(paperid))
                    print('paper.questionseq = ', paper.questionseq)
                    questionseq = pickle.loads(str(paper.questionseq))
                except:
                    paper = None
                    questionseq = []
                print('paper @@= ', paper)
                print('questionseq @@@= ', questionseq)
                if paper and questionseq:
                    ztreejson, qnum, checkeditempools = __buildcheckeditempooltree(questionseq, view, student)
                    try:
                        #totalitempool = Itempool.objects.filter(teacher=teacher)
                        totalitempool = Itempool.objects.filter(accessible=teacher)
                        itempools = list(set(totalitempool) - set(checkeditempools))
                    except:
                        itempools = []
                    else:
                        ztreejson += __builduncheckeditempooltree(itempools, view, student)
                else:
                    ztreejson = inital_ztree()
            else:
                ztreejson = inital_ztree()
            response = render_to_response('paper_allquestions.json',
                                          {'questiontree': ztreejson,
                                           'inum': len(ztreejson), 'qnum': qnum},
                                          context_instance=RequestContext(request))
            response['Content-Type'] = 'text/plain; charset=utf-8'
            response['Cache-Control'] = 'no-cache'
            return response
    except:
        traceback.print_exc()


def __buildcheckeditempooltree(questionseq, view, student):
    # for checkeditempools
    checkeditempools = []
    for qid in questionseq:
        try:
            cq = Question.objects.get(id=qid)
        except:
            pass
        else:
            if cq.itempool not in checkeditempools:
                checkeditempools.append(cq.itempool)
    ztreejson = []
    qnum = 0
    for item in checkeditempools:
        questionnodes = []
        itemnode = {'name': item.poolname, 'checked': 'true'}
        if view:
            itemnode['disabled'] = 'true'
        else:
            itemnode['disabled'] = 'false'
        # checkedquestions
        if student:
            checkedquestions = Question.objects.filter(itempool=item, id__in=questionseq,
                                                       qtype="Review")
        else:
            checkedquestions = Question.objects.filter(itempool=item, id__in=questionseq)
        for q in checkedquestions:
            questionnode = {'node': q, 'checked': 'true'}
            if view:
                questionnode['disabled'] = 'true'
            else:
                questionnode['disabled'] = 'false'
            qnum += 1
            questionnodes.append(questionnode)
        #uncheckedquestions
        if student:
            uncheckedquestions = Question.objects.filter(itempool=item,
                                                         infocompleted=Question.ALLCOMPLETED,
                                                         qtype="Review").exclude(id__in=questionseq)
        else:
            uncheckedquestions = Question.objects.filter(itempool=item,
                                                         infocompleted=Question.ALLCOMPLETED).exclude(id__in=questionseq)
        for q in uncheckedquestions:
            questionnode = {'node': q, 'checked': 'false'}
            if view:
                questionnode['disabled'] = 'true'
            else:
                questionnode['disabled'] = 'false'
            questionnodes.append(questionnode)
        ztreejson.append([itemnode, questionnodes])
    return ztreejson, qnum, checkeditempools


def __builduncheckeditempooltree(itempools, view, student):
    # for uncheckeditempools
    ztreejson = []
    for item in itempools:
        questionnodes = []
        itemnode = {'name': item.poolname, 'checked': 'false'}
        if view:
            itemnode['disabled'] = 'true'
        else:
            itemnode['disabled'] = 'false'
        # get question: if request from student, only qtype=Review
        if student:
            questions = Question.objects.filter(itempool=item,
                                                infocompleted=Question.ALLCOMPLETED,
                                                qtype="Review")
        else:
            questions = Question.objects.filter(itempool=item,
                                                infocompleted=Question.ALLCOMPLETED)
        if questions:
            for q in questions:
                questionnode = {'node': q, 'checked': 'false'}
                if view:
                    questionnode['disabled'] = 'true'
                else:
                    questionnode['disabled'] = 'false'
                questionnodes.append(questionnode)
            ztreejson.append([itemnode, questionnodes])
    print(ztreejson,"ztreejson")
    return ztreejson


class PaperDelete(DeleteView):
    model = Paper
    success_url = reverse_lazy("deleteview_callback")

    def get_object(self):
        pk = self.request.POST['paperid']
        return get_object_or_404(Paper, id=pk)


@permission_required('auth.add_user')
def paper_updatename(request):
    logger.info("paper updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    try:
        if tp:
            paperid = int(request.GET.get('paperid').strip())
            print('paperid = ', paperid)
            papername = request.GET.get('papername')
            print("papername = ", papername)
            if paperid == -1 and papername:
                new_paper = Paper.objects.create(papername=papername,
                                                 owner=tp.user,
                                                 passpoint=0)
                response_data['paperid'] = new_paper.id
                response_data['papername'] = new_paper.papername
                response_data['state'] = 'success'
            else:
                try:
                    paper = Paper.objects.get(id=paperid)
                except Paper.DoesNotExist:
                    paper = None
                print('paper object = ', paper)
                if paper:
                    paper.papername = papername
                    paper.owner = tp.user
                    paper.save()
                    response_data['paperid'] = paper.id
                    response_data['papername'] = paper.papername
                    response_data['ptype'] = paper.ptype
                    response_data['duration'] = paper.duration
                    try:
                        response_data['year'] = [paper.year.id, paper.year.yearname]
                        response_data['subject'] = [paper.subject.id, paper.subject.subjectname]
                        response_data['level'] = [paper.level.id, paper.level.levelname]
                    except:
                        pass
                    response_data['state'] = 'success'
    except:
        traceback.print_exc()
    print(response_data)
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
