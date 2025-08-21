import logging
import re
import os
import hashlib
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
from mcq.forms import MCQ_CustomPaperForm , MCQ_AssignmentDetailForm,MCQ_ItemPoolDetailForm  , MCQ_PaperDetailForm, MCQ_PaperSearchForm , MCQ_DetailSearchForm, MCQ_FeedbackForm
from portal.common import getTpByRequest, getSpByRequest,getGroupNameByRequest, stripHTMLStrings, stripBody 
from django.utils.html import strip_tags
from mcq.models import MCQ_OptionCanvas,MCQ_OptionImage, MCQ_Itempool, MCQ_Question,MCQ_QuestionImage, MCQ_Optionlist, MCQ_Assignment, MCQ_Paper,MCQ_StudentAnswer,MCQ_StudentRetakeAnswer,MCQ_StudentTakenTracking, MCQ_StudentReTakenTracking, MCQ_QuestionCategory, MCQ_Canvas
from portal.common import getTpByRequest, getSpByRequest
from django.utils import simplejson as json
from algo.answer import Answer, ImageAnswer
from portal.models import TProfile,SProfile
from PIL import Image
logger = logging.getLogger(__name__)
from django.db.models import Sum
logger.debug("mcq/question/views.py: __name__=%s" % __name__)
#=======MH16010001====================
# student answer for take and retake can't re-answer again once is answered b4.
#=====================================
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
    return render_to_response('index.html', {'form': form},
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
def getall_mcq_itempool(request):
	# logger.info("mcq = itempool getall...")
	tp, res = getTpByRequest(request, "login")
	if not tp and res:
		return res
	itempools = []
	if tp:
		try:
			itempools = MCQ_Itempool.objects.filter(itp_teacher=tp)
		except:
			pass
	response = render_to_response('mcq_itempool_all.json',
                                  {'itempools': itempools},
                                  context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response


@login_required
def getall_mcq_paper(request):
    if request.method == 'POST':
        pids = request.POST.get('pids')
        student, res = getSpByRequest(request, None)
        if pids and not student:
            takedpaperlist = __teachermarkreport(pids)
        elif student:
            takedpaperlist = __studentmarkreport(student)
        response = render_to_response('mcq_paper_mark.json', {'takedpaperlist': takedpaperlist},
                                      context_instance=RequestContext(request))
    else:
        forwhat = request.GET.get('forwhat')
        if forwhat == 'teacher_report':
            """
               teacher_report default datatable
            """
            try:
                papers = MCQ_Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('mcq_paper_report.json',
                                          {'papers': papers},
                                          context_instance=RequestContext(request))
        else:
            """
                teacher get all paper ztree
            """
            try:
                papers = MCQ_Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('mcq_paper_all.json', {'papers': papers},
                                          context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def getall_mcq_assignment(request):
	teacher, res = getTpByRequest(request, None)
	if not teacher:
		student, res = getSpByRequest(request, None)
		teacher = student.teacher
	try:
		assignments = MCQ_Assignment.objects.filter(teacher=teacher)
	except Exception, e:
		assignments = []
	try:
		forwhat = request.GET.get('forwhat')
	except:
		forwhat = 'default'

	if forwhat == 'teacher_report':
		response = render_to_response('teacherreport_assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))
	else:
		response = render_to_response('mcq_assignment_all.json', {'assignments': assignments},
                                      context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response

# ================== ITEM POOL ================================

def __getItempool(itempoolid, tp=None):
    if not itempoolid or itempoolid == "-1":
        if tp:
            return MCQ_Itempool.objects.create(itp_teacher=tp)
        else:
            return None
    return get_object_or_404( MCQ_Itempool, id=int(itempoolid))

@permission_required('auth.add_user')
def itempool_add(request):
    tp, res = getTpByRequest(request, "login")
    if not tp and res:
        return res
    if request.method == "POST":
        form = MCQ_ItemPoolDetailForm(request.POST, teacher=tp)
        if form.is_valid():
            pass
    else:
        itempoolid = request.GET.get('itempoolid')
        try:
            i = MCQ_Itempool.objects.get(id=itempoolid)
        except:
            form = MCQ_ItemPoolDetailForm(teacher=tp)
        else:
            form = MCQ_ItemPoolDetailForm(teacher=tp,
                                      initial={'itempoolid': i.id,
                                               'itempoolname': i.itp_poolname})
    return render_to_response('mcq_itempool_detail.html', {'form': form},
                              context_instance=RequestContext(request))

def mcq_itempool_updatedesc(request):
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


@permission_required('auth.add_user')
def mcq_itempool_updatename(request):
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


@permission_required('auth.add_user')
def get_mcq_question(request):
    tp, res = getTpByRequest(request, None)
    questions = []
    view = 0
    if tp:
        itempoolid = request.GET.get("itempoolid")
        view = request.GET.get("view")
        if itempoolid:
            try:
                itempool = MCQ_Itempool.objects.get(id=int(itempoolid))
            except:
                itempool = None
            else:
                try:
                    questions = MCQ_Question.objects.filter(teacher=tp, itempool=itempool)
                except:
                     logger.info("no questions in %s" % itempool)
    if view:
        response = render_to_response('mcq_itempool_allquestions_readonly.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    else:
        response = render_to_response('mcq_itempool_allquestions.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response

class ItempoolDelete(DeleteView):
    success_url = reverse_lazy("deleteview_callback")
    model = MCQ_Itempool

    def get_object(self):
        pk = self.request.POST['itempoolid']
        return get_object_or_404(MCQ_Itempool, id=pk)
# ================== END OF ITEM POOL ================================

# ================== Question ==========================================

def __addQuestionCategory(parentQuestionCategory, parentDesc):
	jsonArray = []
	subArray = MCQ_QuestionCategory.objects.filter(qct_sequence=parentQuestionCategory.qct_sequence + 1, qct_QuestionCategory_parentid= parentQuestionCategory.id)
	if subArray != None:
		for rowEach in subArray:
			parentDesc = parentDesc + "=>" + rowEach.qct_description
			logger.info('rowEach %s ' % rowEach)
			jsonArray.append([rowEach.id, parentDesc, rowEach.qct_sequence])
			jsonTemp = __addQuestionCategory(rowEach,parentDesc)
			if jsonTemp != []:
				jsonArray.append(jsonTemp)
	return jsonArray		
@permission_required('auth.add_user')
def mcq_questioncategory_delete(request):
	txtID=request.POST.get('txtID')
	response_data = {'state': 'failure'}
	
	try:
		rowQuestCat = MCQ_QuestionCategory.objects.get(id=int(txtID))
		rowQuestCat.delete()
		response_data['state'] = "success"
	except Exception, E:
		rowQuestCat = None
		logger.debug(E)
	return HttpResponse(json.dumps(response_data), mimetype="application/json")


	
@permission_required('auth.add_user')
def mcq_questioncategory_save(request):
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
			rowQuestCat = MCQ_QuestionCategory.objects.create(qct_category=txtQuestCat,
							   qct_description=txtDesc,
							   qct_sequence=int(txtSeq),
							   qct_QuestionCategory_parentid=int(txtParentid))
			logger.info('new id %s ' % rowQuestCat)
			response_data['newID'] = rowQuestCat.id
		else:
			rowQuestCat = MCQ_QuestionCategory.objects.get(id=int(txtID))
			rowQuestCat.qct_description = txtDesc
			logger.info('the desc: %s ' % txtDesc)
			response_data['state'] = "success"
			rowQuestCat.save()

	except Exception, E:
		rowQuestCat = None
		logger.debug(E)
	
			
	return HttpResponse(json.dumps(response_data), mimetype="application/json")		
	


@permission_required('auth.add_user')
def mcq_questioncategory_edit(request):
	tp, res = getTpByRequest(request, 'login')
	strRow=request.GET.get('row')
	if not tp and res:
		return res
	try:
		rowQuestCat = MCQ_QuestionCategory.objects.get(id=int(strRow))
	except:
		rowQuestCat = None
	if rowQuestCat != None:
		logger.info('rowQuestCat %s' % rowQuestCat)
	return render_to_response('mcq_questioncategory_edit.html',
			{'rowQuestCat': rowQuestCat},
			context_instance=RequestContext(request))		
	

@permission_required('auth.add_user')
def mcq_questioncategory_add(request):
	tp, res = getTpByRequest(request, 'login')
	txtid=request.GET.get('id')
	txtseq=request.GET.get('seq')
	
	return render_to_response('mcq_questioncategory_add.html',
			{'txtID': txtid,
			'txtSeq':txtseq},
			context_instance=RequestContext(request))

	

		
def mcq_questioncategory_generateSub(rowObj):
	logger.info('generatesub %s' % rowObj)
	strOutput = " <a href='/mcq/questioncategory/edit/?row=" + str(rowObj.id) + "' >" + rowObj.qct_category + "</a>"
	try:
		lst_childCategory = MCQ_QuestionCategory.objects.filter(qct_QuestionCategory_parentid=rowObj.id)
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
		strOutput = strOutput + "<li> " + mcq_questioncategory_generateSub(rowchild) + " </li>"
	if b_isEmpty != True:
		strOutput = strOutput + "</ul>"
	return strOutput

@permission_required('auth.add_user')
def mcq_questioncategory_view(request):
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
		lst_questioncategory = MCQ_QuestionCategory.objects.filter(qct_sequence=0)
	except  Exception , e :
		logger.debug("error %s " % e)
		lst_questioncategory = []
	for rowObj in lst_questioncategory:
		strOutput = strOutput + "<li>" + mcq_questioncategory_generateSub(rowObj) + "</li>"
	
	strOutput = mark_safe(strOutput + "</ul>")
	return render_to_response('mcq_questioncategory_detail.html',
			{'testtree': strOutput},
			context_instance=RequestContext(request))
	

@permission_required('auth.add_user')
def mcq_questioncategory_empty(request):
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	
	return render_to_response('mcq_questioncategory_empty.html',
			{},
			context_instance=RequestContext(request))
	

@permission_required('auth.add_user')
def mcq_question_add(request):
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	questionid = request.GET.get('questionid')
	selitempoolid = request.GET.get('itempoolid')
	try:
		itempools = MCQ_Itempool.objects.filter(itp_teacher=tp)
	except:
		itempools = []
	try:
		questions = MCQ_Question.objects.filter(teacher=tp)
	except:
		questions = []

    	questioncategory = []
	try:
		lst_teacher = [tp]
		lst_questioncategory = MCQ_QuestionCategory.objects.filter(qct_sequence=0, qct_teacher__in = lst_teacher)

	except Exception , e:
		logger.info('question category exception %s' % e)
		lst_questioncategory = []
	for rowQC in lst_questioncategory: #==== Array 1 ========
		questioncategory.append([rowQC.id , rowQC.qct_description, rowQC.qct_sequence])
		#jsonTemp = __getQuestionCategory(rowQC,rowQC.qct_description, questioncategory)
		__getQuestionCategory(rowQC,rowQC.qct_description, questioncategory,tp)
		 
	return render_to_response('mcq_question_detail.html',
			{'selitempoolid': selitempoolid,
			'questioncategorys':questioncategory,
			'questionid': questionid,
			'itempools': itempools,
			'questions': questions},
			context_instance=RequestContext(request))
def __addSpaceQuestionCategory(intLoop):
	strValue = ""
	for _ in range(intLoop):
		strValue = strValue + "="
	return strValue
		
def __getQuestionCategory(parentQuestionCategory, parentDesc, lst_param,tp):
	#jsonArray = []
	lst_teacher = [tp]
	subArray = MCQ_QuestionCategory.objects.filter(qct_sequence=parentQuestionCategory.qct_sequence + 1, qct_QuestionCategory_parentid= parentQuestionCategory.id, qct_teacher__in = lst_teacher)
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


def __getquestiondetail(questionid):
    """
    get question detais: desc, type, question_content, standard_content, itempool,
    canvas, imgthumbnails
    """
    if not questionid or questionid is '-1':
        return {'state': 'No Resource'}
    try:
	question = MCQ_Question.objects.get(id=int(questionid))
	questioncat_id = 0
	try:
		questioncat_id = question.qtn_questioncategory.id
	except Exception , e:
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
    except Exception, e:
        return {'state': 'No Resource'}
    return response_data


@login_required
def mcq_question_getid(request):
	logger.info('mcq_question_getid')
	response_data = {'state': 'failure'}
	if request.method == 'POST':
		paperid = request.POST.get("paperid")
	if paperid:
		try:
			paper = MCQ_Paper.objects.get(id=paperid)
			qids = pickle.loads(str(paper.ppr_questionseq))
			qnames = list(MCQ_Question.objects.get(id=qid).qtn_name for qid in qids)
		except Exception, e:
			logger.error(e)
		else:
			response_data['qids'] = qids
			response_data['qnames'] = qnames
			response_data['state'] = 'success'
	return HttpResponse(json.dumps(response_data), mimetype="application/json")



@permission_required('auth.add_user')
def mcq_question_get(request):
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp and request.method == 'POST':
        questionid = request.POST.get("questionid")
        response_data = __getquestiondetail(questionid)
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

@permission_required('auth.add_user')
def mcq_question_updatename(request):
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
			itempool = MCQ_Itempool.objects.get(id=int(itempoolid))
		except:
			itempool = None
		try:
			categoryobj = MCQ_QuestionCategory.objects.get(id=int(questioncategoryid))
		except Exception,e:
			logger.info("exception get question category %s " % e)
			categoryobj = None
		if questionid and questionname and itempool:
			logger.info("this is the questionid: %s" % questionid)
			if questionid == "-1":
				if categoryobj == None:
					question = MCQ_Question.objects.create(teacher=tp,
								   qtn_name=questionname.strip(),
								   qtyn_type=questiontype,
								   itempool=itempool)
				else:
					question = MCQ_Question.objects.create(teacher=tp,
							   qtn_name=questionname.strip(),
							   qtyn_type=questiontype,
							   itempool=itempool,
							   qtn_questioncategory=categoryobj)

			else:
				question = MCQ_Question.objects.get(id=int(questionid.strip()))
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


#============= question image upload =======================
def __changeName(name, qid):
	try:
		nameArr = re.split('\.', name)
		if len(nameArr) < 2:
			return None, None
		else:
			imagename = "%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
			thumbname = "thumb__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
			return imagename, thumbname
	except Exception , e:
		logger.error(e)
def __changeNameForStd(name, qid):
	try:
		nameArr = re.split('\.', name)
		if len(nameArr) < 2:
			return None, None
		else:
			imagename = "std__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
			thumbname = "thumb__std__%s__%s.%s" % ("_".join(nameArr[:-1]), qid, nameArr[-1])
			return imagename, thumbname
	except Exception , err:
		logger.error(err)
def __saveImage(image, fpath, fname):
	try:
		m = hashlib.md5()
		fullname = os.path.join(fpath, fname)
		with open(fullname, 'wb+') as destination:
			for chunk in image.chunks():
				m.update(chunk)
				destination.write(chunk)
		return fullname, m.hexdigest()
	except Exception , e:
		logger.error(e)

def __resizeImage(imageIn, imageOut):
    orig = Image.open(imageIn)
    origW, origH = orig.size
    destW = 75
    rate = float(destW) / float(origW)
    destH = origH * rate
    try:
        orig.thumbnail((destW, destH))
        orig.save(imageOut)
    except Exception , e:
        logger.error("resize image failed %s" % e)


@csrf_exempt
def mcq_question_uploadimage(request):
	if request.method == 'POST':
		questionid = request.POST["questionid"] 
		isStandardImage = request.POST.get('standard_image')
		image = request.FILES.get('Filedata', None)
		try:
			logger.info('questionid: %s' % questionid)
			question = MCQ_Question.objects.get(id=questionid)
			
		except:
			logger.info('question not exists')
			return HttpResponse("Upload Error")
		else:
		    	if isStandardImage and isStandardImage == 'yes':
				iscorrect = True
				imagename, thumbname = __changeNameForStd(image.name, questionid)
				questionimages = MCQ_QuestionImage.objects.filter(qim_question=question).exclude(qim_description='del')
				digests = list(questionimage.digest for questionimage in questionimages)
				uploadeddigestimages = MCQ_QuestionImage.objects.filter(qim_question=question,
						                                    qim_iscorrect=True).exclude(qim_description='del')
				stddigests = list(i.digest for i in uploadeddigestimages)
				uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER, imagename)
				if digest in digests and digest not in stddigests:
				    description = None
				else:
				    description = 'del'
		    	else:
				try:
					
					iscorrect = False
					imagename, thumbname = __changeName(image.name, questionid)
					uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER, imagename)
					questionimages = MCQ_QuestionImage.objects.filter(question=question).exclude(qti_description='del')
					digests = list(questionimage.qti_digest for questionimage in questionimages)
					if digest in digests:
					    description = 'del'
					else:
					    description = None
				except Exception , e:
					logger.error(e)

			__resizeImage(uploadImageFullName,
			  	os.path.join(settings.THUMBNAILFOLDER, thumbname))
		try:
		    	imageObj = MCQ_QuestionImage.objects.create(question=question,
				                            qti_imagename=image.name,
				                            qti_abspath=imagename,
				                            qti_digest=digest,
				                            qti_description=description,
				                            qti_iscorrect=iscorrect)
		    	imageObj.save()
		except:
		    	print sys.exc_info()
		    	return HttpResponse("Upload Error")
		return HttpResponse("Upload Success!", mimetype="text/plain")
	else:
		return HttpResponse("Upload Error!", mimetype="text/plain")


@permission_required('auth.add_user')
def mcq_question_thumbnails(request):
	#logger.info('mcq_question_thumbnails')
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
				question = MCQ_Question.objects.get(id=int(questionid))
				thumbnails = MCQ_QuestionImage.objects.filter(question=question, qti_iscorrect=iscorrect).exclude(qti_description='del')
			else:
				thumbnails = []
		except Exception, e:
			logger.error(e)
		if thumbnails:
			if iscorrect:
				questionimglist = pickle.loads(str(question.imagepointlist))
				stdthumbnails = list([imagepoint, t]
						     for imagepoint in questionimglist
							     for t in thumbnails
							     	if imagepoint['Point_Text'] is t.digest)
				response_data['state'] = 'success' 
				response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
								    ("P0.%s" % str(i + 1)),
								    "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
								    t.id] for i, t in enumerate(thumbnails))
				response_data['stdthumbnail_ids'] = list(t.id for t in thumbnails)
		    	else:
				pointlist = list({'Point_No': u'P0.' + str(i + 1),
				                  'Point_Text': image.qti_digest}
				                for i, image in enumerate(thumbnails))
				response_data['state'] = 'success' 
				response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.qti_abspath),
				                                    ("P0.%s" % str(i + 1)),
				                                    "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
				                                    t.id] for i, t in enumerate(thumbnails))
		return HttpResponse(json.dumps(response_data), mimetype="application/json")

