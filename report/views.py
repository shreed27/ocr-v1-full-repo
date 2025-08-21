import logging
import pickle
import csv
import time
from traceback import print_exc
from json import loads, dumps
from tempfile import mkstemp
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required, login_required
from paper.models import Paper
from student.models import StudentAnswer
from assignment.models import Assignment, AssignmentFeedback
from question.models import StandardAnswer
from question.models import Question, QuestionVideo
from paper.forms import PaperSearchForm
from report.models import ClosenessReport
from report.forms import DetailSearchForm, FeedbackForm
from portal.common import getSpByRequest, getGroupNameByRequest, getTakedStuanswers, getTpByRequest
from portal.models import SProfile
from paper.templatetags.paper_tags import actual_mark
# from ..paper.templatetags.paper_tags import actual_mark
import re
import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape
from django.utils import simplejson as json

logger = logging.getLogger(__name__)


@permission_required('auth.add_user')
def report_teacher(request):
    group = getGroupNameByRequest(request)
    if group != 'teachers':
        return redirect('teacher_index')
    form = PaperSearchForm()
    if request.method == 'POST':
        pids = request.POST.get('paperids')
        return render_to_response('report_paper.html',
                                  {'form': form, 'pids': pids, 'group': group },
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('report_teacher.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))


@login_required
def report_studentanswer(request):
    form = []
    group = getGroupNameByRequest(request)
    #pids = [int(id) for id in request.POST.get('pids')]
    #stuids = [int(id) for id in request.POST.get('stuids')]
    if request.method == "POST":
        logger.debug("request.POST: %s" % request.POST)
        #get table list of all found papers after select table step 1
        paperids = request.POST.get('paperids')
        pids = []
        stuids = []
        if paperids:
            try:
                paper_stu = re.findall(r'\{pid\:(\d+)\,\sstuid\:(\d+)\}', paperids)
            except Exception, e:
                logger.error(e)
            for pid, stuid in paper_stu:
                pids.append(int(pid))
                stuids.append(int(stuid))
            form = DetailSearchForm(paper=pids, student=stuids)
            return render_to_response('report_studentanswer.html',
                                      {'form': form,
                                       'group': group,
                                       'pids': json.dumps(pids),
                                       'stuids': json.dumps(stuids),
                                       'student_id': stuids[0] if stuids else None,
                                       'paper_id': pids[0] if pids else None,
                                       },
                                      context_instance=RequestContext(request))
        else:
            #get specified papers of students after select table step 2
            try:
                pids = [int(id) for id in request.POST.get('pids').strip('[]').split(',')]
                stuids = [int(id) for id in request.POST.get('stuids').strip('[]').split(',')]
                form = DetailSearchForm(request.POST, paper=pids, student=stuids)
            except Exception, e:
                logger.error(e)
            if form and form.is_valid():
                student = form.cleaned_data['student']
                paper = form.cleaned_data['paper']
            else:
                if not stuids or not pids:
                    return HttpResponse("students or papers do not exist")
                logger.info("stuids[0]:%s,pids[0]:%s ok!" % (stuids[0], pids[0]))
                try:
                    student = SProfile.objects.get(user__id=stuids[0])
                    paper = Paper.objects.get(id=pids[0])
                except Exception, e:
                    logger.error(e)
                    student = None
                    paper = None
            return render_to_response('report_studentanswer.html',
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
        return render_to_response('report_studentanswer.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))


@login_required
def report_question(request):
    questionid = request.GET.get('questionid')
    student, res = getSpByRequest(request, None)
    logger.info(student)
    try:
        question = Question.objects.get(id=questionid)
        studentanswer = StudentAnswer.objects.get(student=student,
                                                  question=question)
        mark = studentanswer.mark
    except:
        return HttpResponse('cant find the specified answer')
    p = re.compile('\'(.*?)\'')
    pointmarklist = []
    try:
        pointmarklist = p.findall(studentanswer.pointmarklist)
    except:
        logger.info("can\'t find pointmark for studentanswer %s" % question.qname)
    pointlist = []
    if pointmarklist:
        for point in pointmarklist:
            pl = 'P' + point
            pointlist.append(pl)
    #p = re.compile('\[\'(.*?)\'')
    omittedpoint = []
    try:
        omittedpoint = p.findall(studentanswer.omitted)
    except:
        logger.info("can\'t find omittedpoint for studentanswer %s" % question.qname)
    omittedlist = []
    if omittedpoint:
        for o in omittedpoint:
            ol = 'P' + o
            omittedlist.append(ol)
    return render_to_response('report_question.html',
                              {'qid': question.id,
                              'mark': mark,
                              'pointmarklist': pointlist,
                              'omittedlist': omittedlist},
                              context_instance=RequestContext(request))


@login_required
def report_student(request):
    group = getGroupNameByRequest(request)
    if group != 'students':
        return redirect('student_index')
    form = PaperSearchForm()
    return render_to_response('report_paper.html',
                              {'form': form},
                              context_instance=RequestContext(request))

@login_required
def feedback_popup(request, pid, stuid):
    group = getGroupNameByRequest(request)

    qid = request.GET.get("question_id")
    if group != 'students':

        paper = Paper.objects.get(id = pid)
        s_profile = SProfile.objects.get(user=stuid)

        fb, s = StudentAnswer.objects.get_or_create(

                                                    question = qid,
                                                    student = s_profile

                                                    )
        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            if form.is_valid():
                fback = request.POST['Add_Feedback']
                fb_code = request.POST['Add_Feedback_Code']


                fb.feedback = fback
                fb.feedback_code = fb_code

                fb.save()
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

        form = FeedbackForm()
        return render_to_response('fb_popup.html',
                                  {'form':form, 'pid':pid, 'stuid': stuid,'fb':fb, 'qid':qid },
                                  context_instance=RequestContext(request)
                                 )

    else:
        """
        The else part is user for show the student report and able to print
        that report """
        qset = []
        student = request.user
        paper = Paper.objects.get(id = pid)
        questionseq = pickle.loads(str(paper.questionseq)) #question sequence are added into this part
        print "paper question sequence", paper.questionseq
        print "question sequence", questionseq
        for q in questionseq:
            qset.append(Question.objects.get(id = q))
        # print "qset" , qset
        stuanswer_set = getTakedStuanswers(qset, student)
        video_set = get_videoForQuestion(qset)
        print "video SETTTTTT", video_set
        # print "stu_answer set" , stuanswer_set
        total_mark = 0
        stud_mark = 0
        for q in stuanswer_set:
            marks = q.question.markscheme.split(",")
            marks = [mark.strip() for mark in marks]
            mark_set = int(marks[marks.index("all") + 1])
            mark_set = actual_mark(q)
            total_mark = total_mark + mark_set
            stud_mark = stud_mark + q.mark

            # print "marks",  marks
            # print "mark_set", mark_set
            # print "total_mark", total_mark
            # print "stud_mark", stud_mark
        #try:
        #    fb = AssignmentFeedback.objects.get(Assignment = paper.assignment,
        #                                                Student = student
        #                                                )
        
        common_student_video = map(None, stuanswer_set, video_set)
        # print "studend answer set" , stuanswer_set
        # print "stu_answer_set *** ", stuanswer_set
        # return render_to_response('report_feedback_report.html',
        #         {'user':student,'paper':paper,'stu':stuanswer_set,
        #          'sum':total_mark,'smark':stud_mark,
        #          'print': True if request.is_ajax() else False,'len':len(questionseq),
        #         })
        print "******** zipped List ********" , common_student_video
        return render_to_response('report_feedback_report.html',
        {'user':student,'paper':paper,'stu':common_student_video,
         'sum':total_mark,'smark':stud_mark,
         'print': True if request.is_ajax() else False,'len':len(questionseq),
        })
        #except:
        #    return HttpResponse("Feedback is not given")

@login_required
def feedback_download(request, pid, stuid):
    """
    For download pdf of student's account
    """
    qid = request.GET.get("question_id")
    qset = []
    student = request.user
    paper = Paper.objects.get(id = pid)
    questionseq = pickle.loads(str(paper.questionseq)) #question sequence are added into this part
    for q in questionseq:
        qset.append(Question.objects.get(id = q))
    stuanswer_set = getTakedStuanswers(qset, student)
    total_mark = 0
    stud_mark = 0
    for q in stuanswer_set:
        marks = q.question.markscheme.split(",")
        marks = [mark.strip() for mark in marks]
        mark_set = mark_set = actual_mark(q)
        total_mark = total_mark + mark_set
        stud_mark = stud_mark + q.mark
    #try:
    #    fb = AssignmentFeedback.objects.get(Assignment = paper.assignment,
    #                                                Student = student
    #                                                )
    template_src = 'report_feedback_report_download.html'
    context_dict ={'user':student,'paper':paper,'stu':stuanswer_set,
             'sum':total_mark,'smark':stud_mark,
             'print': True if request.is_ajax() else False,'len':len(questionseq),
             }
    return generate_pdf(template_src, context_dict)

def generate_pdf(template_src, context_dict):
    # pisa.showLogging(debug=True)
    template = get_template(template_src)
    context = Context(context_dict)
    _html  = template.render(context)
    html_stream = StringIO.StringIO(_html.encode("utf-8"))
    result = StringIO.StringIO()
    # _pdf = pisa.pisaDocument(StringIO.StringIO(_html.encode("UTF-8")), result)
    fid, fname = mkstemp(dir='/tmp')
    pdf_file_name = fname+'.pdf'
    with open(pdf_file_name, "w+") as pdf_file:
        pdf_result = pisa.pisaDocument(html_stream, pdf_file)
    if pdf_result.err:
        print "some error occur when pdf is creating ", pdf_result.err
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    else:
        with open(pdf_file_name) as pdf:
            content = pdf.read()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="feedback.pdf"'
    response.write(content)
    return response
    # return HttpResponse(result.getvalue(), mimetype='application/pdf')


def json_response(response=dict(), success=True, msg=""):
    # multi-purpose json response generator
    return dumps({'success': success, "response": response, "msg": msg})


def get_assignmet(asgn_id):
    # get the assignment obj for given assignment id
    try:
        return Assignment.objects.get(id=asgn_id)
    except (Assignment.DoesNotExist, ValueError) as e:
        print e
        print_exc()
        return None

def get_paper(asgn_id):
    # get the paper obj for given assignment id
    try:
        return Paper.objects.get(assignment__id=asgn_id)
    except Paper.DoesNotExist:
        return None

def get_question(q_id):
    # get Question obj for given id
    try:
        return Question.objects.get(id=q_id)
    except Question.DoesNotExist:
        return None

def get_student_ans(s_id, q_id):
    # get the StudentAnswer obj for given student_id and question_id
    try:
        return StudentAnswer.objects.filter(student__pk=s_id,
            question__id=q_id,
            taked=True).latest('timestamp')
    except StudentAnswer.DoesNotExist:
        return None

def _get_closeness_report(q_id, s_id):
    # get ClosnessReport obj for given question, student id
    try:
        student_answer = get_student_ans(s_id, q_id)
        if not student_answer:
            return None
        return ClosenessReport.objects.get(question__id=q_id, student_answer=student_answer)
    except (ClosenessReport.DoesNotExist, Question.DoesNotExist) as e:
        print e
        print_exc()
        return None

def get_closeness_record_pts(q_id, s_id):
    # closeness record with only points excluding
    # `wrong_pts`, `correct_pts` and `all_pts`
    _record = _get_closeness_report(q_id, s_id)
    if not _record:
        return None

    _record = loads(_record.closeness_record)
    _record = exclue_dict_values(['wrong_pts', 'correct_pts', 'all_pts'], _record)
    return _record

def get_closeness_record(q_id, s_id):
    # returns entire closeness record available in ClosenessRecord
    _record = _get_closeness_report(q_id, s_id)

    if not _record:
        return None
    return loads(_record.closeness_record)

def exclue_dict_values(keys, _dikt):
    # remove list of keys for the dictionary
    for key in keys:
        _dikt.pop(key, None)
    return _dikt

def get_dict_values(keys, _dikt):
    # returns only requested values of keys
    __dikt = dict()
    for key in keys:
        __dikt.update({key: _dikt.get(key, None)})
    return __dikt

def get_closeness_stats(q_id, s_id):
    # returns only `wrong_pts` and `correct_pts`
    _record = _get_closeness_report(q_id, s_id)

    if not _record:
        return None
    _record = loads(_record.closeness_record)
    _record = get_dict_values(['wrong_pts', 'correct_pts'])
    return _record

def get_point_list(question, alternative=False):
    # gets the list of points available for given question.
    try:
        if alternative:
            _point_list = pickle.loads(question.alt_stdanswer.pointlist)
        else:
            _point_list = pickle.loads(question.stdanswer.pointlist)

        return list(pt['Point_No'] for pt in _point_list)
    except (Question.DoesNotExist, StandardAnswer.DoesNotExist) as e:
        print e
        print_exc()
        return list()

def init_points_dict(pointlist):
    # initializes empty points_list dict
    return {point: {'wrong': list(), 'correct': list()} for point in pointlist}

def update_student_closeness(q_id, s_id, s_name, point_dict):
    # update students point wise correctness to the pointlist
    try:
        closeness_stats = get_closeness_record_pts(q_id, s_id)

        if not closeness_stats:
            return None

        for key, value in closeness_stats.iteritems():
            point_dict[key]['correct'].append(s_name) if value else point_dict[key]['wrong'].append(s_name)
    except:
        import traceback
        traceback.print_exc()
    return point_dict

def __get_closeness_report(asgn):
    # helper function for closeness report
    if asgn:
        paper = get_paper(asgn.id)
        students = asgn.students.all()
        qids = pickle.loads(paper.questionseq)

        """
        response = {
            "question_list" : qids,
            "questions": [
                {
                "question_id": qid,
                "question_name": "",
                'point_list': [pids],
                'points': {
                    'p1':{
                        'correct': [students],
                        'wrong': [students]
                    },
                    'p2': {
                        'correct': [students],
                        'wrong': [student]
                    },
                }
            },
            .................
            ],
        }
        """
        response = {
            "qids": qids,
            "questions": list()
        }

        for q_id in qids:
            question = get_question(q_id)
            if question:
                point_list = get_point_list(question)
                points_dict = init_points_dict(point_list)

                for student in students:
                    update_student_closeness(q_id,
                        student.pk,
                        student.user.username,
                        points_dict
                    )

                _question_dict = {
                    "question_id": q_id,
                    "question_name": question.qname,
                    "point_list": point_list,
                    "points": points_dict
                }

                response['questions'].append(_question_dict)

        return response
    else:
        return dict()

def get_closeness_report(request):
    """
    get the closeness report for the given assignment id
    """

    asgn_id = int(request.POST.get('assignment_id', 0))
    asgn = get_assignmet(asgn_id)

    response = __get_closeness_report(asgn)

    if response:
        response = json_response(response=response)
    else:
        response = json_response(success=False, msg="Assignment Not found")

    return HttpResponse(response)


def csv_closeness_report(request):
    # download csv response

    asgn_id = int(request.GET.get('assignment_id', 0))

    asgn = get_assignmet(asgn_id)

    response = __get_closeness_report(asgn)

    csv_response = HttpResponse(mimetype='text/csv')
    csv_response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
        str(asgn.assignmentname) if asgn.assignmentname else "closeness_report"
        )

    writer = csv.writer(csv_response)
    writer.writerow(['Question', 'Points', 'Wrongly Answered Students', 'Correctly Answered Students'])

    if response:
        try:
            for question in response['questions']:
                _wrote_question = False # write question only one time
                for point in question['point_list']:
                    writer.writerow([
                        "" if _wrote_question else question['question_name'],
                        point,
                        ", ".join(question['points'][point]['wrong']),
                        ", ".join(question['points'][point]['correct']),
                    ])
                    _wrote_question = True

                writer.writerow(["", "", "", ""])

        except KeyError as e:
            print e
            print_exc()
    else:
        logger.info("Empty response found")

    return csv_response

def get_videoForQuestion(questionset):
    video_set = list(QuestionVideo.objects.filter(question__in=questionset))
    return video_set

### def csv_closeness_report_summary(request):
# for old format
# def csv_closeness_report_summary(request):
#     """
#     render the closeness report summary for all the assignments
#     """

#     csv_response = HttpResponse(mimetype='text/csv')
#     csv_response['Content-Disposition'] = 'attachment; filename="{0}.csv"'\
#         .format("Closeness Report")

#     # file_obj = file("testing_closeness.csv", "w+")
#     writer = csv.writer(csv_response)
#     # writer = csv.writer(file_obj)
#     try:
#         teacher, res = getTpByRequest(request, None)
#         print teacher, res
#         # static for now
#         assignments = Assignment.objects.filter(teacher=teacher)
#         # assignments = Assignment.objects.filter(teacher__pk=206)
#         #assignments = Assignment.objects.all()
#         print len(assignments)

#         for asgn in assignments:
#             paper = get_paper(asgn.id)
#             if paper:
#                 print "asgn available"
#                 students = asgn.students.all()

#                 header_row = []
#                 detail_row = []

#                 for student in students:
#                     if paper.questionseq:
#                         qids = pickle.loads(paper.questionseq)
#                         taked = False
#                         for qid in qids:
#                             student_answer = get_student_ans(student.pk, qid)
#                             if student_answer and student_answer.taked:
#                                 taked = True

#                         if taked:
#                             header_row = [""]
#                             # initializing the header dictionary
#                             _detail_row = [student.user.username]


#                             # point_record.update([(student.pk, dict())])
#                             for qid in qids:
#                                 question = get_question(qid)
#                                 if question:
#                                     closeness_report = _get_closeness_report(qid, student.pk)
#                                     point_list = get_point_list(
#                                         question, 
#                                         alternative=closeness_report.alternative
#                                     )

#                                     if closeness_report:
#                                         for point in point_list:
#                                             header_row.append("point: " + point +", Q:"+ question.qname)
#                                             _detail_row.append("Correct" if closeness_report.get_pt_value(point) else "Wrong")

#                                         stu_answer = get_student_ans(student.pk, qid)
#                                         header_row += ["CLOSENESS", "MARK"]
#                                         if stu_answer:
#                                             _detail_row += [str(stu_answer.closeness*100)+"%" or "NA", stu_answer.mark or "NA"]
#                                         else:
#                                             _detail_row += ["NA", "NA"]
#                                     else:
#                                         for point in point_list:
#                                             header_row.append("point: " + point +", Q:"+ question.qname)
#                                             _detail_row.append("NA")

#                                         header_row += ["CLOSENESS", "MARK"]
#                                         _detail_row += ["NA", "NA"]

#                             print header_row
#                             print _detail_row
#                             # append to the global list for each assignment
#                             detail_row.append(_detail_row)

#                 # write the actual assignment details to the CSV
#                 writer.writerow(["ASSIGNMENT NAME:", asgn.assignmentname])
#                 writer.writerow([])
#                 writer.writerow(header_row)
#                 writer.writerow(["STUDENT NAME"])
#                 for row in detail_row:
#                     writer.writerow(row)
#                 writer.writerows([[],[]])

#     except Exception, e:
#         print_exc()
#         print e

#     return csv_response


def csv_closeness_report_summary(request):    
    """
    csv closeness report with new format
    """
    csv_response = HttpResponse(mimetype='text/csv')
    csv_response['Content-Disposition'] = 'attachment; filename="{0}.csv"'\
        .format("Closeness Report")

    # file_obj = file("new_closeness_report.csv", "w+")
    writer = csv.writer(csv_response)
    # writer = csv.writer(file_obj)
    try:
        teacher, res = getTpByRequest(request, None)
        print teacher, res
        # static for now
        assignments = Assignment.objects.filter(teacher=teacher)
        # assignments = Assignment.objects.filter(teacher__pk=206)
        # assignments = Assignment.objects.all()
        print len(assignments)

        for asgn in assignments:
            paper = get_paper(asgn.id)
            if paper:
                print "asgn available"
                students = asgn.students.all()

                question_row = []
                header_row = []
                detail_row = []

                for student in students:
                    if paper.questionseq:
                        qids = pickle.loads(paper.questionseq)
                        taked = False
                        for qid in qids:
                            student_answer = get_student_ans(student.pk, qid)
                            if student_answer and student_answer.taked:
                                taked = True

                        if taked:
                            question_row = [""]
                            header_row = ["STUDENT NAME"]                            
                            # initializing the header dictionary
                            _detail_row = [student.user.username]


                            # point_record.update([(student.pk, dict())])
                            for qid in qids:
                                question = get_question(qid)
                                if question:
                                    closeness_report = _get_closeness_report(qid, student.pk)
                                    alternative = closeness_report.alternative if closeness_report else False
                                    point_list = get_point_list(
                                        question, 
                                        alternative=alternative
                                    )

                                    if closeness_report:
                                        for point in point_list:
                                            question_row += ["P:" + point.strip('P') + ", " + question.qname, ""]
                                            header_row += ["Summarization", "Result"]
                                            _detail_row += [
                                                str(closeness_report.get_pt_closeness(point)*100)+"%",
                                                1 if closeness_report.get_pt_value(point) else 0, 
                                            ]
                                    else:
                                        for point in point_list:
                                            question_row += ["P:" + point.strip('P') + ", " + question.qname, ""]
                                            header_row += ["Summarization", "Result"]
                                            _detail_row += ["N/A", "N/A"]


                            print question_row
                            print _detail_row
                            # append to the global list for each assignment
                            detail_row.append(_detail_row)

                # write the actual assignment details to the CSV
                writer.writerow(["ASSIGNMENT NAME:", asgn.assignmentname])
                writer.writerow([])
                writer.writerow(question_row)
                writer.writerow(header_row)
                for row in detail_row:
                    writer.writerow(row)
                writer.writerows([[],[]])

    except Exception, e:
        print_exc()
        print e

    return csv_response    
