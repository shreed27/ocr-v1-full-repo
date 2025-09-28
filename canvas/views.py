# Create your views here.
import pickle
import logging
from django.utils import simplejson as json
from django.views.generic import TemplateView
from django.http import HttpResponse
from canvas.models import Canvas
from question.models import Question
from student.models import StudentAnswer
from algo.canvascompare import Canvascompare

logger = logging.getLogger(__name__)


class CanvasView(TemplateView):
    template_name = 'raphael.html'


def canvas_upload(request):
    response_data = {'state': 'failure'}
    if request.method == "POST":
        print("~~~~~~~~~~~~~~~~~~" * 122)
        print(request.POST)
        id = json.loads(request.POST['id'].encode('utf-8'))
        canvasmap = json.loads(request.POST['canvasmap'].encode('utf-8'))
        try:
            question = Question.objects.get(id=id['questionid'])
            stdanswer = None
            stuanswer = None
            if id.get('stdanswerid'):
                stdanswer = question.stdanswer
            elif id.get('stuanswerid'):
                stuanswer = StudentAnswer.objects.get(id=id['stuanswerid'])
        except Exception as e:
            logger.error(e)
            response_data['state'] = "question not found"
        else:
            for canvasname, canvasitem in list(canvasmap.items()):
                try:
                    if stdanswer:
                        canvas = Canvas.objects.get_or_create(name=str(canvasname),
                                                              question=question, stdanswer=stdanswer, stuanswer=None)
                    elif stuanswer:
                        print('1111111111111111111111111' * 121)
                        canvas = Canvas.objects.get_or_create(name=str(canvasname),
                                                              question=question, stuanswer=stuanswer, stdanswer=None)
                        print('canvas = ', canvas)
                    else:
                        canvas = Canvas.objects.get_or_create(name=str(canvasname),
                                                              question=question, stuanswer=None, stdanswer=None)
                except Exception as e:
                    print(str(e) ,"EXCEP11111111111111111111111111")
                    logger.error(e)
                try:
                    canvas[0].axismap = pickle.dumps(canvasitem['axis'])
                    canvas[0].drawopts = pickle.dumps(canvasitem['drawopts'])
                    canvas[0].rulelist = pickle.dumps(canvasitem['rulelist'])
                except Exception as e:
                    print(str(e), "222222222222222222222222222222222222")
                    logger.error(e)
                print(stuanswer, "STUDENT ANSWER")
                if stuanswer:
                    mark = __canvasmark(question, canvas[0])
                    if not mark:
                        mark = 0
                    print(mark, "MARK555555555555")
                    canvas[0].mark = mark
                    response_data['canvasmark'] = mark
                    print('text twex')
                try:
                    canvas[0].save()
                except Exception as e:
                    print(str(e), "8888888888888888")
                print('End')
            response_data['state'] = "success"
    print(response_data, "response_data response_data")
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __canvasmark(question, stucanvas):
    print("###############################")
    canvasname = stucanvas.name
    print('canvasname  = ', canvasname)
    try:
        stdanswer = question.stdanswer
        stdcanvas = Canvas.objects.get(name=str(canvasname), question=question,
                                       stdanswer=stdanswer, stuanswer=None)
        stddrawopts = pickle.loads(str(stdcanvas.drawopts))
        stdrulelist = pickle.loads(str(stdcanvas.rulelist))
        stdpointlist = pickle.loads(str(stdcanvas.pointlist))
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(e)
    else:
        canvascompare = Canvascompare()
        studrawopts = pickle.loads(str(stucanvas.drawopts))
        sturulelist = pickle.loads(str(stucanvas.rulelist))
        drawoptspair = canvascompare.comparecurvesimilarity(stddrawopts, studrawopts)
        print('drawoptspair = ', drawoptspair)
        logger.info(drawoptspair)
        correctlist = canvascompare.comparelist(sturulelist, stdrulelist)
        print('correctlist = ', correctlist)
        mark = canvascompare.mark(correctlist, stdpointlist)
        print('mark = ', mark)
        return mark


def canvas_get(request):
    if request.method == 'POST':
        print(request.POST)
        response_data = {'state': 'failure'}
        try:
            canvasname = request.POST['name']
            id = json.loads(request.POST['id'].encode('utf-8'))
        except Exception as e:
            logger.error(e)
            response_data['state'] = "no name or id specified"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        try:
            question = Question.objects.get(id=id['questionid'])
            stdanswer = None
            stuanswer = None
            if id.get('stdanswerid'):
                stdanswer = question.stdanswer
            elif id.get('stuanswerid'):
                stuanswer = StudentAnswer.objects.get(id=id['stuanswerid'])
        except Exception as e:
            logger.error(e)
            response_data['state'] = "question not found"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        if stdanswer:
            try:
                canvas = Canvas.objects.get(name=canvasname, question=question,
                                            stdanswer=stdanswer, stuanswer=None)

            except:
                questioncanvas = Canvas.objects.get(name=canvasname, question=question,
                                                    stdanswer=None, stuanswer=None)
                canvas = Canvas.objects.create(name=canvasname, question=question,
                                               stdanswer=stdanswer, stuanswer=None,
                                               drawopts=questioncanvas.drawopts,
                                               axismap=questioncanvas.axismap,
                                               rulelist=questioncanvas.rulelist)
        elif stuanswer:
            try:
                canvas = Canvas.objects.get(name=canvasname, question=question,
                                            stuanswer=stuanswer, stdanswer=None)
                canvas.rulelist = pickle.dumps([])
                print("\n  --------------------")
                print('stu_canvas = ', canvas)
                canvas.save()
            except Exception as e:
                print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                import traceback
                traceback.print_exc()
                logger.info(e)
                canvas = None
        else:
            try:
                canvas = Canvas.objects.get(name=canvasname, question=question,
                                            stdanswer=None, stuanswer=None)

            except Exception as e:
                print("@@@@@@@ last part     1111")
                import traceback
                traceback.print_exc()                
                logger.info(e)
                canvas = None
        if canvas:
            canvasmap = {canvasname: {'axis': pickle.loads(str(canvas.axismap)),
                                      'drawopts': pickle.loads(str(canvas.drawopts)),
                                      'rulelist': pickle.loads(str(canvas.rulelist))
                                      }
                         }
            print(canvasmap, "CANCAS @ canvas_get")
            if canvasmap:
                response_data['canvasmap'] = canvasmap
                response_data['state'] = 'success'
        print('response_data @ last...............\n')
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
