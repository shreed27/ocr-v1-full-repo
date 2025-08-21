import os
import sys
import re
import pickle
import logging
import traceback
from PIL import Image
from bs4 import BeautifulSoup
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson as json
from django.conf import settings
from django.utils.html import strip_tags
from question.models import Question, QuestionImage, StandardAnswer
from student.models import StudentAnswer
from itempool.models import Itempool
from portal.common import (getTpByRequest,
                           getSpByRequest,
                           stripHTMLStrings,
                           stripBody,
                           std_embedded_latex,
                           latex_to_img)
from portal.models import SProfile
from canvas.models import Canvas
from algo.standard import Standard
from algo.markscheme import MarkScheme
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import DeleteView
from paper.models import Paper
import hashlib
from question.forms import QuestionVideoForm
from question.models import QuestionVideo
import settings
# Number of partitions for summarization closeness scores
NUM_CLOSENESS_BANDS = 10
#
# Note: The closeness support is spread out among several files:
#   algo/
#     answer.py: closeness calculation for individual question
#   question/
#     models.py: new database field for closeness band
#     views.py: display of closeness value (as pertains to individual question)
#     templates/question_detail.html: field for min closeness band
#     static/js/question_detail.js: dynamic update of HTML field
#   paper/
#     templates/paper_closeness.json: definition of closeness datatable
#     urls.py: maps /paper/getall_closeness into paper_getall_closeness from views.py
#     views.py: closeness calculation for paper (via averaging) and determation of students in bands
#   report/
#      templates/report_paper.html: HTML definition of Summarization Closeness Report
#      static/js/report_paper_closeness.js: dynamic creation of closeness datatable
#      templates/report_studentanswer.html: includes closeness band
#      static/js/report_reviewquestion.js: dynamic update of closeness summarization
#   student/
#      models.js: new database field for closeness score
#      views.js: updates mark with respect to closeness band
#

logger = logging.getLogger(__name__)
logger.debug("question/views.py: __name__=%s" % __name__)
print "question/views.py: __name__=%s" % __name__

@permission_required('auth.add_user')
def question_add(request):
    logger.debug("question_add()")
    tp, res = getTpByRequest(request, 'login')
    if not tp and res:
        return res
    questionid = request.GET.get('questionid')
    selitempoolid = request.GET.get('itempoolid')
    logger.info("sel itempool id:%s, question id:%s" % (selitempoolid, questionid))
    try:
        itempools = Itempool.objects.filter(accessible=tp)
    except:
        itempools = []
    try:
        questions = Question.objects.filter(accessible=tp)
    except:
        questions = []
    try:
        questionobj = Question.objects.get(id=questionid)
        vidobj = QuestionVideo.objects.get(question=questionobj)
    except:
        questionobj = []
        vidobj = []
    logger.debug("questions: %s" % questions)
    return render_to_response('question_detail.html',
                              {'selitempoolid': selitempoolid,
                               'questionid': questionid,
                               'itempools': itempools,
                               'questions': questions,
                               'vidobj': vidobj,
                               },
                              context_instance=RequestContext(request))

@csrf_exempt
def questionvideo_upload(request):
    response_data = {}
    if request.method == "POST":
        # Get the posted form
        questionid = request.POST["questionid"]
        try:
            questionobj = Question.objects.get(id=questionid)
        except:
            logger.info('question not exists')
            logger.error(sys.exc_info())
            return HttpResponse("Upload Error")
        VideoForm = QuestionVideoForm(request.POST, request.FILES)
        print request
        print VideoForm
        if VideoForm.is_valid():
            # profile = Profile()
            question = questionobj
            videoupload = VideoForm.cleaned_data["videoupload"]
            vidpath = '/static/questionvideos/'
            vidname = str(VideoForm.cleaned_data["videoupload"])
            vidname = __changeNameForVideo(vidname)
            vidsource = vidpath + vidname
            src = vidsource
            vidobj = QuestionVideo.objects.filter(question=question)
            if vidobj:
                vidobj = QuestionVideo.objects.get(question=question)
                vidobj.videoupload = videoupload
                vidobj.src = src
                response_data['src'] = vidobj.src
                vidobj.save()
            else:
                vidobj = QuestionVideo.objects.create(question=question, videoupload=videoupload, src=src)
                vidobj.save()
            # print profile.name
            # print profile.picture
            print "Cleaned Data!"
            # profile.save()
            print 'saved successfully'
            return HttpResponse(json.dumps(response_data),
                 content_type="application/json")
        else:
             print "Form invalid"

    #     MyProfileForm = ProfileForm()
    # return HttpResponse(json.dumps(response_data),
    #         content_type="application/json")
    # return render(request, 'employee/saved.html', locals())
    #  return HttpResponse("return this string")