@permission_required('auth.add_user')
def mcq_question_deleteimage(request): 
	try:
		
		tp, res = getTpByRequest(request, None) 
		response_data = { 'state'  : 'failure' } 
	except Exception , e:
		logger.info('error %s ' % e)
	#tp, res = getTpByRequest(request, None)
	if tp and request.method == 'POST':
		try: 
			imageid = request.POST.get("imageid") 
			MCQ_QuestionImage.objects.filter(id=imageid).delete() 
		except Exception , e:
			logger.info('error: %s' % e)
			pass
			
		else:
			#imageToDelete.description = 'del'
			#imageToDelete.save()
			response_data['state'] = 'success'
	else:
		logger.info('failed') 
	return HttpResponse(json.dumps(response_data), mimetype="application/json")


@permission_required('auth.add_user')
def mcq_question_submit(request):
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
            itempool = MCQ_Itempool.objects.get(itp_teacher=tp, id=int(itempoolid))
            question = MCQ_Question.objects.get(id=int(questionid))
        except Exception, e:
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
		except Exception, Err:
			logger.debug(Err)
            else:
		try:
			try:
		            	logger.error('test2a')
				logger.info('ok...something i get this %s' % question_category)
				
		            	logger.error('test2b')
				getQuestionCategory = MCQ_QuestionCategory.objects.get(id=int(question_category))
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
		        question.teacher = tp
			if getQuestionCategory != None:
			        question.qtn_questioncategory = getQuestionCategory
		        question.qty_html = stripBody(question_content)
		        question.qtn_mark = int(question_mark)
		        question.qty_text = stripHTMLStrings(strip_tags(question_content))
		        question.save()
		        response_data['state'] = 'success'
		except Exception, e:
			logger.debug('%s (%s)' % (e.message, type(e)))
			response_data = {'state': 'failure'}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

class QuestionDelete(DeleteView):
	success_url = reverse_lazy("deleteview_callback")
	model = MCQ_Question

	def get_object(self):	
		pk = self.request.POST['questionid']
		return get_object_or_404(MCQ_Question, id=pk)
# ================== End of Question ===================================

# ================== PAPER =============================================

@login_required
def MCQ_GetPaperInfoById(request):
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        paperid = request.POST.get("paperid")
	logger.info('paperid %s ' % paperid)
        if paperid:
            try:
                paper = MCQ_Paper.objects.get(id=int(paperid))
                response_data['papername'] = paper.ppr_papername
                response_data['duration'] = paper.ppr_duration
            except Exception, e:
		logger.error('is here...')
		logger.error("MCQ_GetPaperInfoById Error: %s" % MCQ_GetPaperInfoById)
                print e
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
		except Exception , e:
			logger.error(e)
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")



