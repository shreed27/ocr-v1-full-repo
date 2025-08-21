import logging
import json
from django.shortcuts import render_to_response
from django.template import RequestContext
from itempool.models import Itempool
from itempool.forms import ItemPoolDetailForm
from portal.models import TProfile
from question.models import Question
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy
from portal.common import getTpByRequest
import traceback

logger = logging.getLogger(__name__)


def __getItempool(itempoolid, tp=None):
    if not itempoolid or itempoolid == "-1":
        if tp:
            itempool = Itempool.objects.create(teacher=tp)
            itempool.accessible.add(tp)
            return itempool
        else:
            return None
    return get_object_or_404(Itempool, id=int(itempoolid))


@permission_required('auth.add_user')
def itempool_add(request):
    tp, res = getTpByRequest(request, "login")
    if not tp and res:
        return res
    if request.method == "POST":
        form = ItemPoolDetailForm(request.POST, teacher=tp)
        if form.is_valid():
            pass
    else:
        itempoolid = request.GET.get('itempoolid')
        try:
            i = Itempool.objects.get(id=itempoolid)
        except:
            form = ItemPoolDetailForm(teacher=tp)
        else:
            form = ItemPoolDetailForm(teacher=tp,
                                      initial={'itempoolid': i.id,
                                               'itempoolname': i.poolname})
    logger.info("itempool all...")
    return render_to_response('itempool_detail.html', {'form': form},
                              context_instance=RequestContext(request))