@permission_required('auth.add_user')
def question_updatename(request):
    logger.info("question_updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {"state": "failure"}
    if tp and request.method == 'POST':
        questionid = request.POST.get("questionid")
        questionname = request.POST.get("questionname")
        itempoolid = request.POST.get("itempoolid")
        try:
            itempool = Itempool.objects.get(id=int(itempoolid))
        except:
            itempool = None
        if questionid and questionname and itempool:
            logger.info("questionid:%s,name:%s" % (questionid, questionname))
            if questionid == "-1":
                try:
                    question = Question.objects.create(teacher=tp,
                                                   qname=questionname.strip(),
                                                   itempool=itempool)
                except:
                    traceback.print_exc()
            else:
                question = Question.objects.get(id=int(questionid.strip()))
                question.qname = questionname.strip()
                question.save()
            logger.info("question %s" % question)
            response_data['questionid'] = question.id
            response_data['questiontype'] = question.qtype
            response_data['description'] = question.description
            response_data['min_closeness_band'] = question.min_closeness_band
            response_data['state'] = "success"
    return HttpResponse(json.dumps(response_data), mimetype="application/json")






def __pointanalysis(fulltext):
    pointlist = []
    text = fulltext.replace('\t', '')
    p = re.compile(r'^\d[\d\D]+?\n$', re.M)
    m = p.findall(text)
    logger.info(m)
    for i in range(0, len(m)):
        num = re.search(r'\d(\.\d)*', m[i]).group()
        pointlist.append({'Point_No': 'P' + num,
                          'Point_Text': m[i][len(num):].replace('\n', ' ')})
    return pointlist

def __changeNameForVideo(name):
    nameArr = re.split('\.', name)
    if len(nameArr) < 2:
        return None, None
    else:
        videoname = "std__%s__video.%s" % (nameArr[0], nameArr[-1])
        return videoname


def __changeNameForStd(name, qid):
    nameArr = re.split('\.', name)
    if len(nameArr) < 2:
        return None, None
    else:
        imagename = "std__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
        thumbname = "thumb__std__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
        return imagename, thumbname


def __changeName(name, qid):
    nameArr = re.split('\.', name)
    if len(nameArr) < 2:
        return None, None
    else:
        imagename = "%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
        thumbname = "thumb__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
        return imagename, thumbname


def __saveImage(image, fpath, fname):
    m = hashlib.md5()
    fullname = os.path.join(fpath, fname)
    with open(fullname, 'wb+') as destination:
        for chunk in image.chunks():
            m.update(chunk)
            destination.write(chunk)
    logger.debug('md5:%s' % m.hexdigest())
    return fullname, m.hexdigest()


def __resizeImage(imageIn, imageOut):
    orig = Image.open(imageIn)
    origW, origH = orig.size
    destW = 75
    rate = float(destW) / float(origW)
    destH = origH * rate
    try:
        orig.thumbnail((destW, destH))
        orig.save(imageOut)
    except:
        logger.error("resize image failed")


@csrf_exempt
def questionimage_upload(request):
    if request.method == 'POST':
        questionid = request.POST["questionid"]
        isStandardImage = request.POST.get('standard_image')
        image = request.FILES.get('Filedata', None)
        #print  'questionid   ===  ', questionid
        nameArr = re.split('\.', image.name)
        try:
            question = Question.objects.get(id=questionid)
        except:
            logger.info('question not exists')
            logger.error(sys.exc_info())
            return HttpResponse("Upload Error")
        else:
            if isStandardImage and isStandardImage == 'yes':
                iscorrect = True
                imagename, thumbname = __changeNameForStd(image.name, questionid)
                print 'imagename   ==  ', imagename,' thumbname    =  ', thumbname
                questionimages = QuestionImage.objects.filter(question=question).exclude(description='del')
                print 'questionimages   ==  ', questionimages
                digests = list(questionimage.digest for questionimage in questionimages)
                
                uploadeddigestimages = QuestionImage.objects.filter(question=question,
                                                                    iscorrect=True).exclude(description='del')
                print 'uploadeddigestimages == ', uploadeddigestimages
                stddigests = list(i.digest for i in uploadeddigestimages)
                uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER, imagename)
                print 'uploadImageFullName   ', uploadImageFullName, 'digest   ', digest
                if digest in digests and digest not in stddigests:
                    print 'description is None'
                    description = None
                else:
                    description = 'del'
            else:
                iscorrect = False
                imagename, thumbname = __changeName(image.name, questionid)
                #print 'imagename', imagename
                uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER, imagename)
                #print 'uploadImageFullName', uploadImageFullName
                #in case uploaded the same img
                questionimages = QuestionImage.objects.filter(question=question).exclude(description='del')
                digests = list(questionimage.digest for questionimage in questionimages)
                if digest in digests:
                    description = 'del'
                else:
                    description = None
                #print "description", description
            if str(nameArr[-1]).lower() not in("pdf", "xlsx", "xls", "docx", "doc", "txt", "odt", "ods"):
                __resizeImage(uploadImageFullName,
                              os.path.join(settings.THUMBNAILFOLDER, thumbname))
            print "Image Name:%s,Image Thumbnail Name:%s" % (imagename, thumbname)
            logger.info("Image Name:%s,Image Thumbnail Name:%s" % (imagename, thumbname))
        try:
            imageObj, is_created = QuestionImage.objects.get_or_create(question=question,
                                                    imagename=image.name,
                                                    abspath=imagename,
                                                    digest=digest,
                                                    description=description,
                                                    iscorrect=iscorrect)
            imageObj.save()
            print "saved", 'imageObj = ', imageObj, 'description = ', description
        except:
            print "exception             ", sys.exc_info()
            return HttpResponse("Upload Error")
        logger.info("upload sucessful")
        return HttpResponse("Upload Success!", mimetype="text/plain")
    else:
        return HttpResponse("Upload Error!", mimetype="text/plain")