@login_required
def paper_getall(request):
    if request.method == 'POST':
        pids = request.POST.get('pids')
        student, res = getSpByRequest(request, None)
        if pids and not student:
            takedpaperlist = __teachermarkreport(pids)
        elif student:
            takedpaperlist = __studentmarkreport(student)
        response = render_to_response('paper_mark.json', {'takedpaperlist': takedpaperlist},
                                      context_instance=RequestContext(request))
    else:
        forwhat = request.GET.get('forwhat')
        if forwhat == 'teacher_report':
            """
               teacher_report default datatable
            """
            try:
                papers = Paper.objects.filter(owner=request.user)
            except:
                papers = []
            response = render_to_response('paper_report.json',
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
    return response

# ================== END OF PAPER =============================================

# ================== Option list ==============================================

def str2bool(v):
  return v.lower() in ("yes","Yes", "true","True", "t", "1")
@login_required
def mcq_optionlist_getby_question(request):
	tp, res = getTpByRequest(request, "login")
	if not tp and res:
		return res
	optionlisting = []
	if tp:
		try:
			questionid = request.GET.get("questionid")
			questionObj=MCQ_Question.objects.filter(id=int(questionid))
			optionlisting = MCQ_Optionlist.objects.filter(opl_question=questionObj)
		except:
			pass
	response = render_to_response('mcq_optionlist_all.json',
                                  {'optionlisting': optionlisting},
                                  context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response

@permission_required('auth.add_user')
def mcq_optionlist_add(request):
	logger.info("mcq_optionlist_add")
	tp, res = getTpByRequest(request, 'login')
	if not tp and res:
		return res
	try:
		questionid = request.GET.get('questionid')
		optionlistid = request.GET.get('optionlistid')
		if optionlistid  is not None :  # if is not blank mean is modify mode.
			optionRow = MCQ_Optionlist.objects.get(id=int(optionlistid))
			optionlisting = MCQ_Optionlist.objects.filter(opl_question=optionRow.opl_question)
		else:
			question = MCQ_Question.objects.get(id=questionid)
			optionlisting = MCQ_Optionlist.objects.filter(opl_question=question)
	except Exception, e:
		logger.debug('%s (%s)' % (e.message, type(e)))
		optionlisting = []

	if optionlistid  is not None : 
		return render_to_response('mcq_optionlist_detail.html',
			{'questionid': questionid,
			'optionlisting': optionlisting,
			'optionlst':optionRow},
			context_instance=RequestContext(request))
	else:
		return render_to_response('mcq_optionlist_detail.html',
			{'questionid': questionid,
			'optionlisting': optionlisting},
			context_instance=RequestContext(request))
@permission_required('auth.add_user')
def mcq_optionlist_get(request):
	tp, res = getTpByRequest(request, None)
	response_data = {"state": "failure"}
	if request.method == 'POST':
		if tp:
			try:
				optionID = request.POST.get('KEYVALUE')
				optionlisting=MCQ_Optionlist.objects.get(id=int(optionID))
				response_data = {"optionlist_name":optionlisting.opl_name, 
					"optionlist_description":optionlisting.opl_description, 
					"optionlist_option":optionlisting.opl_option,
					"optionlist_id":optionID,
					"optionlist_correct":optionlisting.opl_iscorrect
					}
			
				response_data['state'] = 'success'
			except Exception, e:
				logger.debug('%s (%s)' % (e.message, type(e)))
				
				response_data = {"state": "failure"}
	return HttpResponse(json.dumps(response_data), mimetype="application/json")


@permission_required('auth.add_user')
def mcq_optionlist_updatefield(request):
	tp, res = getTpByRequest(request, None)
	response_data = {"state": "failure"}
	if request.method == 'POST':
		if tp:
			
			try:
				optionID = request.POST.get('optionlist_id')
				questionID = request.POST.get('questionid')
				optionName = request.POST.get('optionlist_name')
				optionDesc = request.POST.get('optionlist_description')
				optionOption = request.POST.get('optionlist_option')
				optionCorrect = request.POST.get('optionlist_correct')
				logger.info('optionCorrect : %s' % optionCorrect)
				questionObject=MCQ_Question.objects.get(id=int(questionID))
				response_data["optionlist_name"]=optionName
				response_data["optionlist_description"]=optionDesc
				response_data["optionlist_option"]=optionOption
				response_data["questionid"]=questionID
				response_data["optionlist_id"]=int(optionID)
				response_data["optionlist_correct"]=str2bool(optionCorrect)
				logger.info('21111' )
				if optionID == "-1":
					optionObject = MCQ_Optionlist.objects.create(opl_name=optionName.strip(),
						opl_description=optionDesc,opl_option=optionOption
						,opl_iscorrect=str2bool(optionCorrect),opl_question=questionObject)
					response_data["optionlist_id"]=optionObject.id;
				else:
					optionObject = MCQ_Optionlist.objects.get(id=int(optionID.strip()))
					optionObject.opl_name = optionName.strip()
					optionObject.opl_description = optionDesc
					optionObject.opl_option = optionOption
					optionObject.opl_iscorrect=str2bool(optionCorrect)
					optionObject.save()
				
				response_data["state"]="success"
			except Exception, e:
				logger.debug('%s (%s)' % (e.message, type(e)))
				
				response_data = {"state": "failure"}

	return HttpResponse(json.dumps(response_data), mimetype="application/json")

class OptionlistDelete(DeleteView):
	success_url = reverse_lazy("deleteview_callback")
	model = MCQ_Optionlist

	def get_object(self):	
		pk = self.request.POST['optionlistid']
		return get_object_or_404(MCQ_Optionlist, id=pk)
# ================== End of Optin list ========================================

#=================== Paper =====================================================

@login_required
def mcq_student_custompaper(request):
    student, res = getSpByRequest(request, 'login')
    #add custompaper
    if request.method == "POST":
        form = MCQ_CustomPaperForm(request.POST, owner=request.user)
        if form.is_valid():
            paperid = int(form.cleaned_data['paperid'])
            papername = form.cleaned_data['papername']
            duration = form.cleaned_data['duration']
            if paperid != -1:
                paper = MCQ_Paper.objects.get(id=paperid)
                paper.ppr_papername = papername
                paper.ppr_papertype = 'Review'
                paper.owner = student.user
                paper.ppr_duration = duration
                paper.ppr_passpoint = 0
            else:
                paper = MCQ_Paper.objects.create(ppr_papername=papername,
                                             ppr_duration=duration, ppr_passpoint=0,
                                             ppr_papertype="Review", owner=request.user)
            questionlist = form.cleaned_data['questionlist']
            paper.questionseq = pickle.dumps([q.id for q in questionlist])
            paper.total = len(questionlist)
            logger.debug("questionlist:%s" % questionlist)
            __updatequestioninpaper(questionlist, paper)
            paper.save()
            return redirect("/mcq/student/takeassignment?paperid=" + str(paper.id))
    else:
        #show add custompaper view
        paperid = request.GET.get('paperid')
        if paperid:
            try:
                p = MCQ_Paper.objects.get(id=paperid)
            except:
                logger.debug("paper not found:%s" % paperid)
                pass
            logger.debug("paper:%s" % p)
            logger.debug(type(request.user))
            form = MCQ_CustomPaperForm(initial={'paperid': p.id,
                                            'papername': p.ppr_papername,
                                            'duration': p.ppr_duration},
                                   owner=request.user)
        else:
            form = MCQ_CustomPaperForm(owner=request.user)
    return render_to_response('mcq_student_custompaper.html', {'form': form},
                              context_instance=RequestContext(request))




def __teacher_closeness_info(pids):
	"""Returns data for summarization closeness band report (in support of paper_closeness.json)"""
	# TODO: reconcile with __teachermarkreport
	if not pids:
		return []
	closeness_band_students = [[] for i in range(NUM_CLOSENESS_BANDS)]
	try:
		paperids = [int(i) for i in pids.split(',')]
		papers = MCQ_Paper.objects.filter(id__in=paperids)
	except Exception, e:
		papers = []
	logger.info('__teacher_closeness_info papers %s' % papers)
	total_num_scores = 0
	for p in papers:
		try:
			students = SProfile.objects.filter(mcq_assignment=p.assignment)
		except Exception, e:
			# logger.error('error here found')
			logger.error(e)
		for student in students:
			question_set = MCQ_Question.objects.filter(paper=p)
			# Note: ignores earlier responses if question was retaken
			stuanswer_set = getTakedStuanswers(question_set, student,p,isRetake)
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
	except Exception,  Err:
		logger.debug("Error: %s" % Err)
def __teachermarkreport(pids):
	"""
	teacher report post pids
	"""
	takedpaperlist = []
	try:
		paperids = [int(i) for i in pids.split(',')]
		papers = MCQ_Paper.objects.filter(id__in=paperids)
	except Exception, e:
		logger.debug('__teachermarkreport : %s' % e)
		print e
		papers = []
	for p in papers:
		logger.info('paper %s ' % p)
		#============= Alternate way to get p		
		lst_assignment = MCQ_Assignment.objects.filter(id=p.assignment.id).values('asm_students')
		stuid = []
		for row_assign in lst_assignment :
			logger.info("row_assign %s " % row_assign["asm_students"])
			stuid.append(int(row_assign["asm_students"]))
		logger.info('stuids: %s ' % stuid)
		students = SProfile.objects.filter(user__id__in=stuid)
		logger.info('students %s ' % students)
		for student in students:
			logger.info('student %s ' % student)
			question_set = MCQ_Question.objects.filter(paper=p)
			# Note: ignores earlier responses if question was retaken
			stuanswer_set = getTakedStuanswers(question_set, student,p)
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
		response = render_to_response('mcq_paper_mark.json', {'takedpaperlist': takedpaperlist},
			context_instance=RequestContext(request))
	else:
		logger.info('mcq_paper_getall zone 2')
		forwhat = request.GET.get('forwhat')
		if forwhat == 'teacher_report':
			"""
			teacher_report default datatable
			"""
			try:
				papers = MCQ_Paper.objects.filter(owner=request.user)
			except:
				papers = []
			logger.info('use mcq_paper_report.json')
			response = render_to_response('mcq_paper_report.json',
				{'papers': papers},
				context_instance=RequestContext(request))
		else:
			"""
			teacher get all paper ztree
			"""
			try:
				papers = MCQ_Paper.objects.filter(owner=request.user)
			except:
				papers = []
			logger.info('use mcq_paper_all.json')
			response = render_to_response('mcq_paper_all.json', {'papers': papers},
				context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response



@permission_required('auth.add_user')
def mcq_paper_add(request):
	tp, res = getTpByRequest(request, None)
	if request.method == "POST":
		form = MCQ_PaperDetailForm(request.POST, teacher=tp)
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
					paper = MCQ_Paper.objects.get(id=paperid)
				except:
					paper = MCQ_Paper.objects.create(ppr_papername=papername,
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
					paper = MCQ_Paper.objects.create(ppr_papername=papername,
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
			print paper.ppr_questionseq
			messages.add_message(request, messages.SUCCESS, "One Paper Added")
			# logger.info(' saved done, going to redirect page')
			return redirect("/mcq/paper/add?paperid=" + str(paper.id))
		else:
			logger.info(' ops.... got error for form.isvalid()')
	else:
		# logger.info(' ok ..inside mcq paper add get')
		paperid = request.GET.get('paperid')
		if paperid:
			try:
				p = MCQ_Paper.objects.get(id=int(paperid))
			except:
				logger.info("paper not found:%s" % paperid)
				form = MCQ_PaperDetailForm(teacher=tp)
			else:	
				# logger.info("paper:%s" % p.ppr_papername)
				form = MCQ_PaperDetailForm(teacher=tp,
				       initial={'paperid': p.id,
				       'papername': p.ppr_papername,
				       'duration': p.ppr_duration,
				       'passpoint': p.ppr_passpoint,
				       'year': p.year,
				       'subject': p.subject,
				       'level': p.level,
				       'ptype': p.ppr_papertype})
		else:
    			form = MCQ_PaperDetailForm(teacher=tp)
	return render_to_response('mcq_paper_detail.html', {"form": form},
		context_instance=RequestContext(request))
@permission_required('auth.add_user')
def mcq_paper_updatename(request):
    # logger.info("paper updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp:
        paperid = request.GET.get('paperid')
        papername = request.GET.get('papername')
        if paperid and papername:
            paper = MCQ_Paper.objects.get(id=int(paperid.strip()))
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
            paper = MCQ_Paper.objects.create(ppr_papername=papername,
                                         ppr_papertype='Formal', owner=tp.user)
            response_data['paperid'] = paper.id
            response_data['papername'] = paper.ppr_papername
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
def __updatequestioninpaper(questionlist, paper):
	# logger.debug("i'm in __updatequestioninpaper , Paper= %s" % paper)
	questions = MCQ_Question.objects.filter(paper=paper)
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






@login_required
def mcq_paper_getquestions(request):
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

		print paperid
		if paperid and paperid != '-1':
			# logger.info("paper_getquestion ....option 1a")
		    	try:	
				# logger.info("paper_getquestion ....option 1a_1 , with paper id: %s " % paperid)
				paper = MCQ_Paper.objects.get(id=int(paperid))
				# logger.info("paper_getquestion ....option 1a_2")
				print paper.ppr_questionseq
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
				    		totalitempool = MCQ_Itempool.objects.filter(itp_teacher=teacher)
				    		itempools = list(set(totalitempool) - set(checkeditempools))
						# logger.info("paper_getquestion ....option 1b c")
					except:
				    		itempools = []
					else:
						# logger.info("paper_getquestion ....option 1b")
				    		ztreejson += __builduncheckeditempooltree(itempools, view, student)
				
			except Exception, e:
				logger.error(e)
		elif paperid == '-1':
	    		itempools = MCQ_Itempool.objects.filter(itp_teacher=teacher)
	    		ztreejson = __builduncheckeditempooltree(itempools, view, student)
	    		qnum = 0
		else:
			ztreejson = []
			qnum = 0
		response = render_to_response('mcq_paper_allquestion.json',
		                              {'questiontree': ztreejson,
		                               'inum': len(ztreejson), 'qnum': qnum},
		                              context_instance=RequestContext(request))
		response['Content-Type'] = 'text/plain; charset=utf-8'
		response['Cache-Control'] = 'no-cache'
		return response

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
			questions = MCQ_Question.objects.filter(itempool=item,
				qtyn_type="Review")
		else:
			#questions = Question.objects.filter(itempool=item,
			#	infocompleted=Question.ALLCOMPLETED)
			questions = MCQ_Question.objects.filter(itempool=item)
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


def __buildcheckeditempooltree(questionseq, view, student):
	# for checkeditempools
	checkeditempools = []
	for qid in questionseq:
		try:
			cq = MCQ_Question.objects.get(id=qid)
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
			checkedquestions = MCQ_Question.objects.filter(itempool=item, id__in=questionseq,
				                               qtype="Review")
		else:
			checkedquestions = MCQ_Question.objects.filter(itempool=item, id__in=questionseq)
		for q in checkedquestions:
			questionnode = {'node': q, 'checked': 'true'}
			if view:
				questionnode['disabled'] = 'true'
			else:
				questionnode['disabled'] = 'false'
			qnum += 1
			questionnodes.append(questionnode)
		if student:
            		uncheckedquestions = MCQ_Question.objects.filter(itempool=item,                                                        
                                                         qtype="Review").exclude(id__in=questionseq)
		else:
			uncheckedquestions = MCQ_Question.objects.filter(itempool=item
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

class PaperDelete(DeleteView):
	# logger.info('ok.... in PaperDelete')
	model = MCQ_Paper
	success_url = reverse_lazy("deleteview_callback")

	def get_object(self):
		pk = self.request.POST['paperid']
		return get_object_or_404(MCQ_Paper, id=pk)


#====================== Assignment =========================================
@permission_required('auth.add_user')
def MCQ_assignment_getstudents(request):
    # logger.info("assignment_getstudents")
    if request.method == "POST":
        assignmentid = request.POST['assignmentid']
        view = request.POST.get('view', False)
        teacher, res = getTpByRequest(request, None)
        # logger.info("assignment_getstudents, teacher:%s,assignmentid:%s" % (teacher, assignmentid))
        try:
            assignment = MCQ_Assignment.objects.get(id=assignmentid)
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

def __updatestuinassignment(assignment, studentlist):
    try:
        students = MCQ_Assignment.asm_students.all()
    except Exception , e:
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

def __updatepaperinassignment(assignment, paperlist):
    try:
        papers = MCQ_Paper.objects.filter(assignment=assignment)
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

@login_required
def mcq_assignment_add(request):
    teacher, res = getTpByRequest(request, None)
    if request.method == "POST":
        form = MCQ_AssignmentDetailForm(request.POST, teacher=teacher)
	# logger.info('form: %s' % form)
        if form.is_valid():
            if not teacher:
                student, res = getSpByRequest(request, None)
                teacher = student.teacher
            # logger.info("assignment add:%s" % teacher)
            assignmentid = int(form.cleaned_data['assignmentid'])
            if assignmentid != -1:
                assignment = MCQ_Assignment.objects.get(id=assignmentid)
                assignment.teacher = teacher
            else:
                assignment = MCQ_Assignment.objects.create(asm_assignmentname=form.cleaned_data['assignmentname'],
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
            return redirect("/mcq/assignment/add?assignmentid=" + str(assignment.id))
        else:
            # logger.info("form invalid")
            messages.add_message(request, messages.SUCCESS, "You missed some values")
    else:
        assignmentid = request.GET.get('assignmentid')
        form = MCQ_AssignmentDetailForm(teacher=teacher)
        if assignmentid:
            try:
                assignment = MCQ_Assignment.objects.get(id=assignmentid)
            except:
                form = MCQ_AssignmentDetailForm(teacher=teacher)
                # logger.info("assignment not found:%s" % assignmentid)
            else:
                # logger.info("paper:%s" % MCQ_Assignment)
                papers = MCQ_Paper.objects.filter(assignment=assignment)
                form = MCQ_AssignmentDetailForm(teacher=teacher,
                                            initial={'assignmentid': assignment.id,
                                                     'papername': assignment.asm_assignmentname,
                                                     'testdate': assignment.asm_datecreated,
                                                     'deadline': assignment.asm_deadline,
                                                     'description': assignment.asm_description.replace('</br>', '\n'),
                                                     'papers': papers})
    return render_to_response('mcq_assignment_detail.html',
                              {'form': form},
                              context_instance=RequestContext(request))

@permission_required('auth.add_user')
def mcq_assignment_updatename(request):
    # logger.info("assignment updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if not tp:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    assignmentid = request.GET.get('assignmentid').strip()
    assignmentname = request.GET.get('assignmentname')
    if assignmentid and assignmentid != '-1' and assignmentname:
        try:
            assignment = MCQ_Assignment.objects.get(id=int(assignmentid), teacher=tp)
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
            papers = MCQ_Paper.objects.filter(assignment=assignment)
            response_data['papers'] = list(p.id for p in papers)
            response_data['state'] = 'success'
            # logger.info(papers)
    elif assignmentid == '-1':
        try:
            assignment = MCQ_Assignment.objects.create(teacher=tp)
        except:
            pass
        else:
            response_data['assignmentid'] = assignment.id
            response_data['assignmentname'] = assignment.asm_assignmentname
            response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")



@permission_required('auth.add_user')
def mcq_assignment_getstudents(request):
    # logger.info("assignment_getstudents")
    if request.method == "POST":
        assignmentid = request.POST['assignmentid']
        view = request.POST.get('view', False)
        teacher, res = getTpByRequest(request, None)
        # logger.info("assignment_getstudents, teacher:%s,assignmentid:%s" % (teacher, assignmentid))
        try:
            assignment = MCQ_Assignment.objects.get(id=assignmentid)
            checkedstudents = assignment.asm_students.all()
	    # logger.info("ok....i'm in here after get checkedstudent")
        except:
	    # logger.error("ok..... error here checkedstudents")
            checkedstudents = []

        stu_teacher_list = []
        teachernode = {'name': teacher.user.username, 'checked': 'true'}
        if view:
            teachernode['disabled'] = 'true'
        else:
            teachernode['disabled'] = 'false'

        stunodes = []
        try:
	    # logger.info("get stduent start")	
            students = SProfile.objects.filter(teacher=teacher)
	    # logger.info("get student end")	
        except Exception, err:
	    logger.info(err)
            students = []
	    # logger.info("exception at student")	

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

class MCQ_AssignmentDelete(DeleteView):
	model = MCQ_Assignment
	success_url = reverse_lazy("deleteview_callback")

	def get_object(self):
		pk = self.request.POST['assignmentid']
		return get_object_or_404(MCQ_Assignment, id=pk)
# ======================End of Assignment ====================


#======================================================================================================
#     ST Potion                                                                                      ==
#======================================================================================================


def _getdeadlinewarning(student, assignments,isRetake):
	for assignment in assignments:
		papers = MCQ_Paper.objects.filter(assignment=assignment)
		for paper in papers:
			questions = MCQ_Question.objects.filter(paper=paper)
			stuanswers = getTakedStuanswers(questions, student,paper,isRetake)
			anscount = sum(1 for stuanswer in stuanswers)
			if anscount != paper.ppr_total:
				yield '<p class="assignment-dueto-dialog"> %s/%s will be due.</p>'\
					% (str(assignment.asm_assignmentname), str(paper.ppr_papername))


@login_required
def mcq_student_index(request):
	## # logger.debug("student_index(%s)" % request)
	# logger.debug("mcq_student_index(_)" % request)
	sp, res = getSpByRequest(request, 'login')
	if not sp and res:
		return res
	teacher = sp.teacher
	# logger.debug("sp=%s; teacher=%s" % (sp, teacher))
	curtime = datetime.now()
	warningtime = curtime + timedelta(days=1)
	## HACK: widen delta by 1 month
	curtime = datetime.now() - timedelta(days=30)
	warningtime = datetime.now() + timedelta(days=30)
	try:
#        assignments = Assignment.objects.filter(students=sp,
#                                                deadline__lt=warningtime,
#                                                deadline__gt=curtime)
#        # logger.debug("assignments=%s; deadline__gt=%s deadline__lt=%s" % (assignments, curtime, warningtime))
        ## HACK: ignore the deadline
		assignments = MCQ_Assignment.objects.filter(asm_students=sp)
		# logger.debug("assignments=%s" % assignments)
	except:
		pass
	else:
		deadlinewarning = "".join(str for str in _getdeadlinewarning(sp, assignments,False))
		if deadlinewarning:
			warninghead = "<h6 class='assignment-dueto-dialog'>Teacher %s:</h6> " % teacher.user.username
			msg = warninghead + deadlinewarning
			messages.add_message(request, messages.SUCCESS, msg)
	return render_to_response('mcq_student_index.html', context_instance=RequestContext(request))

@login_required
def mcq_student_achod(request):
	sp, res = getSpByRequest(request, 'login')
	if not sp and res:
		return res
	teacher = sp.teacher
	return render_to_response('mcq_student_achod.html', context_instance=RequestContext(request))


@login_required
def mcq_student_getcustompapers(request):
	student, res = getSpByRequest(request, None)
	papers = MCQ_Paper.objects.filter(owner=student.user, ppr_papertype='Review')
	response = render_to_response('mcq_student_allcustompapers.json',
		                  {'paperlist': papers},
		                  context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response


def getTakedStuanswers(questionset, student,paper,isRetakes):
	try:
		if isRetakes == True:
			stuanswer_set = list(MCQ_StudentRetakeAnswer.objects.filter(srta_question=question,srta_paper=paper,
				                          srta_student=student, srta_taked=True).latest('srta_timestamp') for srta_question in questionset)
		else:
			stuanswer_set = list(MCQ_StudentAnswer.objects.filter(question=question,sta_paper=paper,
		                                  student=student, sta_taked=True).latest('timestamp') for question in questionset)
	except:
		if isRetakes == True:
			stuanswer_set = list(MCQ_StudentRetakeAnswer.objects.filter(srta_question__in=questionset,srta_paper=paper,
		                                  srta_student=student, srta_taked=True))
		else:
			stuanswer_set = list(MCQ_StudentAnswer.objects.filter(question__in=questionset,sta_paper=paper,
		                                  student=student, sta_taked=True))



		
		
	return stuanswer_set



def getStu_retake_answers(questionset, student,paper):
    try:
        stuanswer_set = list(MCQ_StudentRetakeAnswer.objects.filter(srta_question=question, srta_paper=paper,
                                                          srta_student=student).latest('timestamp') for question in questionset)
    except:
        stuanswer_set = list(MCQ_StudentRetakeAnswer.objects.filter(srta_question__in=questionset,srta_paper=paper,
                                                          srta_student=student))
    return stuanswer_set
def getStuanswers(questionset, student,paper):
    try:
        stuanswer_set = list(MCQ_StudentAnswer.objects.filter(Q(question=question),Q(sta_paper=paper),
                                                          Q(student=student)).latest('timestamp') for question in questionset)
    except:
        stuanswer_set = list(MCQ_StudentAnswer.objects.filter(Q(question__in=questionset),Q(sta_paper=paper),
                                                          Q(student=student)))
    return stuanswer_set


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
			ans = MCQ_StudentAnswer.objects.get_or_create(student=student, question=question,sta_paper=paper,
				              sta_taked=False)
		except Exception, e:
			logger.error('ERRRO IN "reinitanswer" : %s' % e)
	return mark
def __initstu_retake_answer(paper, question_set, student):
	[h, m] = paper.ppr_duration.split(':')
	duration = int(h) * 3600 + int(m) * 60
	for question in question_set:
		try:
			
			
			sa = MCQ_StudentRetakeAnswer.objects.get_or_create(srta_student=student,srta_paper=paper,
			srta_question=question, srta_taked=True)
			sa[0].srta_timeleft = duration
			sa[0].save()
		except Exception, e:
			logger.error(e)
			pass
	return duration
def __initstuanswer(paper, question_set, student):
	[h, m] = paper.ppr_duration.split(':')
	duration = int(h) * 3600 + int(m) * 60
	for question in question_set:
		try:
			sa = MCQ_StudentAnswer.objects.get_or_create(student=student,sta_paper=paper,
			question=question, sta_taked=True)
			sa[0].sta_timeleft = duration
			sa[0].save()
		except Exception, e:
			logger.error(e)
			pass
	return duration
@login_required
def mcq_student_re_takeassignment(request):
	# logger.info("i'm in re takeassignment")
	student, res = getSpByRequest(request, None)
	paperid = request.GET.get("paperid")
	retake = request.GET.get("retake")
	try:
		paper = MCQ_Paper.objects.get(id=paperid)
		questionseq = pickle.loads(str(paper.ppr_questionseq))
	except:
		paper = None
		questionseq = []
	if paper and questionseq:
		try:
			assignment = paper.assignment
		except:
			assignment = None

		#========== need to check is it re-taken, if is yes, no re-take are allowed.
		checkRetake = MCQ_StudentReTakenTracking.objects.filter(strt_assignment=assignment, strt_paper=paper,strt_student=student)
		checkRetake.delete()
		#if checkRetake :
		#	return redirect('mcq_student_index')
		#===========================================================================
		try:
			question_set = MCQ_Question.objects.filter(id__in=questionseq)
			deleteQuestion = MCQ_StudentRetakeAnswer.objects.filter(srta_question__id__in=questionseq,srta_student=student)
			deleteQuestion.delete()
			stuanswer_set = getStu_retake_answers(question_set, student,paper)
			qnameseq = list(MCQ_Question.objects.get(id=qid).qtn_name for qid in questionseq)
		except Exception, e:
			logger.error(e)
			stuanswer_set = []
			qnameseq = []
			#custom paper student can retake
		#if retake:
		#	_reinitanswer(stuanswer_set)
		#	stuanswer_set = []
		if stuanswer_set:
			# logger.info('stuanswer_set option 1')
			anscount = sum(1 for stuanswer in stuanswer_set if stuanswer.srta_taked)
			if anscount == paper.ppr_total and paper.ppr_papertype != 'Review':
				return redirect('mcq_student_index')
			else:
				# logger.debug(stuanswer_set)
				duration = stuanswer_set[0].srta_timeleft
				# logger.debug(duration)
			if duration != -1:
				__getInstallTimer(request, duration)
			else:
				duration = __initstu_retake_answer(paper, question_set, student)
				__getInstallTimer(request, duration)
		else:
			# logger.info('stuanswer_set option 2')
			duration = __initstu_retake_answer(paper, question_set, student)
			__getInstallTimer(request, duration)
		if assignment:
			## HACK: disable the deadline check
			#            if assignment.deadline < datetime.now() + timedelta(seconds=duration):
			#                return HttpResponse("Test time %s is due, you haven\'t enough time: %s"
			#                                    % (assignment.deadline, timedelta(seconds=duration)))
			pass
		

		#========== Here need to note down this assignment and paper has taken ==================
		MCQ_StudentReTakenTracking.objects.create(strt_student=student,strt_assignment=assignment,strt_paper=paper)
		#========================================================================================
	else:
		assignment = None
		qnameseq = []
		# duration has to be defined
		messages.add_message(request, messages.INFO, 'Paper not found')
	return render_to_response('mcq_student_retakeassignment.html',
		{'student': student,
		'qids': simplejson.dumps(questionseq),
		'qnames': simplejson.dumps(qnameseq),
		'paper': paper, 'assignment': assignment},
		context_instance=RequestContext(request))


@login_required
def mcq_student_takeassignment(request):
	logger.info("i'm in takeassignment")
	student, res = getSpByRequest(request, None)
	paperid = request.GET.get("paperid")
	retake = request.GET.get("retake")
	try:
		paper = MCQ_Paper.objects.get(id=paperid)
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
			question_set = MCQ_Question.objects.filter(id__in=questionseq)
			stuanswer_set = getStuanswers(question_set, student)
			qnameseq = list(MCQ_Question.objects.get(id=qid).qtn_name for qid in questionseq)
		except Exception, e:
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
		MCQ_StudentTakenTracking.objects.create(stt_student=student,stt_assignment=assignment,stt_paper=paper)
	else:
		assignment = None
		logger.info('paper not found')
		qnameseq = []
		# duration has to be defined
		messages.add_message(request, messages.INFO, 'Paper not found')
	return render_to_response('mcq_student_takeassignment.html',
		{'student': student,
		'qids': simplejson.dumps(questionseq),
		'qnames': simplejson.dumps(qnameseq),
		'paper': paper, 'assignment': assignment},
		context_instance=RequestContext(request))




@login_required
def mcq_stu_question_get(request):
	logger.info("mcq_stu_question_get")
	student, res = getSpByRequest(request, None)
	response_data = {'state': 'failure'}
	str_optionlist = ""
	if request.method == 'POST':
		questionid = request.POST.get("questionid")
		paperid = request.POST.get("paperid")
		## logger.info("xxxxx===========questionid:%s" % questionid)
		if questionid and questionid != '-1':
			try:
				#logger.info('questionid: %s ' % questionid)
				question = MCQ_Question.objects.get(id=int(questionid))
				paper = MCQ_Paper.objects.get(id=int(paperid))
				logger.info("===============================================")
				logger.info("question = %s" % question)
				logger.info("===============================================")
				try:
					# logger.info('ok..going to get value liao 1' )
					studentAnswer = MCQ_StudentAnswer.objects.get(Q(sta_paper=paper),Q(question=question),Q(student=student),~Q(optionlist = None))
					# logger.info('ok..going to get value liao 2s')
				except ObjectDoesNotExist:
					logger.info('try to get studentanswer, but not found')
					studentAnswer = None
				# logger.info("question %s" % question)
				response_data['question_desc'] = question.qtn_description
				if question.qtn_questioncategory != None:
					response_data['question_questioncategory'] = question.qtn_questioncategory.id
				else:
					response_data['question_questioncategory'] = ""
				response_data['question_content'] = question.qty_html
				lst_optionlist = MCQ_Optionlist.objects.filter(opl_question=question)
				logger.info("===============================================")
				logger.info("lst_optionlist = %s" % lst_optionlist)
				logger.info("===============================================")
				#lst_randompick = lst_optionlist[random.randrange(len(lst_optionlist))]
				lst_randompick = lst_optionlist
				loopValue = 0
				for objOption in lst_randompick:
					strCheck=""
					strFieldValue="optionlist_option" + ("%s" % loopValue)
					strCanvasValue="optionlist_canvas" + ("%s" % loopValue)
					strDiagramValue="optionlist_diagram" + ("%s" % loopValue)
					strThumbnailsValue="optionlist_thumbnails" + ("%s" % loopValue)
					try:
						lst_Optionimage =  MCQ_OptionImage.objects.filter(Q(option=objOption),~Q(qti_description = "del"))
					except:
						lst_Optionimage=None
					#========== Generate Picture list =====================
					strThumbnailLayout=""
					
					if lst_Optionimage != None:
						for objOptionimage in lst_Optionimage:
							strImageName=objOptionimage.qti_imagename[:4] + "..."
							strImageURL= "/static/%s/%s" % (settings.UPLOADPREFIX, objOptionimage.qti_abspath) 
							logger.info('strImageURL: %s ' % strImageURL) 
							strThumbnailLayout = strThumbnailLayout + '<li class="ui-widget-content ui-corner-tr"><h6 class="ui-widget-header">' + strImageName + '</h6><img src="' + strImageURL + '" id="' + ("%s" % objOption.id) + '" alt="' + objOptionimage.qti_imagename + '" width="96" height="72"><a href="#" title="View larger Image" class="ui-icon ui-icon-zoomin">View Larger</a></li>'
						
					#========== End of Generate Picture list ==============	
					if studentAnswer != None:
						strCheck=" disabled "
						
						if studentAnswer.optionlist.id == objOption.id:
							strCheck= strCheck + " checked "
					str_button_URL = '/mcq/optioncanvas/?canvasname=1&optionid=' + str(objOption.id)  ;
					str_button_class= 'nyroModal populate greenBtn';
					strDiagramOption = '<h4 class="ui-widget-header" id="thumbnails_header">Option Diagrams</h4> <div id="' + strThumbnailsValue + '" class=" specialpicture ui-widget-content ui-state-default" style="height:165px;overflow:auto;"> <ul id="' + strDiagramValue + '" class=" gallery ui-helper-reset ui-helper-clearfix">' + strThumbnailLayout + ' </ul></div>'
					#========= Canvas option ==========================						
					strCanvasOption = ' <a id="' + strCanvasValue + '"   style="width: 43px; height: 15px;" class="Graphic  ' + str_button_class + '" href="' + str_button_URL + '" target="_blank">Graph</a>'
					#========= end of Canvas option ===================
					strTempOption = '<div class="optionlist"><table><tr><td> <input ' + strCheck + ' name="question_multiselection_option"  id="question_multiselection_option" type="radio" onchange="onChangedOptionList(' + questionid + ',' + str(objOption.id) + ')"' +  ' value="' + str(objOption.id) + '">Select <textarea id="' + strFieldValue + '" name="' + strFieldValue + '">' + objOption.opl_option + "</textarea> </input></td><td><table><tr><td>" + strCanvasOption + "</td></tr><tr><td>" + strDiagramOption + "</td></tr></table></td></tr></table></div>"
					if str_optionlist == "":
						str_optionlist = strTempOption
					else:
						str_optionlist =  str_optionlist + '<br/>' + strTempOption
					loopValue = loopValue + 1	
				## logger.info('this is  the lst_optionlist ============= %s' % str_optionlist)
				response_data['question_multiselection'] = str_optionlist
			except Exception , e:
				# logger.error('is here')
				logger.error(e)
				pass
			try:
				# logger.info('test 1')
				stuanswer = MCQ_StudentAnswer.objects.filter(question=question,sta_paper=paper,
					student=student)
				# logger.info('test 2')
				html_answer = "ned to change to option list id"
			except Exception, e:
				# logger.error('get student answer, i shouldnt in here: %s' % e)
				logger.error(e)
				pass
			else:
				# logger.info('test 3')
				#response_data['question_canvas'] = __getstucanvas(question, stuanswer)
				response_data['question_stuanswer'] = html_answer
				# logger.info('test 4')
				
				response_data['stuanswerid'] = '0'
				# logger.info('test 5')
				response_data['state'] = 'success'
				# logger.info('test 6')
	return HttpResponse(json.dumps(response_data), mimetype="application/json")
@login_required
def mcq_stu_retake_question_get(request):
	logger.info("mcq_stu_question_get")
	student, res = getSpByRequest(request, None)
	response_data = {'state': 'failure'}
	str_optionlist = ""
	if request.method == 'POST':
		questionid = request.POST.get("questionid")
		paperid = request.POST.get("paperid")
		## logger.info("xxxxx===========questionid:%s" % questionid)
		if questionid and questionid != '-1':
			try:
				question = MCQ_Question.objects.get(id=int(questionid))
				paper = MCQ_Paper.objects.get(id=int(paperid))
				logger.info("===============================================")
				logger.info("question = %s" % question)
				logger.info("===============================================")
				try:
					# logger.info('ok..going to get value liao 1' )
					studentAnswer = MCQ_StudentRetakeAnswer.objects.get(Q(srta_paper=paper),Q(srta_question=question),Q(srta_student=student),~Q(srta_optionlist = None))
					# logger.info('ok..going to get value liao 2s')
				except ObjectDoesNotExist:
					logger.info('try to get studentanswer, but not found')
					studentAnswer = None
				# logger.info("question %s" % question)
				response_data['question_desc'] = question.qtn_description
				if question.qtn_questioncategory != None:
					response_data['question_questioncategory'] = question.qtn_questioncategory.id
				else:
					response_data['question_questioncategory'] = ""
				response_data['question_content'] = question.qty_html
				lst_optionlist = MCQ_Optionlist.objects.filter(opl_question=question)
				logger.info("===============================================")
				logger.info("lst_optionlist = %s" % lst_optionlist)
				logger.info("===============================================")
				#lst_randompick = lst_optionlist[random.randrange(len(lst_optionlist))]
				lst_randompick = lst_optionlist
				loopValue = 0
				for objOption in lst_randompick:
					strCheck=""
					strFieldValue="optionlist_option" + ("%s" % loopValue)
					strCanvasValue="optionlist_canvas" + ("%s" % loopValue)
					strDiagramValue="optionlist_diagram" + ("%s" % loopValue)
					strThumbnailsValue="optionlist_thumbnails" + ("%s" % loopValue)
					try:
						lst_Optionimage =  MCQ_OptionImage.objects.filter(Q(option=objOption),~Q(qti_description = "del"))
					except:
						lst_Optionimage=None
					#========== Generate Picture list =====================
					strThumbnailLayout=""
					
					if lst_Optionimage != None:
						for objOptionimage in lst_Optionimage:
							strImageName=objOptionimage.qti_imagename[:4] + "..."
							strThumbnailLayout = strThumbnailLayout + '<li class="ui-widget-content ui-corner-tr"><h6 class="ui-widget-header">' + strImageName + '</h6><img src="' + "/static/%s/%s" % (settings.UPLOADPREFIX, objOptionimage.qti_abspath) + '" id="' + ("%s" % objOption.id) + '" alt="' + objOptionimage.qti_imagename + '" width="96" height="72"><a href="#" title="View larger Image" class="ui-icon ui-icon-zoomin">View Larger</a></li>'
						
					#========== End of Generate Picture list ==============	
					if studentAnswer != None:
						strCheck=" disabled "
						
						if studentAnswer.srta_optionlist.id == objOption.id:
							strCheck= strCheck + " checked "
					str_button_URL = '/mcq/optioncanvas/?canvasname=1&optionid=' + str(objOption.id)  ;
					str_button_class= 'nyroModal populate greenBtn';
					strDiagramOption = '<h4 class="ui-widget-header" id="thumbnails_header">Option Diagrams</h4> <div id="' + strThumbnailsValue + '" class="specialpicture ui-widget-content ui-state-default" style="height:165px;overflow:auto;"> <ul id="' + strDiagramValue + '" class="gallery ui-helper-reset ui-helper-clearfix">' + strThumbnailLayout + ' </ul></div>'
					#========= Canvas option ==========================						
					strCanvasOption = ' <a id="' + strCanvasValue + '"   style="width: 43px; height: 15px;" class="Graphic  ' + str_button_class + '" href="' + str_button_URL + '" target="_blank">Graph</a>'
					#========= end of Canvas option ===================
					strTempOption = '<div class="optionlist"><table><tr><td> <input ' + strCheck + ' name="question_multiselection_option"  id="question_multiselection_option" type="radio" onchange="onChangedOptionList(' + questionid + ',' + str(objOption.id) + ')"' +  ' value="' + str(objOption.id) + '">Select <textarea id="' + strFieldValue + '" name="' + strFieldValue + '">' + objOption.opl_option + "</textarea> </input></td><td><table><tr><td>" + strCanvasOption + "</td></tr><tr><td>" + strDiagramOption + "</td></tr></table></td></tr></table></div>"
					if str_optionlist == "":
						str_optionlist = strTempOption
					else:
						str_optionlist =  str_optionlist + '<br/>' + strTempOption
					loopValue = loopValue + 1	
				## logger.info('this is  the lst_optionlist ============= %s' % str_optionlist)
				response_data['question_multiselection'] = str_optionlist
			except Exception , e:
				# logger.error('is here')
				logger.error(e)
				pass
			try:
				# logger.info('test 1')
				stuanswer = MCQ_StudentRetakeAnswer.objects.filter(srta_question=question,srta_paper = paper,
					srta_student=student)
				# logger.info('test 2')
				html_answer = "ned to change to option list id"
			except Exception, e:
				# logger.error('get student answer, i shouldnt in here: %s' % e)
				logger.error(e)
				pass
			else:
				# logger.info('test 3')
				#response_data['question_canvas'] = __getstucanvas(question, stuanswer)
				response_data['question_stuanswer'] = html_answer
				# logger.info('test 4')
				
				response_data['stuanswerid'] = '0'
				# logger.info('test 5')
				response_data['state'] = 'success'
				# logger.info('test 6')
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required
def mcq_student_selectedoption_retakepaper(request):
	student, res = getSpByRequest(request, None)
	response_data = {'state': 'failure'}
	# logger.info("ok test1")
	str_optionlist = ""
	if request.method == 'POST':
		questionid = request.POST.get("questionid")
		paperid = request.POST.get("paperid")  # MH16010001
		obj_paper = MCQ_Paper.objects.get(id=int(paperid))  # MH16010001
		optionid = request.POST.get("optionID")
		obj_question = MCQ_Question.objects.get(id=int(questionid))
		obj_optionlist = MCQ_Optionlist.objects.get(id=int(optionid))
		try:
			# logger.info("ok test1")
			#check_isit_studentanswered = MCQ_StudentRetakeAnswer.objects.get(srta_question=obj_question ,srta_paper=obj_paper , srta_optionlist=None,srta_student=student) # MH16010001
			check_isit_studentanswered = MCQ_StudentRetakeAnswer.objects.get(srta_question=obj_question ,srta_paper=obj_paper , srta_student=student) # MH16010001
		except Exception , e:
			
			# logger.info("ERROR LOL: %s " % e)
			response_data['message'] = "Question has been answered by you."
			pass
		else:
			check_isit_studentanswered.srta_taked = str2bool("True")
			check_isit_studentanswered.srta_optionlist = obj_optionlist
			# logger.info("obj_optionlist.opl_iscorrect: %s" % obj_optionlist.opl_iscorrect)
			if obj_optionlist.opl_iscorrect:
				# logger.info("obj_question.qtn_mark: %s" % obj_question.qtn_mark)
				check_isit_studentanswered.srta_mark = obj_question.qtn_mark
			check_isit_studentanswered.save()
			response_data = {'state': 'success'}
			#messages.add_message(request, messages.SUCCESS, "You missed some values")
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required
def mcq_student_selectedoption(request):
	student, res = getSpByRequest(request, None)
	response_data = {'state': 'failure'}
	logger.info("ok test1")
	str_optionlist = ""
	if request.method == 'POST':		
		logger.info("post pos 1")
		questionid = request.POST.get("questionid") 
		paperid = request.POST.get("paperid")  # MH16010001
		optionid = request.POST.get("optionID")

		obj_question = MCQ_Question.objects.get(id=int(questionid))
		obj_paper = MCQ_Paper.objects.get(id=int(paperid))  # MH16010001
		obj_optionlist = MCQ_Optionlist.objects.get(id=int(optionid))
		try:
			logger.info("ok test1")
			#check_isit_studentanswered = MCQ_StudentAnswer.objects.get(question=obj_question ,sta_paper=obj_paper , optionlist=None,student=student) # MH16010001
			check_isit_studentanswered = MCQ_StudentAnswer.objects.get(question=obj_question ,sta_paper=obj_paper , student=student) # MH16010001
			logger.info("ok test2")
		except Exception , e:
			
			logger.info("ok test3")
			logger.info("ERROR LOL: %s " % e)
			response_data['message'] = "Question has been answered by you."
			pass
		else:
			#logger.info("ok test4")
			#try:
			#	logger.debug('testing')
			#	thumbnail_ids = [int(i) for i in request.POST['stuthumbnail_ids'].split(',') if i]
			#	logger.debug(' thumbnail_ids@@@@@@@@@ = %s' %  thumbnail_ids)
			#except Exception , e:
			thumbnail_ids = []
			#	logger.debug("no img for question %s" % question)
			#	pass
			#stdanswer algorithm to mark stuanswer
			logger.info("ok test2")
			try:
				logger.info("thumbnail_ids: %s" % thumbnail_ids)
				#stuansimages = __getimgmark(thumbnail_ids, obj_question)
			except Exception , e:
				logger.info("error: %s " % e) 
			try:
				logger.info("test 1")
				check_isit_studentanswered.sta_taked = str2bool("True")
				logger.info("test 2")
				check_isit_studentanswered.optionlist = obj_optionlist
				logger.info("test 3")
				#check_isit_studentanswered.stuansimages = None
				logger.info("test 4")
				if obj_optionlist.opl_iscorrect:
					check_isit_studentanswered.sta_mark = obj_question.qtn_mark
				check_isit_studentanswered.save()
				response_data = {'state': 'success'}
			except Exception , e:
				logger.info("error: %s " % e) 
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

def __getimgmark(thumbnail_ids, question):
    """getthumbnails of studentanswer image"""
    if not thumbnail_ids:
	return 0, []
    try:
	#stdanswer = question.stdanswer
	stuansimages = MCQ_QuestionImage.objects.filter(id__in=thumbnail_ids)
	#imagepointlist = pickle.loads(str(question.imagepointlist))
    except Exception, e:
	print "expppppppp", e
	logger.error(e)
	return 0, []
    #else:
	#stuanspoints = list([imagepoint, stuansimage]
	#                    for imagepoint in imagepointlist
	#                    for stuansimage in stuansimages
	#                    if imagepoint['Point_Text'] == stuansimage.qti_digest)
	#stuansimages = list(image for imagepoint, image in stuanspoints)
	#logger.debug(stuanspoints)

    #try:
	#imgrulelist = _loadlist(stdanswer.imgrulelist)
    #except Exception, e:
	#logger.error(e)
    #imgmark = None
    #if stuanspoints and imgrulelist:
	#imgans = ImageAnswer()
	#imgmark, imgpointlist, imgomitted = imgans.Analysis(stuanspoints, imagepointlist, imgrulelist)
	#logger.debug("imgmark:%d" % imgmark)
    #return imgmark, stuansimages
    return  stuansimages



def _loadlist(list):
    if list:
        return pickle.loads(str(list))
    else:
        return None
@login_required
def mcq_student_papersummarize(request):
	student, res = getSpByRequest(request, 'login')
	if not student and res:
		return res
	paperid = request.GET.get('paperid')
	passed = request.GET.get('passed')
	try:
		paper = MCQ_Paper.objects.get(id=paperid)
		questionseq = pickle.loads(str(paper.ppr_questionseq))
	except:
		return HttpResponse("paper does not exist")
	if paper and questionseq:
		question_set = MCQ_Question.objects.filter(id__in=questionseq)
		stuanswer_set = getStuanswers(question_set, student,paper)
		# logger.info('you result "pass" is equal to "%s"' % passed)
		mark = sum(ans.sta_mark for ans in stuanswer_set)
	else:
		mark = 0
	return render_to_response('mcq_student_assignmentsummarize.html',
		{'paper': paper,
		'mark': mark},
		context_instance=RequestContext(request))


@login_required
def mcq_student_retakepapersummarize(request):
	student, res = getSpByRequest(request, 'login')
	if not student and res:
		return res
	paperid = request.GET.get('paperid')
	passed = request.GET.get('passed')
	try:
		paper = MCQ_Paper.objects.get(id=paperid)
		questionseq = pickle.loads(str(paper.ppr_questionseq))
	except:
		return HttpResponse("paper does not exist")
	if paper and questionseq:
		question_set = MCQ_Question.objects.filter(id__in=questionseq)
		stuanswer_set = getStu_retake_answers(question_set, student,paper)
		# logger.info('you result "pass" is equal to "%s"' % passed)
		mark = sum(ans.srta_mark for ans in stuanswer_set)
	else:
		mark = 0
	return render_to_response('mcq_student_assignmentretakesummarize.html',
		{'paper': paper,
		'mark': mark},
		context_instance=RequestContext(request))

#=============================== REPORT=========================================================================

@permission_required('auth.add_user')
def mcq_report_teacher(request):
	group = getGroupNameByRequest(request)
	if group != 'teachers':
		return redirect('teacher_index')
	form = MCQ_PaperSearchForm()
	if request.method == 'POST':
		pids = request.POST.get('paperids')
		return render_to_response('mcq_report_paper.html',
			{'form': form, 'pids': pids, 'group': group },
			context_instance=RequestContext(request))
	else:
		return render_to_response('mcq_report_teacher.html',
			{'form': form},
			context_instance=RequestContext(request))


@login_required
def mcq_report_student(request):
	group = getGroupNameByRequest(request)
	if group != 'students':
		logger.info('redirect to mcq_student_index')
		return redirect('mcq_student_index')
	form = MCQ_PaperSearchForm()
	logger.info('use mcq_report_paper.html')
	return render_to_response('mcq_report_paper.html',
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
        print paperids,"paperids paperids"
        pids = []
        stuids = []
        if paperids:
	    logger.info('enter zone 1')
            try:
		logger.info('this is all paperids: %s' % paperids)
                paper_stu = re.findall(r'\{pid\:(\d+)\,\sstuid\:(\d+)\}', paperids)
		logger.info('this is all paper_stu: %s' % paper_stu)
            except Exception, e:
                logger.error(e)
            for pid, stuid in paper_stu:
		logger.info('this is each id : %s ' % pid)
                pids.append(int(pid))
                stuids.append(int(stuid))
	    # logger.info('ok...going in MCQ_DetailSearchForm')
            form = MCQ_DetailSearchForm(paper=pids, student=stuids)
	    # logger.info('ok...safety landed MCQ_DetailSearchForm')
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
                form = MCQ_DetailSearchForm(request.POST, paper=pids, student=stuids)
            except Exception, e:
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
                except Exception, e:
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



def __studentmarkreport(student):
	takedpaperlist = []
	try:
		lst_assignments = MCQ_Assignment.objects.filter(asm_students=student)
		lst_papers = MCQ_Paper.objects.filter(assignment__in=lst_assignments).distinct()
		logger.info( ' check all lst_papers %s ' % lst_papers)
	except Exception , E:
		logger.info(' exception studentmarkreport %s ' % E)
		lst_papers = []

	for p in lst_papers:
		question_set = MCQ_Question.objects.filter(paper=p)
		stuanswer_set = getTakedStuanswers(question_set, student,p,False)
		if stuanswer_set:
			mark = sum(ans.sta_mark for ans in stuanswer_set)
			closeness = sum(ans.sta_closeness if ans.sta_closeness else 0.0 for ans in stuanswer_set)
			closeness /= float(len(stuanswer_set))
			takedpaperlist.append([p, student, mark, closeness])
	return takedpaperlist


@login_required
def mcq_stu_question_thumbnails(request):
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
		logger.info('debug1')
                question = MCQ_Question.objects.get(id=int(questionid))
                stuanswer = MCQ_StudentAnswer.objects.filter(question=question,
                                                         student=student).latest('sta_timestamp')
            except Exception , e:
		logger.info('debug2 %s ' % e)
                stuanswer = None
                thumbnails = MCQ_QuestionImage.objects.filter(question=question,
                                                          qti_iscorrect=False)\
                    .exclude(qti_description="del")
                stuthumbnails = None
            else:
		try:
		        stuthumbnails = stuanswer.stuansimages.all()
			logger.info('going to get stuthumbnails %s' % stuthumbnails)
		        studigests = list(st.qti_digest for st in stuthumbnails)
		        thumbnails = MCQ_QuestionImage.objects.filter(question=question,
		                                                  qti_iscorrect=False)\
		            .exclude(qti_description="del")\
		            .exclude(qti_digest__in=studigests)
		except Exception , e:
			logger.debug('ok ..error here %s ' % e)
            logger.info("question %s, thumbnails%s" % (question, thumbnails))
                #[0] thumb,[1] imagename,[2] orig image
            if thumbnails:
                response_data['thumbnails'] = list(["%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                                    t.qti_imagename,
                                                    "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                                    t.id] for t in thumbnails)
            if stuthumbnails:
                response_data['stuthumbnails'] = list(["%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                                      t.qti_imagename,
                                                      "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                                      t.id] for t in stuthumbnails)

		logger.info('test response data stuthumbnails %s ' % response_data['stuthumbnails'])
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required
def mcq_report_thumbnails(request):
	response_data = {'state': 'failure'}
	logger.info("report question thumbnails with method: %s" % request.method)
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
				question = MCQ_Question.objects.get(id=int(questionid))
				stuanswer = MCQ_StudentAnswer.objects.filter(question=question,
					student=student).latest('sta_timestamp')
			except Exception, e:
				logger.error(e)
				pass
			else:
				logger.info('ok la...i got here liao!!!!!!!')
				response_data = __getReportThumbnails(question, stuanswer)
	return HttpResponse(json.dumps(response_data), mimetype="application/json")

def __getReportThumbnails(question, stuanswer):
    logger.info('###################start test ################################################')
    logger.info("question %s ============ stuanswer : %s" % (question, stuanswer))
    logger.info('###################end test#######################################')
    response_data = {'state': 'failure'}
    try:
        questionthumbnails = MCQ_QuestionImage.objects.filter(question=question).exclude(qti_description="del")
	#===== Get the corret option for particular question first ======================
	lst_correct_optionlist = MCQ_Optionlist.objects.filter(opl_question=question)
	correct_optionlist = lst_correct_optionlist[0]	if lst_correct_optionlist != None else None
        #stdthumbnails = MCQ_QuestionImage.objects.filter(question=question, qti_iscorrect=True).exclude(qti_description="del")
	stdthumbnails=MCQ_OptionImage.objects.filter(option=correct_optionlist).exclude(qti_description="del")
        stuthumbnails = MCQ_OptionImage.objects.filter(option=stuanswer.optionlist).exclude(qti_description="del")
	logger.info('stuanswer : %s' % stuanswer)
	logger.info('=====================================================')
	logger.info('questionthumbnails %s' % questionthumbnails)
	logger.info('=====================================================')
	logger.info('stdthum %s' % stdthumbnails)
	logger.info('=====================================================')
	logger.info('stuthum %s' % stuthumbnails if stuthumbnails != None else "is Empty")
	logger.info('=====================================================')
    except Exception , e:
	logger.error(e)
        pass
    else:
        response_data['questionthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.qti_abspath),
                                                    t.qti_imagename,
                                                    "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                                    t.id]
                                                   for t in questionthumbnails)
        response_data['stuthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.qti_abspath),
                                               t.qti_imagename,
                                               "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                               t.id]
                                              for t in stuthumbnails)
        response_data['stdthumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.qti_abspath),
                                               t.qti_imagename,
                                               "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
                                               t.id]
                                              for t in stdthumbnails)
	logger.info(' response data stdthumbnails : %s' % response_data['stdthumbnails'] )
        response_data['state'] = 'success'
    return response_data
@login_required
def mcq_question_getstureport(request):
    logger.debug("in question_getstureport")
    # note: Used for student report (see report_studentanswer.html and report_reviewquestion.js)
    response_data = {'state': 'failure'}
    stuid = request.POST.get('studentid')
    qid = request.POST.get('questionid')
    pid = request.POST.get('paperid')
    isRetake = request.POST.get('isRetake')
    b_student_has_answer = False
    d_total_mark = 0

    response_data['optionid_stdanswer'] = 0
    response_data['optionid_stuanswer'] = 0
    stuanswer = None
    try:
        question = MCQ_Question.objects.get(id=qid)
        paper = MCQ_Paper.objects.get(id=int(pid))
	try:
		optionlist_stdanswer= MCQ_Optionlist.objects.filter(opl_question=question, opl_iscorrect=True)[0]
		if optionlist_stdanswer != None:
			stdanswer = optionlist_stdanswer.opl_option
			response_data['optionid_stdanswer'] = optionlist_stdanswer.id
		else:
			stdanswer = ""
	except Exception , e:
		logger.info('exception %s' % e)
	 	optionlist_stdanswer= None
		stdanswer = ""	
        stdcanvaslist = [] #Canvas.objects.filter(question=question, stdanswer=stdanswer, stuanswer=None)
        student = SProfile.objects.get(user__id=stuid)
	try:
		if isRetake == True:
			stuanswer = MCQ_StudentRetakeAnswer.objects.filter(srta_question=question, srta_paper = paper,
		                                         srta_student=student, srta_taked=True).latest('srta_timestamp')
		else:
			stuanswer = MCQ_StudentAnswer.objects.filter(question=question, sta_paper = paper,
		                                         student=student, sta_taked=True).latest('sta_timestamp')
			
		b_student_has_answer = True
	except: 
		pass
        stucanvaslist = [] #Canvas.objects.filter(question=question, stuanswer=stuanswer, stdanswer=None)
	
    except Exception, e:
	
        logger.error(e)
    else: 
	logger.info("============================== test v1 ========================")
        response_data['canvas'] = {
            'stucanvas': [[stuanswer.id if b_student_has_answer else 0, stucanvas.name] for stucanvas in stucanvaslist],
            'stdcanvas': [[stdanswer.id if b_student_has_answer  else 0, stdcanvas.name] for stdcanvas in stdcanvaslist]
        }
        response_data['stuname'] = student.user.username
	response_data['stdanswer'] = stdanswer
	if isRetake == True:
        	response_data['mark'] = stuanswer.srta_mark if b_student_has_answer  else ""
	else:
		response_data['mark'] = stuanswer.sta_mark if b_student_has_answer  else ""
        response_data['question'] = question.qty_html
	str_stuanswer = ""
	if stuanswer != None:
		if isRetake == True:
			if stuanswer.srta_optionlist != None:
				str_stuanswer = stuanswer.srta_optionlist.opl_option
				response_data['optionid_stuanswer'] =  stuanswer.srta_optionlist.id
		else:
			if stuanswer.optionlist != None:
				str_stuanswer = stuanswer.optionlist.opl_option
				response_data['optionid_stuanswer'] =  stuanswer.optionlist.id
		
        response_data['stuanswer'] = stripBody(str_stuanswer)
        response_data['grammar_issues'] = ""
        # The closeness score is in range [0, 1] and is converted into a percentage with 10 bands,
        # defined as 0-10%, 11-20%, ..., 91-100%.
        closeness = 0
        closeness_band = 0
	if isRetake == True:
		if stuanswer.srta_closeness if b_student_has_answer else False:
			closeness = round(stuanswer.srta_closeness * 100, 1)
			closeness_band = 1 + int(stuanswer.srta_closeness * NUM_CLOSENESS_BANDS)
			closeness_band = max(1, min(closeness_band, NUM_CLOSENESS_BANDS))
	else:
		if stuanswer.sta_closeness if b_student_has_answer else False:
			closeness = round(stuanswer.sta_closeness * 100, 1)
			closeness_band = 1 + int(stuanswer.sta_closeness * NUM_CLOSENESS_BANDS)
			closeness_band = max(1, min(closeness_band, NUM_CLOSENESS_BANDS))
		
        
        response_data['closeness'] = closeness
        response_data['closeness_band'] = closeness_band
        response_data['num_closeness_bands'] = NUM_CLOSENESS_BANDS
	
        try:
		if isRetake == True:
			response_data['pointmarklist'] = pickle.loads(str(stuanswer.srta_pointmarklist))
		else:
			response_data['pointmarklist'] = pickle.loads(str(stuanswer.sta_pointmarklist))
        except Exception, e:
            logger.error(e)
            response_data['pointmarklist'] = [] 
	response_data['omitted'] = ''
        response_data['state'] = 'success'


    try:
    	mark_paper = MCQ_Paper.objects.get(id=pid)
    	mark_questionseq = pickle.loads(str(mark_paper.ppr_questionseq))
    	mark_question_set = MCQ_Question.objects.filter(id__in=mark_questionseq)
    	stuanswer_set = getStuanswers(mark_question_set, student,paper) 
    	d_total_mark = sum(ans.sta_mark for ans in stuanswer_set)
    except Exception, e:
    	logger.info('errro %s ' % e)
    logger.info('total mark %s ' % d_total_mark)
    response_data['total_mark'] = d_total_mark
        #logger.debug("question_getstureport: response_data=%s" % response_data)
    #logger.debug("out question_getstureport")
    return HttpResponse(json.dumps(response_data), mimetype="application/json")




@login_required
def mcq_feedback_popup(request, pid, stuid):
	group = getGroupNameByRequest(request)
	qid = request.GET.get("question_id")
	if group != 'students':
		logger.info("mcq_feedback_popup: if statement start") 
		paper = MCQ_Paper.objects.get(id = pid)
		s_profile = SProfile.objects.get(user=stuid)
		fb, s = MCQ_StudentAnswer.objects.get_or_create(
			question = qid,
			student = s_profile,
			sta_paper = paper
			)
		logger.info("mcq_feedback_popup: if statement done") 
		if request.method == 'POST':
			print "post method calling"
			form = MCQ_FeedbackForm(request.POST)

			if form.is_valid():
				fback = request.POST['Add_Feedback']
				fb_code = request.POST['Add_Feedback_Code']
				fb.sta_feedback = fback
				fb.sta_feedback_code = fb_code
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
		logger.info("mcq_feedback_popup: get form feedback start ") 
		form = MCQ_FeedbackForm()           
		logger.info("mcq_feedback_popup: get form feedback end") 
		return render_to_response('mcq_fb_popup.html',
				{'form':form, 'pid':pid, 'stuid': stuid,'fb':fb, 'qid':qid },
				context_instance=RequestContext(request)
			)

	else:
		logger.info("mcq_feedback_popup: else statement") 
		"""
		The else part is user for show the student report and able to print
		that report """
		qset = []
		student = request.user
		paper = MCQ_Paper.objects.get(id = pid)
		questionseq = pickle.loads(str(paper.ppr_questionseq)) #question sequence are added into this part
		for q in questionseq:
			qset.append(MCQ_Question.objects.get(id = q))
		stuanswer_set = getTakedStuanswers(qset, student,paper, False)
		total_mark = 0
		stud_mark = 0
		print stuanswer_set
		lst_allanswer  = [];
		for q in stuanswer_set:
			answer_is_correct = "N"
			total_mark = total_mark + q.sta_mark
			stud_mark = stud_mark + q.sta_mark
			strActualAnswer = ""
			logger.info('testing going in')
			try:
				 
				actualAnswer = MCQ_Optionlist.objects.filter(opl_question=q.question , opl_iscorrect = True)
				
				logger.info(" actualAnswer ....: %s" % actualAnswer)
				if actualAnswer != None:
					for actualAnswer_row in actualAnswer:
						if strActualAnswer == "":
							strActualAnswer = "- " + actualAnswer_row.opl_option
						else:	
							strActualAnswer = strActualAnswer + "<br/>" + "- " + actualAnswer_row.opl_option
						
						
						if q.optionlist.id == actualAnswer_row.id :
							answer_is_correct = "Y"
					
			except Exception , e:
				logger.debug("eception here %s " % e)
				actualAnswer = None
			try:
				lst_allanswer.append({'question': q.question.qtn_name + " - " +  q.question.qtn_description , 'student_answer': q.optionlist.opl_option ,'actual_answer':strActualAnswer ,'correct':answer_is_correct, 'mark':  q.sta_mark , 'feedback':q.sta_feedback , 'feedback_code':q.sta_feedback_code})
			except Exception, e:
				logger.debug(e)
		return render_to_response('mcq_report_feedback_report.html',
				{'user':student,'paper':paper,'stu':stuanswer_set, 'lst_allanswer':lst_allanswer,
				'sum':total_mark,'smark':stud_mark,
				'print': True if request.is_ajax() else False,'len':len(questionseq),
			})




        
@login_required
def mcq_student_retake_checktime(request):
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
            p = MCQ_Paper.objects.get(id=paperid)
            question_set = MCQ_Question.objects.filter(paper=p)
            stuanswer_set = getStu_retake_answers(question_set, student,p)
            logger.debug("stuanswer len: %s" % len(stuanswer_set))
            for stuanswer in stuanswer_set:
                timeleft = stuanswer.srta_timeleft
                stuanswer.srta_timeleft = timeleft - (curtime - starttime).seconds
                stuanswer.save()
        except Exception, e:
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
def mcq_student_checktime(request):
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
            p = MCQ_Paper.objects.get(id=paperid)
            question_set = MCQ_Question.objects.filter(paper=p)
            stuanswer_set = getStuanswers(question_set, student)
            logger.debug("stuanswer len: %s" % len(stuanswer_set))
            for stuanswer in stuanswer_set:
                timeleft = stuanswer.sta_timeleft
                stuanswer.sta_timeleft = timeleft - (curtime - starttime).seconds
                stuanswer.save()
        except Exception, e:
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
def MCQ_student_getretakepapers(request):
	response = {'status':'failure'}
	try:
		retake_assignment_list = []
		student, res = getSpByRequest(request, None)
		teacher = student.teacher
	except:
		student, res = None, None
	else:
		# need to know what kind of assignment has been assigned 
		# for the particular student.
		lst_retakeassignment = MCQ_StudentReTakenTracking.objects.filter(strt_student=student).order_by('-strt_timestamp')
		logger.info('lst_retakeassignment: =====> %s ' % lst_retakeassignment)
		for rowReTakeAssignment in lst_retakeassignment:
			strView="<a href='/mcq/student/retakesummarize/?paperid=%s'><font color=black>View</font></a>" % str(rowReTakeAssignment.strt_paper.id)
			retake_assignment_list.append([rowReTakeAssignment.strt_assignment,  rowReTakeAssignment.strt_paper,strView])
		
		logger.info('retake_assignment_list: =====> %s ' % retake_assignment_list)
	response['Cache-Control'] = 'no-cache'
	response = render_to_response('mcq_student_allretakeassignment.json',
			{'retake_assignment_list': retake_assignment_list },
			context_instance=RequestContext(request))
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Cache-Control'] = 'no-cache'
	return response



def _getassignmentjson(assignments, teacher, student):
	assignment_list = []
	
	for a in assignments:
		answered_wrong_answer_count = 0
		papers = MCQ_Paper.objects.filter(assignment=a, owner=teacher.user)
		# logger.info('miao...found papers: %s' % papers)
		for p in papers:
			try:
				questionseq = pickle.loads(str(p.ppr_questionseq))
				question_set = MCQ_Question.objects.filter(id__in=questionseq)
				stuanswer_set = getStuanswers(question_set, student,p)
				count = sum(1 for sa2 in stuanswer_set if sa2.sta_taked)
				count_isExist = sum(1 for sa1 in stuanswer_set if sa1.sta_taked == True or sa1.sta_taked == False)
				# If contain incorrect answer then allowed to redo, but only once. therefore, once this button 
				# is clicked. then this paper can not redo any more for this student.
				if count != 0:	
					answered_wrong_answer_count = sum(1 for sa in stuanswer_set if sa.optionlist != None if sa.optionlist.opl_iscorrect==False)
						
				# logger.info('after miao ... this is the number %s' % count)
				
			except Exception, e:
				logger.error(e)
				# logger.error(a)
				# logger.error(p)
				break
			# logger.info('miao finsihed for ppr_total: %s' % p.ppr_total)
			str_btn_retake = ""
			str_btn_take = ""
			try:
				trackingassignment = MCQ_StudentTakenTracking.objects.get(stt_assignment=a,stt_paper=p,stt_student=student)
				logger.info('found trackingassignment: %s' % trackingassignment)
			except:
				logger.info('not found trackingassignment')
				str_btn_retake = "<a href='/mcq/student/takeassignment/?paperid=%s'><font color=black>Take</font></a>&nbsp;|&nbsp;" % str(p.id)
			else:
				#===== this is if taken exam. and retake if still got incorrect question. then allowed to re-take
				#===== modification is requested by customer. retake one time is not enough. they need to change it
				#===== if retake still got error. they are allowed to retake.
				try:
					logger.info("retake trakcing")
					if MCQ_StudentRetakeAnswer.objects.filter(srta_student=student,srta_question__in=question_set,srta_optionlist__opl_iscorrect=False,srta_paper=p).exists():
						logger.info('fall in option 1')
						str_btn_retake = "<a href='/mcq/student/retakeassignment/?paperid=%s'><font color=black>Re-Take</font></a> &nbsp;|&nbsp;" % str(p.id)	
					else:
						logger.info('fall in option 2')
						if MCQ_StudentRetakeAnswer.objects.filter(srta_paper=p,srta_student=student,srta_question__in=question_set ).exists() == False:
							str_btn_retake = "<a href='/mcq/student/retakeassignment/?paperid=%s'><font color=black>Re-Take</font></a> &nbsp;|&nbsp;" % str(p.id)
						else:
							logger.info('fall in option 3')
						
						

				except Exception, Err:
					
					logger.debug("exception %s" % Err)


				#if MCQ_StudentReTakenTracking.objects.filter(strt_assignment=a,strt_paper=p,strt_student=student).exists():
				#	str_btn_retake=""
				#else:
					#====== two situation, if taken with all correct. not required re-take, if take but no select option, then allowed to retake
				#	if answered_wrong_answer_count > 0:
				#		str_btn_retake = "<a href='/mcq/student/retakeassignment/?paperid=%s'><font color=black>Re-Take</font></a> &nbsp;|&nbsp;" % str(p.id)
				#	else:
				#		answered_yet_answer_count = sum(1 for sa in stuanswer_set if sa.optionlist == None)
				#		if answered_yet_answer_count > 0:
				#			str_btn_retake = "<a href='/mcq/student/retakeassignment/?paperid=%s'><font color=black>Re-Take</font></a> &nbsp;|&nbsp;" % str(p.id)
		
			
			
			action = "%s <a href='/mcq/student/summarize/?paperid=%s'><font color=black>View</font></a>" % (str_btn_retake,str(p.id))
			
				
					
			
			assignment_list.append([a, count, p, action])
	# logger.info("assignment_list  .... %s" % assignment_list)
	return assignment_list

@login_required
def mcq_student_getassignedassignments(request):
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
		assignments = teacher.mcq_assignment_set.filter(asm_students=student)
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

#=========================================================
#             Canvas in MCQ
#=========================================================


class MCQ_CanvasView(TemplateView):
	template_name = 'mcq_raphael.html'


class MCQ_OptionCanvasView(TemplateView):
	template_name = 'mcq_optionraphael.html'



def mcq_canvas_upload(request):
    response_data = {'state': 'failure'}
    if request.method == "POST":
        print "~~~~~~~~~~~~~~~~~~" * 122
        print request.POST
        id = json.loads(request.POST['id'].encode('utf-8'))
        canvasmap = json.loads(request.POST['canvasmap'].encode('utf-8'))
        try:
            question = MCQ_Question.objects.get(id=id['questionid'])
            stdanswer = None
            stuanswer = None
            if id.get('stdanswerid'):
                #stdanswer = question.stdoption
		logger.info("should update standard answer, but mcq not available")
            elif id.get('stuanswerid'):
                stuanswer = MCQ_StudentAnswer.objects.get(id=id['stuanswerid'])
        except Exception, e:
            logger.error(e)
            response_data['state'] = "question not found"
        else:
            for canvasname, canvasitem in canvasmap.items():
                try:
                    
                    canvas = MCQ_Canvas.objects.get_or_create(name=str(canvasname),
                                                              question=question, stuanswer=None)
                except Exception, e:
                    print str(e) ,"EXCEP11111111111111111111111111"
                    logger.error(e)
                try:
                    canvas[0].axismap = pickle.dumps(canvasitem['axis'])
                    canvas[0].drawopts = pickle.dumps(canvasitem['drawopts'])
                    canvas[0].rulelist = pickle.dumps(canvasitem['rulelist'])
                except Exception, e:
                    print str(e), "222222222222222222222222222222222222"
                    logger.error(e)
                print stuanswer, "STUDENT ANSWER"
                if stuanswer:
                    mark = __canvasmark(question, canvas[0])
                    if not mark:
                        mark = 0
                    print mark, "MARK555555555555"
                    canvas[0].mark = mark
                    response_data['canvasmark'] = mark
                    print 'text twex'
                try:
                    canvas[0].save()
                except Exception as e:
                    print str(e), "8888888888888888"
                print 'End'
            response_data['state'] = "success"
    print response_data, "response_data response_data"
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def mcq_optioncanvas_upload(request):
    response_data = {'state': 'failure'}
    if request.method == "POST":
        print "~~~~~~~~~~~~~~~~~~" * 122
        print request.POST
        id = json.loads(request.POST['id'].encode('utf-8'))
        canvasmap = json.loads(request.POST['canvasmap'].encode('utf-8'))
        try:
            optionobj = MCQ_Optionlist.objects.get(id=id['optionid'])
	    
        except Exception, e:
            logger.error(e)
            response_data['state'] = "question not found"
        else:
            for canvasname, canvasitem in canvasmap.items():
                try:
                    
                    canvas = MCQ_OptionCanvas.objects.get_or_create(name=str(canvasname),
                                                              option=optionobj )
                except Exception, e:
                    print str(e) ,"EXCEP11111111111111111111111111"
                    logger.error(e)
                try:
                    canvas[0].axismap = pickle.dumps(canvasitem['axis'])
                    canvas[0].drawopts = pickle.dumps(canvasitem['drawopts'])
                    canvas[0].rulelist = pickle.dumps(canvasitem['rulelist'])
                except Exception, e:
                    print str(e), "222222222222222222222222222222222222"
                    logger.error(e)
                 
                try:
                    canvas[0].save()
                except Exception as e:
                    print str(e), "8888888888888888"
                print 'End'
            response_data['state'] = "success"
    print response_data, "response_data response_data"
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def __mcq_canvasmark(question, stucanvas):
    print "###############################"
    canvasname = stucanvas.name
    print 'canvasname  = ', canvasname
    try:
        stdanswer = question.stdanswer
        stdcanvas = MCQ_Canvas.objects.get(name=str(canvasname), question=question,
                                       stdanswer=stdanswer, stuanswer=None)
        stddrawopts = pickle.loads(str(stdcanvas.drawopts))
        stdrulelist = pickle.loads(str(stdcanvas.rulelist))
        stdpointlist = pickle.loads(str(stdcanvas.pointlist))
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error(e)
    else:
        canvascompare = Canvascompare()
        studrawopts = pickle.loads(str(stucanvas.drawopts))
        sturulelist = pickle.loads(str(stucanvas.rulelist))
        drawoptspair = canvascompare.comparecurvesimilarity(stddrawopts, studrawopts)
        print 'drawoptspair = ', drawoptspair
        logger.info(drawoptspair)
        correctlist = canvascompare.comparelist(sturulelist, stdrulelist)
        print 'correctlist = ', correctlist
        mark = canvascompare.mark(correctlist, stdpointlist)
        print 'mark = ', mark
        return mark


def mcq_canvas_get(request):
    if request.method == 'POST':
        print request.POST
        response_data = {'state': 'failure'}
        try:
            canvasname = request.POST['name']
            id = json.loads(request.POST['id'].encode('utf-8'))
        except Exception, e:
            logger.error(e)
            response_data['state'] = "no name or id specified"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        try:
            question = MCQ_Question.objects.get(id=id['questionid'])
            stdanswer = None
            stuanswer = None
            if id.get('stdanswerid'):
                stdanswer = question.stdanswer
            #elif id.get('stuanswerid'):
            #    stuanswer = MCQ_StudentAnswer.objects.get(id=id['stuanswerid'])
        except Exception, e:
            logger.error(e)
            response_data['state'] = "question not found"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        if stdanswer:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                            stdanswer=stdanswer, stuanswer=None)

            except:
                questioncanvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                                    stdanswer=None, stuanswer=None)
                canvas = MCQ_Canvas.objects.create(name=canvasname, question=question,
                                               stdanswer=stdanswer, stuanswer=None,
                                               drawopts=questioncanvas.drawopts,
                                               axismap=questioncanvas.axismap,
                                               rulelist=questioncanvas.rulelist)
        elif stuanswer:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                            stuanswer=stuanswer, stdanswer=None)
                canvas.rulelist = pickle.dumps([])
                print "\n  --------------------"
                print 'stu_canvas = ', canvas
                canvas.save()
            except Exception, e:
                print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
                import traceback
                traceback.print_exc()
                logger.info(e)
                canvas = None
        else:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                            stdanswer=None, stuanswer=None)

            except Exception, e:
                print "@@@@@@@ last part     1111"
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
            print canvasmap, "CANCAS @ canvas_get"
            if canvasmap:
                response_data['canvasmap'] = canvasmap
                response_data['state'] = 'success'
        print 'response_data @ last...............\n'
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
		
def mcq_optioncanvas_get(request):
    if request.method == 'POST':
        print request.POST
        response_data = {'state': 'failure'}
        try:
            canvasname = request.POST['name']
            id = json.loads(request.POST['id'].encode('utf-8'))
	    logger.info("id:  %s" % id)
        except Exception, e:
            logger.error(e)
            response_data['state'] = "no name or id specified"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        try:
            optionlist = MCQ_Optionlist.objects.get(id=id['optionid'])
             
        except Exception, e:
            logger.error(e)
            response_data['state'] = "question not found"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
       
        try:
            canvas = MCQ_OptionCanvas.objects.get(name=canvasname, option=optionlist)
	except Exception , e:
            logger.error(e)

        if canvas:
            canvasmap = {canvasname: {'axis': pickle.loads(str(canvas.axismap)),
                                      'drawopts': pickle.loads(str(canvas.drawopts)),
                                      'rulelist': pickle.loads(str(canvas.rulelist))
                                      }
                         }
            print canvasmap, "CANCAS @ canvas_get"
            if canvasmap:
                response_data['canvasmap'] = canvasmap
                response_data['state'] = 'success'
        print 'response_data @ last...............\n'
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
		
		
def getMCQTeacherList(request):
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
        print ztreejson
        response = render_to_response('mcq_teacher_list.json',
                                      {'questiontree': ztreejson,
                                       'inum': len(ztreejson), 'qnum': qnum},
                                      context_instance=RequestContext(request))
        response['Content-Type'] = 'text/plain; charset=utf-8'
        response['Cache-Control'] = 'no-cache'
        return response
    else:
        view = request.GET.get('view')
        itempool_id = request.GET.get('itempool_id')
        print view,"view", itempool_id, "itempool_id"
        if view:# Itempool view mode selected
            itempool = MCQ_Itempool.objects.get(id=int(itempool_id))
            ztreejson = __teacherJsonList(tb, view, itempool)
            print ztreejson
            response = render_to_response('teacher_list.json',
                                          {'mcq_questiontree': ztreejson,
                                           'inum': len(ztreejson), 'qnum': qnum},
                                          context_instance=RequestContext(request))
            response['Content-Type'] = 'text/plain; charset=utf-8'
            response['Cache-Control'] = 'no-cache'
            return response
        else:# Other than view mode either add item or modify item.
            print 'yes'
            if itempool_id and int(itempool_id) != -1:
                #Modify mode of selected box
                modify = True
                itempool = MCQ_Itempool.objects.get(id=int(itempool_id))
                ztreejson = __teacherJsonList(tb, view, itempool, modify)
                print ztreejson
                response = render_to_response('mcq_teacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response
            else: 
                #Get method of selected teacher box
                ztreejson = __teacherJsonList(tb, view)
                print ztreejson
                response = render_to_response('mcq_teacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response
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
            print selected_teacher,"selected teacher"
            teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
            print teacher_list,"modified list"
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

def addMCQteacher(request):
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
			print type(teacher_ids), teacher_ids
			if int(itempool_id) != -1:
				itempool = MCQ_Itempool.objects.get(id = int(itempool_id))

				print itempool.itp_teacher.user_id
				for teacher in teacher_list:
					if itempool.itp_teacher.user_id != int(teacher):
						teach = TProfile.objects.get(user_id=int(teacher))
						print teach,"teacher"
						itempool.itp_accessible.add(teach)
						itempool.save()
					try:
						question_list = MCQ_Question.objects.filter(itempool=itempool)
						logger.info("print question list %s" % question_list)
						for question in question_list:
							if question.teacher.user_id != int(teacher):
								teach = TProfile.objects.get(user_id=int(teacher))
								logger.info("print teacher %s" % teach)
								question.qtn_accessible.add(teach)
								question.save()
					except Exception , e:
						logger.error(e)
						#traceback.print_exec();
				return HttpResponse(json.dumps({'response':'success'}))
			else:
				return HttpResponse(json.dumps({'response':'failure'}))
		except Exception, e:
			logger.error(e)
	return HttpResponse(json.dumps({'response':'failure'}))



def mcq_canvas_get(request):
    if request.method == 'POST':
        print request.POST
        response_data = {'state': 'failure'}
        try:
            canvasname = request.POST['name']
            id = json.loads(request.POST['id'].encode('utf-8'))
        except Exception, e:
            logger.error(e)
            response_data['state'] = "no name or id specified"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        try:
            question = MCQ_Question.objects.get(id=id['questionid'])
            stdanswer = None
            stuanswer = None
            #if id.get('stdanswerid'):
            #    stdanswer = question.stdanswer
            #elif id.get('stuanswerid'):
            #stuanswer = MCQ_StudentAnswer.objects.get(id=id['stuanswerid'])
        except Exception, e:
            logger.error(e)
            response_data['state'] = "question not found"
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        if stdanswer:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                             stuanswer=None)

            except:
                questioncanvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                                    stuanswer=None)
                canvas = MCQ_Canvas.objects.create(name=canvasname, question=question,
                                               stuanswer=None,
                                               drawopts=questioncanvas.drawopts,
                                               axismap=questioncanvas.axismap,
                                               rulelist=questioncanvas.rulelist)
        elif stuanswer:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                            stuanswer=stuanswer)
                canvas.rulelist = pickle.dumps([])
                print "\n  --------------------"
                print 'stu_canvas = ', canvas
                canvas.save()
            except Exception, e:
                print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
                import traceback
                traceback.print_exc()
                logger.info(e)
                canvas = None
        else:
            try:
                canvas = MCQ_Canvas.objects.get(name=canvasname, question=question,
                                             stuanswer=None)

            except Exception, e:
                print "@@@@@@@ last part     1111"
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
            print canvasmap, "CANCAS @ canvas_get"
            if canvasmap:
                response_data['canvasmap'] = canvasmap
                response_data['state'] = 'success'
        print 'response_data @ last...............\n'
        return HttpResponse(json.dumps(response_data), mimetype="application/json")


@csrf_exempt
def mcq_optionlist_uploadimage(request):
	logger.info('mcq_optionlist_uploadimage %s ' % request.POST)
	if request.method == 'POST':
		
		try:
			optionid = request.POST["optionlistid"] 
			isStandardImage = request.POST.get('standard_image')
			image = request.FILES.get('Filedata', None)
			logger.info('optionid: %s' % optionid)
			optionobj = MCQ_Optionlist.objects.get(id=optionid)
			
		except Exception, e:
			logger.info('option not exists %s ' % e)
			return HttpResponse("Upload Error")
		else:
			logger.info('option 1')
		    	if isStandardImage and isStandardImage == 'yes':
				iscorrect = True
				imagename, thumbname = __changeNameForStd("option_%s" % image.name, questionid)
				questionimages = MCQ_OptionImage.objects.filter(option=optionobj).exclude(qim_description='del')
				digests = list(questionimage.digest for questionimage in questionimages)
				uploadeddigestimages = MCQ_OptionImage.objects.filter(option=optionobj,
						                                    qim_iscorrect=True).exclude(qim_description='del')
				stddigests = list(i.digest for i in uploadeddigestimages)
				uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER, "option_%s" % imagename)
				if digest in digests and digest not in stddigests:
				    description = None
				else:
				    description = 'del'
		    	else:

				logger.info('option 2')
				try:
					iscorrect = False
					imagename, thumbname = __changeName(image.name, optionid)
					uploadImageFullName, digest = __saveImage(image, settings.UPLOADFOLDER,"option_%s" % imagename)
					questionimages = MCQ_OptionImage.objects.filter(option=optionobj).exclude(qti_description='del')
					digests = list(questionimage.qti_digest for questionimage in questionimages)
					if digest in digests:
					    description = 'del'
					else:
					    description = None
				except Exception , e:
					logger.error(e)
				
				logger.info('option 1 %s' % uploadImageFullName)


			__resizeImage(uploadImageFullName,
			  	os.path.join(settings.THUMBNAILFOLDER, thumbname))
		try:
		    	imageObj = MCQ_OptionImage.objects.create(option=optionobj,
				                            qti_imagename=image.name,
				                            qti_abspath=imagename,
				                            qti_digest=digest,
				                            qti_description=description,
				                            qti_iscorrect=iscorrect)
		    	imageObj.save()
		except:
		    	print sys.exc_info()
		    	return HttpResponse("Upload Error")
		return HttpResponse("Upload Success!", mimetype="text/plain")
	else:
		return HttpResponse("Upload Error!", mimetype="text/plain")

@permission_required('auth.add_user')
def mcq_optionlist_thumbnails(request):
	logger.info('mcq_optionlist_thumbnails')
	tp, res = getTpByRequest(request, None)
	response_data = {'state': 'failure'}
	if tp and request.method == 'POST':
		try:
			iscorrectParam = request.POST.get("iscorrect")
			if iscorrectParam and iscorrectParam == 'yes':
				iscorrect = True
			else:
				iscorrect = False
			optionid = request.POST.get("optionlist_id")
			logger.info('mcq_optionlist_thumbnails 2 %s' % optionid)
			if optionid and optionid != '-1':
				optionobj = MCQ_Optionlist.objects.get(id=int(optionid))
				thumbnails = MCQ_OptionImage.objects.filter(option=optionobj, qti_iscorrect=iscorrect).exclude(qti_description='del')
			else:
				thumbnails = []
		except Exception, e:
			logger.error(e)
		if thumbnails:
			if iscorrect:
				questionimglist = pickle.loads(str(optionobj.imagepointlist))
				stdthumbnails = list([imagepoint, t]
						     for imagepoint in questionimglist
							     for t in thumbnails
							     	if imagepoint['Point_Text'] is t.digest)
				response_data['state'] = 'success' 
				response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.abspath),
								    ("P0.%s" % str(i + 1)),
								    "%s/%s" % (settings.UPLOADPREFIX, t.abspath),
								    t.id] for i, t in enumerate(thumbnails))
				response_data['stdthumbnail_ids'] = list(t.id for t in thumbnails)
		    	else:
				pointlist = list({'Point_No': u'P0.' + str(i + 1),
				                  'Point_Text': image.qti_digest}
				                for i, image in enumerate(thumbnails))
				response_data['state'] = 'success' 
				response_data['thumbnails'] = list(["%s/thumb__%s" % (settings.THUMBNAILPREFIX, t.qti_abspath),
				                                    ("P0.%s" % str(i + 1)),
				                                    "%s/%s" % (settings.UPLOADPREFIX, t.qti_abspath),
				                                    t.id] for i, t in enumerate(thumbnails))
		return HttpResponse(json.dumps(response_data), mimetype="application/json")



@permission_required('auth.add_user')
def mcq_optionlist_deleteimage(request):
    logger.info('optionlist delete image')
    response_data = {'state': 'failure'}
    if request.method == 'POST':
        imageid = request.POST.get("imageid")
        try:
            imageToDelete = MCQ_OptionImage.objects.get(id=imageid)
	    logger.info('this is imageToDelete: %s ' % imageToDelete)
        except Exception ,e:
	    logger.info(e)
            pass
        else:
	    logger.info('optionlist delete image no problem')
            imageToDelete.qti_description = 'del'
            imageToDelete.save()
            response_data['state'] = 'success'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

#=========================================================
#             End of Canvas in MCQ
#=========================================================


#=========================================================
#        Category Get Teacher list
#=========================================================
def getMCQCategoryTeacherList(request):
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
	logger.info("getMCQCategoryTeacherList 1")
        questioncategory_id = request.POST['questioncategory_id']
        view = request.POST['view']
        ztreejson = __questionCategoryteacherJsonList(tb, view)
        #print ztreejson
        response = render_to_response('mcq_questioncategoryteacher_list.json',
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
		
	    logger.info("getMCQCategoryTeacherList 2a %S " % questioncategory_id)
            itempool = MCQ_QuestionCategory.objects.get(id=int(questioncategory_id))
	    logger.info("after 2a ================== %s" % itempool)
            ztreejson = __questionCategoryteacherJsonList(tb, view, itempool)
            #print ztreejson
            response = render_to_response('mcq_questioncategoryteacher_list.json',
                                          {'questiontree': ztreejson,
                                           'inum': len(ztreejson), 'qnum': qnum},
                                          context_instance=RequestContext(request))
            response['Content-Type'] = 'text/plain; charset=utf-8'
            response['Cache-Control'] = 'no-cache'
            return response
        else:# Other than view mode either add item or modify item.
	    #logger.info("getMCQCategoryTeacherList 2b  [questioncategory_id: %s ] " % questioncategory_id )
            print 'yes'
            if questioncategory_id and int(questioncategory_id) != -1:
	    	logger.info("getMCQCategoryTeacherList 2a1")
                #Modify mode of selected box
                modify = True
                itempool = MCQ_QuestionCategory.objects.get(id=int(questioncategory_id))
                ztreejson = __questionCategoryteacherJsonList(tb, view, itempool, modify)
		logger.info("====================@@@@@@@@@@@@@============")
		logger.info(ztreejson)
		logger.info("====================@@@@@@@@@@@@@============")

                #print ztreejson
                response = render_to_response('mcq_questioncategoryteacher_list.json',
                                              {'questiontree': ztreejson,
                                               'inum': len(ztreejson), 'qnum': qnum},
                                              context_instance=RequestContext(request))
                response['Content-Type'] = 'text/plain; charset=utf-8'
                response['Cache-Control'] = 'no-cache'
                return response
            else: 
	    	logger.info("getMCQCategoryTeacherList 2a2")
                #Get method of selected teacher box
                ztreejson = __questionCategoryteacherJsonList(tb, view)
                print ztreejson
                response = render_to_response('mcq_questioncategoryteacher_list.json',
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
		parent_questioncategory = MCQ_QuestionCategory.objects.get(id=questioncategory.qct_QuestionCategory_parentid)
		
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



#=========================================================
#       End of  Category Get Teacher list
#=========================================================




#=========================================================
#       Category Add Teacher list
#=========================================================





def addMCQCategoryteacher(request):
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
			print type(teacher_ids), teacher_ids
			if int(questioncategory_id) != -1:
				logger.info("question 1")
				QuestionCategory = MCQ_QuestionCategory.objects.get(id = int(questioncategory_id))
				QuestionCategory.qct_teacher.clear() 
				lst_teacher = TProfile.objects.filter(user_id__in=teacher_list)
				QuestionCategory.qct_teacher.add(*lst_teacher)
				try:
					QuestionCategory.save()
				except Exception , err:
					logger.info("error while saving QuestionCategory: %s" % err)
				logger.info("count for teachers: %s" % lst_teacher) 
				return HttpResponse(json.dumps({'response':'success'}))
			else:
				return HttpResponse(json.dumps({'response':'failure'}))
		except Exception, e:
			logger.error(e)
	return HttpResponse(json.dumps({'response':'failure'}))


#=========================================================
#      End of Category Add Teacher list
#=========================================================