@permission_required('auth.add_user')
def itempool_getall(request):
    logger.info("itempool getall...")
    tp, res = getTpByRequest(request, "login")
    if not tp and res:
        return res
    itempools = []
    if tp:
        try:
            #itempools = Itempool.objects.filter(teacher=tp)
            itempools = Itempool.objects.filter(accessible=tp) #Itempool access by selected teacher
        except:
            pass
    response = render_to_response('itempool_all.json',
                                  {'itempools': itempools},
                                  context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@permission_required('auth.add_user')
def itempool_getquestions(request):
    logger.info("getstudents...")
    tp, res = getTpByRequest(request, None)
    questions = []
    view = 0
    if tp:
        itempoolid = request.GET.get("itempoolid")
        view = request.GET.get("view")
        logger.info("itempoolid:%s" % itempoolid)
        if itempoolid:
            try:
                itempool = Itempool.objects.get(id=int(itempoolid))
            except:
                itempool = None
            else:
                logger.info("itempool:%s" % itempool)
                try:
                    #Questions filter by accessible teacher
                    questions = Question.objects.filter(accessible=tp, itempool=itempool)
                except:
                    logger.info("no questions in %s" % itempool)
    if view:
        response = render_to_response('itempool_allquestions_readonly.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    else:
        response = render_to_response('itempool_allquestions.json',
                                      {'questions': questions},
                                      context_instance=RequestContext(request))
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Cache-Control'] = 'no-cache'
    return response


@permission_required('auth.add_user')
def itempool_updatename(request):
    print request.GET, "get detatis"
    logger.info("itempool_updatename...")
    tp, res = getTpByRequest(request, None)
    response_data = {'state': 'failure'}
    if tp:
        itempoolid = request.GET.get("itempoolid").strip()
        itempoolname = request.GET.get("itempoolname").strip()
        logger.info("itempoolid:%s,name:%s" % (itempoolid, itempoolname))
        if itempoolid and itempoolname:
            itempool = __getItempool(itempoolid, tp)
            logger.info(" get itempool %s" % itempool)
            if itempool:
                itempool.poolname = itempoolname
                itempool.save()
                response_data['itempoolid'] = itempool.id
                response_data['itempoolname'] = itempool.poolname
                response_data['state'] = 'success'
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


class ItempoolDelete(DeleteView):
    success_url = reverse_lazy("deleteview_callback")
    model = Itempool

    def get_object(self):
        pk = self.request.POST['itempoolid']
        return get_object_or_404(Itempool, id=pk)


def itempool_updatedesc(request):
    tp, res = getTpByRequest(request, None)
    response_data = {"state": "failure"}
    if request.method == 'POST':
        print request.POST, "Posted values"
        if tp:
            itempoolid = request.POST.get("itempoolid").strip()
            description = request.POST.get("description").replace('\r', '').replace('\n', '</br>').strip()
            logger.info("itempoolid:%s,desc:%s" % (itempoolid, description))
            if itempoolid:
                itempool = __getItempool(itempoolid, tp)
                logger.info(" get itempool %s" % itempool)
                if itempool:
                    itempool.description = description
                    itempool.save()
                    response_data['description'] = itempool.description.replace('</br>', '\n')
                    response_data['state'] = "success"
    else:
        itempoolid = request.GET.get("itempoolid").strip()
        if itempoolid and itempoolid != '-1':
            itempool = __getItempool(itempoolid, tp)
            response_data['description'] = itempool.description.replace('</br>', '\n')
            response_data['state'] = "success"
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")


def getTeacherList(request):
    """
    This function is used for display all teacher in select box.
    If view mode it show selected teacher only with disabled function.
    If modify mode it show the selected teacher without disabled function.
    :param request:
    :return Json Response of teacher_list.json file the data.
    """
    qnum = 0
    tb, res = getTpByRequest(request, None)
    view = 0
    if request.method == 'POST':
        itempool_id = request.POST['itempool_id']
        view = request.POST['view']
        ztreejson = __teacherJsonList(tb, view)
        print ztreejson
        response = render_to_response('teacher_list.json',
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
            itempool = Itempool.objects.get(id=int(itempool_id))
            ztreejson = __teacherJsonList(tb, view, itempool)
            print ztreejson
            response = render_to_response('teacher_list.json',
                                          {'questiontree': ztreejson,
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
                itempool = Itempool.objects.get(id=int(itempool_id))
                ztreejson = __teacherJsonList(tb, view, itempool, modify)
                print ztreejson
                response = render_to_response('teacher_list.json',
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
                response = render_to_response('teacher_list.json',
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
        selected_teacher = itempool.accessible.all()
        teacher_list = TProfile.objects.all().exclude(user__in = selected_teacher)
    else:
        if modify:
            selected_teacher = itempool.accessible.all()#.exclude(user=itempool.teacher)
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
        for teacher in itempool.accessible.all():
            teacher_node_list.append({'node':teacher, 'checked':'true', 'disabled':'true'})
    else:
        if modify:
            teacher_node_list = [{'node':itempool.teacher, 'checked':'true', 'disabled':'true'}]
            for teacher in itempool.accessible.all().exclude(user=itempool.teacher):
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


def addteacher(request):
    """
    This is post method. When addteacher button clicked then selected teacher
    will come in post method. We save the teacher data in itempool and return
    the success response
    :param request:
    :return {'response':'success'} or {'response':'failure'}:
    """
    if request.method == 'POST':
        print request.POST
        itempool_id = request.POST['itempool_id']
        teacher_ids = request.POST.get('teacher_ids')
        teacher_list = teacher_ids[1:-1].split(',')[1:]
        teacher_list = [int(i.strip('"')) for i in teacher_list]
        print type(teacher_ids), teacher_ids
        if int(itempool_id) != -1:
            itempool = Itempool.objects.get(id = int(itempool_id))

            print itempool.teacher.user_id
            for teacher in teacher_list:
                if itempool.teacher.user_id != int(teacher):
                    teach = TProfile.objects.get(user_id=int(teacher))
                    print teach,"teacher"
                    itempool.accessible.add(teach)
                    itempool.save()
                try:
                    question_list = Question.objects.filter(itempool=itempool)
                    for question in question_list:
                        if question.teacher.user_id != int(teacher):
                            teach = TProfile.objects.get(user_id=int(teacher))
                            print teach,"teacher"
                            question.accessible.add(teach)
                            question.save()
                except:
                    traceback.print_exec();
            return HttpResponse(json.dumps({'response':'success'}))
        else:
            return HttpResponse(json.dumps({'response':'failure'}))