@permission_required('auth.add_user')
def question_deleteimage(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        imageid = request.POST.get("imageid")
        try:
            imageToDelete = QuestionImage.objects.get(id=imageid)
        except:
            pass
        else:
            imageToDelete.description = 'del'
            imageToDelete.save()
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

@permission_required('auth.add_user')
def question_deletevideo(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        questionid = request.POST.get("questionid")
        try:
            videoquesobj = Question.objects.get(id=questionid)
            print videoquesobj
            video_obj = QuestionVideo.objects.get(question=videoquesobj)
            print video_obj
            video_obj.src = ""
            video_obj.save()
            response_data['state'] = 'success'
            return HttpResponse(json.dumps(response_data), mimetype='application/json')

        except:
            return HttpResponse(json.dumps(response_data), mimetype='application/json')


@permission_required('auth.add_user')
def question_submit(request):
    logger.debug("question_submit()")
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        tp, res = getTpByRequest(request, None)
        questionid = request.POST.get('questionid')
        itempoolid = request.POST.get('itempoolid')
        question_content = request.POST.get('question_content', "")
        canvasname = request.POST.get('canvasname')
        logger.info("qid:%s, iid:%s" % (questionid, itempoolid))
        try:
            #Itempool Task for that its commented
            # itempool = Itempool.objects.get(teacher=tp, id=int(itempoolid))
            itempool = Itempool.objects.get(accessible=tp, id=int(itempoolid))
            question = Question.objects.get(id=int(questionid))
            for teacher in itempool.accessible.all():
                question.accessible.add(teacher)
            question.save()
        except Exception, e:
            print 'eeeeeeeeeeeeeeeeeeeeee', e
            logger.error(e)
            itempool = None
            question = None
        else:
            _updatecanvas(question, canvasname)
            logger.info("itempool:%s" % itempool)
            logger.info("question:%s" % question)
            if not question_content:
                question.infocompleted &= ~Question.QUESTIONCOMPLETED
                question.save()
            else:
                logger.debug("content:%s" % question_content)
                question.qname = request.POST.get('question_name')
                question.description = request.POST.get('question_desc')
                question.qtype = request.POST.get('question_type')
                logger.debug("qname:%s, desc:%s, qtype:%s" % (question.qname, question.description, question.qtype))
                question.itempool = itempool
                question.teacher = tp
                try:
                    question_content = question_content.decode("utf8").encode('ascii', 'ignore')
                except:
                    try:
                        question_content = question_content.encode('ascii', 'ignore')
                    except:
                        pass
                question.qhtml = stripBody(question_content)
                qtext = stripHTMLStrings(strip_tags(std_embedded_latex(question_content)))
                try:
                    qtext = qtext.decode("utf8").encode('ascii', 'ignore')
                except:
                    try:
                        qtext = qtext.encode('ascii', 'ignore')
                    except:
                        import traceback
                        traceback.print_exc()
                qtext_dump = latex_to_img(qtext)
                question.qtext = qtext_dump
                question.infocompleted |= Question.QUESTIONCOMPLETED
                question.min_closeness_band = request.POST.get('min_closeness_band')
                logger.debug("min_closeness_band: " + question.min_closeness_band)
                for teacher in itempool.accessible.all():
                    question.accessible.add(teacher)
                question.save()
                if question.infocompleted is Question.ALLCOMPLETED:
                    _updatepaper(question)
                response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def _updatecanvas(question, canvasnames, stdanswer=None):
    if not canvasnames:
        return None
    try:
        canvasname = [cname.strip('"') for cname in canvasnames.strip('[]').split(',')]
        #print canvasname
        canvaslist = Canvas.objects.filter(question=question, stdanswer=stdanswer)
        delcanvaslist = canvaslist.exclude(name__in=canvasname)
        logger.debug(delcanvaslist)
        for canvas in delcanvaslist:
            canvas.delete()
    except Exception, e:
        logger.error(e)
    else:
        retcanvas = {}
        for canvas in canvaslist:
            if canvas.name in canvasname:
                try:
                    rulelist = pickle.loads(str(canvas.rulelist))
                except:
                    rulelist = []
                try:
                    markscheme = pickle.loads(str(canvas.markscheme))
                except:
                    markscheme = {}
                try:
                    pointlist = pickle.loads(str(canvas.pointlist))
                except:
                    pointlist = {}
                retcanvas[canvas.name] = {'id': canvas.id, 'occur': 1,
                                          'rulelist': rulelist,
                                          'markscheme': markscheme,
                                          'pointlist': pointlist}
        return retcanvas


@permission_required('auth.add_user')
def question_get(request):
    logger.info("question get")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp and request.method == 'POST':
        questionid = request.POST.get("questionid")
        logger.debug("questionid:%s" % questionid)
        response_data = __getquestiondetail(questionid)
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __getquestiondetail(questionid):
    """
    get question detais: desc, type, question_content, standard_content, itempool,
    canvas, imgthumbnails
    """
    logger.debug("__getquestiondetail(%s)" % questionid)
    if not questionid or questionid is '-1':
        return {'state': 'No Resource'}
    try:
        question = Question.objects.get(id=int(questionid))
        questioncanvas, stdanswercanvas = __getcanvas(question)
        response_data = {'question_desc': question.description,
                         'question_type': question.qtype,
                         'min_closeness_band': question.min_closeness_band,
                         'alt_min_closeness_band': question.alt_min_closeness_band,
                         'question_content': question.qhtml,
                         'standard_content': question.stdanswerhtml,
                         'alt_standard_content': question.alt_stdanswerhtml,
                         'question_item': question.itempool.id,
                         'question_canvas': questioncanvas,
                         'stdanswer_canvas': stdanswercanvas
                         }
    except Exception, e:
        return {'state': 'No Resource'}
    logger.debug("question=%s" % question)

    raw = question.markscheme
    if not raw:
        response_data['question_markscheme'] = []
    else:
        try:
            rawArr = raw.split(',')
        except Exception, e:
            logger.debug('raw:%s, error:%s' % (raw, e))
        else:
            schemelist = []
            if len(rawArr) >= 2:
                for i in range(0, len(rawArr), 2):
                    str1 = str(rawArr[i])
                    str2 = str(rawArr[i + 1])
                    schemelist.append([str1, str2])
            response_data['question_markscheme'] = schemelist

    raw = question.alt_markscheme
    if not raw:
        response_data['alt_question_markscheme'] = []
    else:
        try:
            rawArr = raw.split(',')
        except Exception, e:
            logger.debug('raw:%s, error:%s' % (raw, e))
        else:
            schemelist = []
            if len(rawArr) >= 2:
                for i in range(0, len(rawArr), 2):
                    str1 = str(rawArr[i])
                    str2 = str(rawArr[i + 1])
                    schemelist.append([str1, str2])
            response_data['alt_question_markscheme'] = schemelist            

    rulelist = []
    imgrulelist = []
    if question.stdanswer:
        try:
            rulelist = pickle.loads(str(question.stdanswer.rulelist))
        except Exception, e:
            logger.error(e)
            rulelist = []

        try:
            imgrulelist = pickle.loads(str(question.stdanswer.imgrulelist))
        except Exception, e:
            logger.error(e)
            imgrulelist = []
        logger.debug('rulelist:%s, imgrulelist:%s' % (rulelist, imgrulelist))

    alt_rulelist = []
    if question.alt_stdanswer:
        try:
            alt_rulelist = pickle.loads(str(question.alt_stdanswer.rulelist))
        except Exception, e:
            logger.error(e)
            alt_rulelist = []


        # XXX: go with imgrulelist calcualated by stdanswer.
        # XXX: same is for canvas

        # try:
        #     imgrulelist = pickle.loads(str(question.stdanswer.imgrulelist))
        # except Exception, e:
        #     logger.error(e)
        #     imgrulelist = []
        # logger.debug('rulelist:%s, imgrulelist:%s' % (rulelist, imgrulelist))        

    canvasrulelistlen = 0
    if stdanswercanvas:
        for canvasname in stdanswercanvas:
            canvasrulelistlen += len(stdanswercanvas[canvasname]['pointlist'])

    response_data['alt_rulecount'] = len(alt_rulelist) + len(imgrulelist) + canvasrulelistlen
    response_data['alt_rulelist'] = (alt_rulelist + imgrulelist)[:5000]

    response_data['rulecount'] = len(rulelist) + len(imgrulelist) + canvasrulelistlen
    response_data['rulelist'] = (rulelist + imgrulelist)[:5000]
    response_data['state'] = 'success'
    return response_data


def __getcanvas(question):
    try:
        questioncanvaslist = Canvas.objects.filter(question=question,
                                                   stdanswer=None, stuanswer=None)
    except:
        logger.debug('No questioncanvas found')
        questioncanvaslist = []
    try:
        stdanswer = question.stdanswer
    except:
        logger.debug('No stdanswer found')
        stdanswercanvaslist = []
    else:
        stdanswercanvaslist = Canvas.objects.filter(question=question,
                                                    stdanswer=stdanswer, stuanswer=None)

    questioncanvas = {}
    for canvas in questioncanvaslist:
        questioncanvas[canvas.name] = {'id': canvas.id, 'occur': 1}

    stdanswercanvas = {}
    for canvas in stdanswercanvaslist:
        try:
            rulelist = pickle.loads(str(canvas.rulelist))
        except Exception, e:
            logger.info(e)
            rulelist = []
        try:
            markscheme = pickle.loads(str(canvas.markscheme))
        except Exception, e:
            logger.info(e)
            markscheme = {}
        try:
            pointlist = pickle.loads(str(canvas.pointlist))
        except Exception, e:
            logger.info(e)
            pointlist = {}
        stdanswercanvas[canvas.name] = {'id': canvas.id, 'occur': 1,
                                        'rulelist': rulelist, 'pointlist': pointlist,
                                        'markscheme': markscheme}
    return questioncanvas, stdanswercanvas


@login_required
def stu_question_get(request):
    student, res = getSpByRequest(request, None)
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        questionid = request.POST.get("questionid")
        logger.info("questionid:%s" % questionid)
        if questionid and questionid != '-1':
            question = Question.objects.get(id=int(questionid))
            logger.info("question %s" % question)
            response_data['question_desc'] = question.description
            response_data['question_content'] = question.qhtml
            try:
                stuanswer = StudentAnswer.objects.filter(question=question,
                                                         student=student).latest('timestamp')
                html_answer = stuanswer.html_answer
            except Exception, e:
                logger.error(e)
                pass
            else:
                response_data['question_canvas'] = __getstucanvas(question, stuanswer)
                response_data['question_stuanswer'] = html_answer
                response_data['stuanswerid'] = stuanswer.id
                response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __getstucanvas(question, stuanswer):
    try:
        question_canvas = Canvas.objects.filter(question=question,
                                                stdanswer=None, stuanswer=None)
    except:
        return []
    else:
        stuanswer_canvaslist = []
        for canvas in question_canvas:
            try:
                stuanswer_canvas = Canvas.objects.get(question=question, name=canvas.name, stuanswer=stuanswer)
            except Exception, e:
                import traceback
                traceback.print_exc()
                logger.error(e)
                stuanswer_canvas = Canvas.objects.create(name=canvas.name, question=question, stuanswer=stuanswer)
                # NEW - 2014
                stuanswer_canvas.axismap = pickle.dumps({})
                stuanswer_canvas.drawopts = pickle.dumps({})
                stuanswer_canvas.rulelist = pickle.dumps({})
                stuanswer_canvas.save()
            else:
                if stuanswer_canvas.drawopts is None and stuanswer_canvas.axismap is None:
                    stuanswer_canvas.axismap = canvas.axismap
                    stuanswer_canvas.drawopts = canvas.drawopts
                    stuanswer_canvas.rulelist = pickle.dumps({})
                    stuanswer_canvas.save()
            stuanswer_canvaslist.append(stuanswer_canvas.name)
        return stuanswer_canvaslist


@login_required
def stu_question_thumbnails(request):
    logger.info("student question thumbnails")
    response_data = {'state': 'failure'}
    student, res = getSpByRequest(request, None)
    if request.method == 'POST':
        questionid = request.POST.get("questionid")
        iscorrectParam = request.POST.get("iscorrect")
        if iscorrectParam and iscorrectParam == 'yes':
            iscorrect = True
        else:
            iscorrect = False
        logger.info("questionid:%s iscorrect:%s" % (questionid, iscorrect))
        if questionid and questionid != '-1':
            try:
                question = Question.objects.get(id=int(questionid))
                stuanswer = StudentAnswer.objects.filter(question=question,
                                                         student=student).latest('timestamp')
            except:
                stuanswer = None
                thumbnails = QuestionImage.objects.filter(question=question,
                                                          iscorrect=False)\
                    .exclude(description="del")
                stuthumbnails = None
            else:
                stuthumbnails = stuanswer.stuansimages.all()
                studigests = list(st.digest for st in stuthumbnails)
                thumbnails = QuestionImage.objects.filter(question=question,
                                                          iscorrect=False)\
                    .exclude(description="del")\
                    .exclude(digest__in=studigests)
            logger.info("question %s, thumbnails%s" % (question, thumbnails))
                #[0] thumb,[1] imagename,[2] orig image
            if thumbnails:
                response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                                    t.imagename,
                                                    "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                                    t.id] for t in thumbnails)
            if stuthumbnails:
                response_data['stuthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                                      t.imagename,
                                                      "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                                      t.id] for t in stuthumbnails)
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@permission_required('auth.add_user')
def question_thumbnails(request):
    logger.info("question thumbnails")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp and request.method == 'POST':
        iscorrectParam = request.POST.get("iscorrect")
        if iscorrectParam and iscorrectParam == 'yes':
            iscorrect = True
        else:
            iscorrect = False
        try:
            questionid = request.POST.get("questionid")
            if questionid and questionid != '-1':
                question = Question.objects.get(id=int(questionid))
                thumbnails = QuestionImage.objects.filter(question=question, iscorrect=iscorrect).exclude(description='del')
            else:
                thumbnails = []
        except Exception, e:
            print e
            logger.error(e)
        if thumbnails:
            if iscorrect:
                questionimglist = pickle.loads(str(question.imagepointlist))
                logger.info(questionimglist)
                stdthumbnails = list([imagepoint, t]
                                     for imagepoint in questionimglist
                                     for t in thumbnails
                                     if imagepoint['Point_Text'] == t.digest)
                logger.info(stdthumbnails)
                response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                                   i['Point_No'],
                                                   "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                                   t.id] for i, t in stdthumbnails)
                response_data['stdthumbnail_ids'] = list(t.id for t in thumbnails)
            else:
                pointlist = list({'Point_No': u'P0.' + str(i + 1),
                                  'Point_Text': image.digest}
                                 for i, image in enumerate(thumbnails))
                question.imagepointlist = pickle.dumps(pointlist)
                question.save()
                response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                                    ("P0.%s" % str(i + 1)),
                                                    "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                                    t.id] for i, t in enumerate(thumbnails))
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@permission_required('auth.add_user')
def question_submitstandard(request):
    response_data = {'state': 'failure'}
    questionid = request.POST.get('questionid')
    canvasname = request.POST.get('canvasname')
    logger.info("qid:%s" % questionid)
    try:
        question = Question.objects.get(id=int(questionid))
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error('No question found: %s' % e)
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
    logger.info("question:%s" % question)
    try:
        stdanswer_content = {'html': request.POST.get('standard_content')}
        try:
            stdanswer_content['html'] = stdanswer_content['html'].decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                stdanswer_content['html'] = stdanswer_content['html'].encode('ascii', 'ignore')
            except:
                pass
        #stdanswer_content['html'] = stdanswer_content['html'] # .decode("utf8").encode('ascii', 'ignore')
        stdanswer_content['text'] = stripHTMLStrings(strip_tags(std_embedded_latex(stdanswer_content['html'])))
        try:
            stdanswer_content['text'] = stdanswer_content['text'].decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                stdanswer_content['text'] = stdanswer_content['text'].encode('ascii', 'ignore')
            except:
                import traceback
                traceback.print_exc()
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error(e)

    stdanswer = __parsestdanswer(question, stdanswer_content)
    stdanswer_canvas = _updatecanvas(question, canvasname, stdanswer)
    logger.debug(stdanswer_canvas)
    questioncomplete = __updatestdanswer(question, stdanswer, stdanswer_content)
    if questioncomplete:
        _updatepaper(question)
    logger.info(question.infocompleted)
    response_data['stdanswer_canvas'] = stdanswer_canvas
    response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __parsestdanswer(question, stdanswer_content):
    if not stdanswer_content['text']:
        return None
    #parse txtpointlist
    sinst = Standard()
    print '\n4444444444444444444444444444444444444444444444' * 5
    pointlist, textfdist, slist = sinst.Analysis(stdanswer_content['text'])
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' * 15, '\n' * 4
    print 'pointlist = ',pointlist
    print '\n\n', 'textfdist = ', textfdist
    print '\n\n', 'slist= ', slist
    print "5555555555555555555555555555" * 12
    try:
        imagepointlist = pickle.loads(str(question.imagepointlist))
    except:
        pass
    else:
        for imagepoint in imagepointlist:
            pointlist.append(imagepoint)

    pnlist = list(point['Point_No'] for point in pointlist)
    if pnlist:
        textfdist_dumpped = pickle.dumps(textfdist)
        sentencelist_dumpped = pickle.dumps(slist)
        pointlist_dumpped = pickle.dumps(pointlist)
        try:
            # stdanswer = 
            stdanswer, created = StandardAnswer.objects.get_or_create(name=question.qname,
                                                                      textfdist=textfdist_dumpped,
                                                                      sentencelist=sentencelist_dumpped,
                                                                      pointlist=pointlist_dumpped,
                                                                      alternative=False)
        except Exception, e:
            print "EXCEPTION AT STANDARD ANSWER !!!!!!!!  = ", e
            import traceback
            traceback.print_exc()
            logger.error(e)
            stdanswer = None
        else:
            print 'std answer created     ', stdanswer
            logger.info(stdanswer)
    else:
        stdanswer = None
    print "@ return of std answer ", stdanswer
    return stdanswer




def __updatestdanswer(question, stdanswer, stdanswer_content):
    if stdanswer:
        question.stdanswertext = stdanswer_content['text']
        question.stdanswerhtml = stripBody(stdanswer_content['html'])
        question.stdanswer = stdanswer
        question.infocompleted |= Question.STDANSWERCOMPLETED
    else:
        question.infocompleted &= ~Question.STDANSWERCOMPLETED
    question.save()
    print "successfully saved"
    return (question.infocompleted == Question.ALLCOMPLETED)


@permission_required('auth.add_user')
def question_submitmark(request):
    logger.debug("question_submitmark()")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    try:
        questionid = request.POST.get('questionid')
        question = Question.objects.get(id=questionid)
        stdanswer = question.stdanswer
    except Exception as e:
        print str(e), 'eeeeeeeeeeeeeeeeeeeeeeeeeeee'
        question = None
        stdanswer = None
    else:
        try:
            logger.info("question:%s" % question)
            print "question:%s" % question
            rawschemes = request.POST.get('schemes') or ""
            print 'rawschemes   =   ', rawschemes
            scheme = __parsescheme(rawschemes)
            print 'scheme = ', scheme, "       stdanswer      =  ", stdanswer
            rulecount, rulelist = __updaterulelist(scheme, stdanswer)
            print 'rulecount, rulelist         = ', rulecount, "  ssssssssss  rulelist  = ", rulelist
    
            #update canvas rules
            rawcanvasschemes = request.POST.get('canvasschemes')
            print 'rawcanvasschemes   = ', rawcanvasschemes
            canvasscheme = __parsecanvasscheme(rawcanvasschemes)
            print 'canvasscheme     =  ', rawcanvasschemes
            canvasrulecount, canvasrulelist = __updatecanvasmarkscheme(canvasscheme, question, stdanswer)
            print 'canvasrulecount, canvasrulelist   =   ', canvasrulecount, '        =     ', canvasrulelist
    
            questioncomplete = __updatesheme(question, stdanswer, rawschemes)
            if questioncomplete:
                _updatepaper(question)
    
            response_data['canvasrulelist'] = canvasrulelist
            response_data['rulelist'] = rulelist
            response_data['rulecount'] = rulecount + canvasrulecount
            if rulelist:
                response_data['state'] = 'success'
        except Exception as e:
            print "ellsssssssssssssssssssseeeeeeeeeeeeeeeeeeee"
            import traceback
            print traceback.format_exc()
    print "response_data['state']    mark   = ", response_data['state']
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __parsescheme(rawschemes):
    rawschemelist = rawschemes.split(',')
    imgschemelist = []
    txtschemelist = []
    if len(rawschemelist) >= 2:
        for i in range(0, len(rawschemelist), 2):
            str1 = str(rawschemelist[i])
            str2 = str(rawschemelist[i + 1])
            if 'P0.' in str1:
                imgschemelist.append([str1, str2])
            else:
                txtschemelist.append([str1, str2])
    txtschemelist.sort(key=lambda x: int(x[1]), reverse=True)
    imgschemelist.sort(key=lambda x: int(x[1]), reverse=True)
    if txtschemelist and imgschemelist:
        fullmark = int(imgschemelist[0][1]) + int(txtschemelist[0][1])
    else:
        fullmark = int(txtschemelist[0][1])
    return {'txtscheme': txtschemelist, 'imgscheme': imgschemelist, 'fullmark': fullmark}


def __updaterulelist(scheme, stdanswer):
    logger.debug("__updaterulelist(_,_)")
    if not stdanswer:
        return 0, None
    try:
        std_pointlist = pickle.loads(str(stdanswer.pointlist))
    except:
        stdanswer = None
        count = 0
        nestedrulelist = []
    else:
        #rulelist
        txtplist = list(point['Point_No'] for point in std_pointlist if 'P0.' not in point['Point_No'])
        txtrulelist = []
        if txtplist:
            try:
                ms = MarkScheme(txtplist)
                print 'ms   = ', ms
                txtrulelist = list(rule for rule in ms.GetRules(scheme['txtscheme']))
                print 'txtrulelist   = ', txtrulelist
            except:
                print 'exceptionsssssssssssssss'
                print traceback.format_exc()
        logger.debug("txtrulelist: %s" % txtrulelist)

        #imgrulelist
        imgplist = list(point['Point_No'] for point in std_pointlist if 'P0.' in point['Point_No'])
        imgrulelist = []
        if imgplist:
            try:
                ms = MarkScheme(imgplist)
                imgrulelist = list(rule for rule in ms.GetRules(scheme['imgscheme']))
            except:
                pass
        logger.debug("imgrulelist: %s" % imgrulelist)

        try:
            stdanswer.rulelist = pickle.dumps(txtrulelist)
            stdanswer.imgrulelist = pickle.dumps(imgrulelist)
            stdanswer.fullmark = scheme['fullmark']
            stdanswer.save()
        except Exception, e:
            logger.error(e)
            count = 0
            nestedrulelist = []
        else:
            rulelist = txtrulelist + imgrulelist
            count = len(rulelist)
            nestedrulelist = rulelist[:5000]
    return count, nestedrulelist


def __parsecanvasscheme(rawschemes):
    rawschemelist = rawschemes.split(',')
    schemelist = {}
    if len(rawschemelist) >= 2:
        for i in range(0, len(rawschemelist), 2):
            [canvasname, scheme] = str(rawschemelist[i]).split(':')
            schemelist.setdefault(canvasname, [])
            mark = str(rawschemelist[i + 1])
            schemelist[canvasname].append([scheme, mark])
        return schemelist
    else:
        return None


def __updatecanvasmarkscheme(scheme, question, stdanswer):
    if not scheme:
        return 0, None
    totalcanvasrulelist = []
    for canvasname in scheme:
        canvasscheme = scheme[canvasname]
        try:
            stdcanvas = Canvas.objects.get(name=canvasname, question=question, stdanswer=stdanswer)
            stdcanvasplist = list(rule[0] for rule in pickle.loads(str(stdcanvas.rulelist)))
        except Exception, e:
            logger.error(e)
        else:
            try:
                logger.debug(stdcanvasplist)
                logger.debug(canvasscheme)
                ms = MarkScheme(stdcanvasplist)
                canvasrulelist = list(rule for rule in ms.GetRules(canvasscheme))
                stdcanvas.pointlist = pickle.dumps(canvasrulelist)
                stdcanvas.markscheme = pickle.dumps(canvasscheme)
                stdcanvas.save()
            except Exception, e:
                logger.error(e)
                stdcanvas.markscheme = None
            else:
                for canvasrule in canvasrulelist:
                    canvasrule['Name'] = canvasname
                totalcanvasrulelist += canvasrulelist
    return len(totalcanvasrulelist), totalcanvasrulelist


def __updatesheme(question, stdanswer, rawschemes):
    if stdanswer:
        try:
            question.stdanswer = stdanswer
            question.markscheme = rawschemes
            question.infocompleted |= Question.MARKSCHEMECOMPLETED
            question.save()
        except Exception, e:
            logger.error(e)
            pass
        else:
            return (question.infocompleted == Question.ALLCOMPLETED)
    question.infocompleted &= ~Question.MARKSCHEMECOMPLETED
    question.save()
    return False


def _updatepaper(question):
    if question and question.infocompleted is Question.ALLCOMPLETED:
        papers = question.paper.all()
        for p in papers:
            questions = Question.objects.filter(paper=p, infocompleted=Question.ALLCOMPLETED)
            p.total = len(questions)
            p.save()


class QuestionDelete(DeleteView):
    model = Question
    success_url = reverse_lazy("deleteview_callback")

    def get_object(self):
        pk = self.request.POST['questionid']
        return get_object_or_404(Question, id=pk)


@login_required
def question_getpointmarklist(request):
    student, res = getSpByRequest(request, None)
    questionid = request.POST.get('questionid')
    try:
        question = Question.objects.get(id=questionid)
        stuanswer = StudentAnswer.objects.filter(question=question,
                                                 student=student).latest('timestamp')
    except:
        return HttpResponse('cant find the specified answer')
    answerdetail = {'mark': stuanswer.mark}
    p = re.compile('\'(.*?)\'')
    answerdetail['pointmarklist'] = p.findall(stuanswer.pointmarklist)
    p = re.compile('\[\'(.*?)\'')
    omittedpoint = p.findall(stuanswer.omitted)
    omittedlist = list('P'.join(o) for o in omittedpoint)
    answerdetail['omittedlist'] = omittedlist
    return HttpResponse(json.dumps(answerdetail), mimetype="application/json")


@login_required
def question_getstdanswer(request):
    logger.info("stdanswer get")
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        questionid = request.POST.get("questionid")
        logger.info("questionid:%s" % questionid)
        if questionid and questionid != '-1':
            question = Question.objects.get(id=int(questionid))
            logger.info("question %s" % question)
            response_data['answer_content'] = question.stdanswerhtml
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required
def questionid_get(request):
    logger.info("question id get")
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        paperid = request.POST.get("paperid")
        logger.info(paperid)
        if paperid:
            try:
                paper = Paper.objects.get(id=paperid)
                qids = pickle.loads(str(paper.questionseq))
                qnames = list(Question.objects.get(id=qid).qname for qid in qids)
            except Exception, e:
                logger.error(e)
            else:
                response_data['qids'] = qids
                response_data['qnames'] = qnames
                response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def format_grammar_issues(text):
    """Add basic HTML formatting to grammar issues TEXT"""
    formatted_issues = ""
    if text:
        formatted_issues = "<tiny><pre>\n%s\n</pre></tiny>" % text
    return formatted_issues

@login_required
def question_getstureport(request):
    logger.debug("in question_getstureport")
    # note: Used for student report (see report_studentanswer.html and report_reviewquestion.js)
    response_data = {'state': 'failure'}
    stuid = request.POST.get('studentid')
    qid = request.POST.get('questionid')
    vidobjsrc= ""
    try:
        question = Question.objects.get(id=qid)
        print "Question is ", question
        # questionvid = QuestionVideo.objects.filter(question=question)
        try:
            vidobj = QuestionVideo.objects.get(question=question)
            vidobjsrc = vidobj.src
            print "vidobjsrc is, ", vidobjsrc
        except QuestionVideo.DoesNotExist:
            pass
        stdanswer = question.stdanswer
        stdcanvaslist = Canvas.objects.filter(question=question, stdanswer=stdanswer, stuanswer=None)
        student = SProfile.objects.get(user__id=stuid)
        stuanswer = StudentAnswer.objects.filter(question=question,
                                                 student=student, taked=True).latest('timestamp')
        stucanvaslist = Canvas.objects.filter(question=question, stuanswer=stuanswer, stdanswer=None)
    except Exception, e:
        logger.error(e)
    else:
        response_data['canvas'] = {
            'stucanvas': [[stuanswer.id, stucanvas.name] for stucanvas in stucanvaslist],
            'stdcanvas': [[stdanswer.id, stdcanvas.name] for stdcanvas in stdcanvaslist]
        }
        response_data['stuname'] = student.user.username
        response_data['mark'] = stuanswer.mark
        response_data['question'] = question.qhtml
        response_data['stuanswer'] = stripBody(stuanswer.html_answer)
        response_data['grammar_issues'] = format_grammar_issues(stuanswer.grammar_issues)
        response_data['questionvid'] = vidobjsrc
        # The closeness score is in range [0, 1] and is converted into a percentage with 10 bands,
        # defined as 0-10%, 11-20%, ..., 91-100%.
        closeness = 0
        closeness_band = 0
        if stuanswer.closeness:
            closeness = round(stuanswer.closeness * 100, 1)
            closeness_band = 1 + int(stuanswer.closeness * NUM_CLOSENESS_BANDS)
            closeness_band = max(1, min(closeness_band, NUM_CLOSENESS_BANDS))
        response_data['closeness'] = closeness
        response_data['closeness_band'] = closeness_band
        response_data['num_closeness_bands'] = NUM_CLOSENESS_BANDS
        try:
            response_data['pointmarklist'] = pickle.loads(str(stuanswer.pointmarklist))
        except Exception, e:
            logger.error(e)
            response_data['pointmarklist'] = []
        if stuanswer.omitted:
            omitted = pickle.loads(str(stuanswer.omitted))
            response_data['omitted'] = omitted
            logger.info("omitted: %s" % omitted)
        else:
            response_data['omitted'] = ''
        response_data['state'] = 'success'
        logger.debug("question_getstureport: response_data=%s" % response_data)
    logger.debug("out question_getstureport")
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required
def report_thumbnails(request):
    response_data = {'state': 'failure'}
    logger.info("report question thumbnails")
    if request.method == 'POST':
        studentid = request.POST.get('studentid')
        if studentid:
            try:
                student = SProfile.objects.get(user__id=studentid)
            except:
                student, res = getSpByRequest(request, None)
        questionid = request.POST.get("questionid")
        if questionid and questionid != '-1':
            try:
                question = Question.objects.get(id=int(questionid))
                stuanswer = StudentAnswer.objects.filter(question=question,
                                                         student=student).latest('timestamp')
            except Exception, e:
                logger.error(e)
                pass
            else:
                response_data = __getReportThumbnails(question, stuanswer)
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __getReportThumbnails(question, stuanswer):
    logger.info("question %s,stuanswer%s" % (question, stuanswer))
    response_data = {'state': 'failure'}
    try:
        questionthumbnails = QuestionImage.objects.filter(question=question).exclude(description="del")
        stdthumbnails = QuestionImage.objects.filter(question=question, iscorrect=True).exclude(description="del")
        stuthumbnails = stuanswer.stuansimages.all()
    except:
        pass
    else:
        response_data['questionthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                                    t.imagename,
                                                    "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                                    t.id]
                                                   for t in questionthumbnails)
        response_data['stuthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                               t.imagename,
                                               "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                               t.id]
                                              for t in stuthumbnails)
        response_data['stdthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
                                               t.imagename,
                                               "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
                                               t.id]
                                              for t in stdthumbnails)
        response_data['state'] = 'success'
    return response_data

##########################################################################
################# Alternate Stadard Answer Processing ####################
##########################################################################
# Functions are duplicated to make it compatible with Alternate          #
# Standard Answer fields, There may be some workaround to encounter      #
# these problems                                                         #
##########################################################################

@permission_required('auth.add_user')
def question_alt_submitstandard(request):
    """submit the alternative standard answer for the question"""
    response_data = {'state': 'failure'}
    questionid = request.POST.get('questionid')
    canvasname = request.POST.get('canvasname')

    try:
        question = Question.objects.get(id=int(questionid))
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error('No question found: %s' % e)
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
    logger.info("question:%s" % question)

    try:
        stdanswer_content = {'html': request.POST.get('standard_content')}
        
        try:
            stdanswer_content['html'] = stdanswer_content['html'].decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                stdanswer_content['html'] = stdanswer_content['html'].encode('ascii', 'ignore')
            except:
                pass
        stdanswer_content['text'] = stripHTMLStrings(strip_tags(std_embedded_latex(stdanswer_content['html'])))
        try:
            stdanswer_content['text'] = stdanswer_content['text'].decode("utf8").encode('ascii', 'ignore')
        except:
            try:
                stdanswer_content['text'] = stdanswer_content['text'].encode('ascii', 'ignore')
            except:
                import traceback
                traceback.print_exc()

    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error(e)

    stdanswer = __alt_parsestdanswer(question, stdanswer_content)
    stdanswer_canvas = _updatecanvas(question, canvasname, stdanswer)
    logger.debug(stdanswer_canvas)
    questioncomplete = __alt_updatestdanswer(question, stdanswer, stdanswer_content)
    if questioncomplete:
        _updatepaper(question)
    logger.info(question.infocompleted)
    response_data['stdanswer_canvas'] = stdanswer_canvas
    response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __alt_parsestdanswer(question, stdanswer_content):
    if not stdanswer_content['text']:
        return None
    sinst = Standard()

    pointlist, textfdist, slist = sinst.Analysis(stdanswer_content['text'])
    try:
        imagepointlist = pickle.loads(str(question.imagepointlist))
    except:
        pass
    else:
        for imagepoint in imagepointlist:
            pointlist.append(imagepoint)

    pnlist = list(point['Point_No'] for point in pointlist)
    if pnlist:
        textfdist_dumpped = pickle.dumps(textfdist)
        sentencelist_dumpped = pickle.dumps(slist)
        pointlist_dumpped = pickle.dumps(pointlist)
        try:
            stdanswer, created = StandardAnswer.objects.get_or_create(name=question.qname,
                                                                      textfdist=textfdist_dumpped,
                                                                      sentencelist=sentencelist_dumpped,
                                                                      pointlist=pointlist_dumpped,
                                                                      alternative=True)
        except Exception, e:
            print "EXCEPTION AT STANDARD ANSWER !!!!!!!!  = ", e
            import traceback
            traceback.print_exc()
            logger.error(e)
            stdanswer = None
        else:
            print 'std answer created     ', stdanswer
            logger.info(stdanswer)
    else:
        stdanswer = None
    print "@ return of std answer ", stdanswer
    return stdanswer

# TODO: LEAVE THE CANVAS FOR NOW. WE CAN UPDATE IT LATER
# def _alt_updatecanvas(question, canvasnames, stdanswer=None):
#     if not canvasnames:
#         return None
#     try:
#         canvasname = [cname.strip('"') for cname in canvasnames.strip('[]').split(',')]
#         #print canvasname
#         canvaslist = Canvas.objects.filter(question=question, stdanswer=stdanswer)
#         delcanvaslist = canvaslist.exclude(name__in=canvasname)
#         logger.debug(delcanvaslist)
#         for canvas in delcanvaslist:
#             canvas.delete()
#     except Exception, e:
#         logger.error(e)
#     else:
#         retcanvas = {}
#         for canvas in canvaslist:
#             if canvas.name in canvasname:
#                 try:
#                     rulelist = pickle.loads(str(canvas.rulelist))
#                 except:
#                     rulelist = []
#                 try:
#                     markscheme = pickle.loads(str(canvas.markscheme))
#                 except:
#                     markscheme = {}
#                 try:
#                     pointlist = pickle.loads(str(canvas.pointlist))
#                 except:
#                     pointlist = {}
#                 retcanvas[canvas.name] = {'id': canvas.id, 'occur': 1,
#                                           'rulelist': rulelist,
#                                           'markscheme': markscheme,
#                                           'pointlist': pointlist}
#         return retcanvas


def __alt_updatestdanswer(question, stdanswer, stdanswer_content):
    # duplicating the function to fill up alternative fileds of the 
    # Question object.
    if stdanswer:
        question.alt_stdanswertext = stdanswer_content['text']
        question.alt_stdanswerhtml = stripBody(stdanswer_content['html'])
        question.alt_stdanswer = stdanswer
        print 'question.alt_stdanswer at assign to question answer = ', question.alt_stdanswer
        question.alt_infocompleted |= Question.STDANSWERCOMPLETED
    else:
        question.alt_infocompleted &= ~Question.STDANSWERCOMPLETED
    question.save()
    return (question.alt_infocompleted == Question.ALLCOMPLETED)


@permission_required('auth.add_user')
def question_alt_submitmark(request):
    """
    create or modify the alternate standard mark scheme
    """    
    logger.debug("question_submitmark()")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    try:
        questionid = request.POST.get('questionid')
        question = Question.objects.get(id=questionid)
        stdanswer = question.alt_stdanswer
    except Exception as e:
        print str(e)
        question = None
        stdanswer = None
    else:
        try:
            logger.info("question:%s" % question)
            print "question:%s" % question
            rawschemes = request.POST.get('schemes') or ""
            print 'rawschemes   =   ', rawschemes
            # tip: no need for customization
            scheme = __parsescheme(rawschemes)
            print 'scheme = ', scheme, "       stdanswer      =  ", stdanswer
            rulecount, rulelist = __updaterulelist(scheme, stdanswer)
            print 'rulecount, rulelist         = ', rulecount, "  ssssssssss  rulelist  = ", rulelist
    
            #update canvas rules
            rawcanvasschemes = request.POST.get('canvasschemes')
            print 'rawcanvasschemes   = ', rawcanvasschemes
            canvasscheme = __parsecanvasscheme(rawcanvasschemes)
            print 'canvasscheme     =  ', rawcanvasschemes
            canvasrulecount, canvasrulelist = __updatecanvasmarkscheme(canvasscheme, question, stdanswer)
            print 'canvasrulecount, canvasrulelist   =   ', canvasrulecount, '        =     ', canvasrulelist
    
            questioncomplete = __alt_updatesheme(question, stdanswer, rawschemes)
            print 'questioncomplete    ', questioncomplete
            if questioncomplete:
                _updatepaper(question)
    
            response_data['canvasrulelist'] = canvasrulelist
            response_data['rulelist'] = rulelist
            response_data['rulecount'] = rulecount + canvasrulecount
            print 'rulelist   =  ', rulelist
            if rulelist:
                response_data['state'] = 'success'
        except Exception as e:
            print "ellsssssssssssssssssssseeeeeeeeeeeeeeeeeeee"
            import traceback
            print traceback.format_exc()
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __alt_updatesheme(question, stdanswer, rawschemes):
    if stdanswer:
        try:
            question.alt_stdanswer = stdanswer
            question.alt_markscheme = rawschemes
            question.alt_available = True
            question.alt_infocompleted |= Question.MARKSCHEMECOMPLETED
            question.save()
        except Exception, e:
            logger.error(e)
            pass
        else:
            return (question.alt_infocompleted == Question.ALLCOMPLETED)
    question.alt_infocompleted &= ~Question.MARKSCHEMECOMPLETED
    question.save()
    return False
