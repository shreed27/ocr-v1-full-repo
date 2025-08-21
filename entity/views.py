# Create your views here.
from entity.models import Subjects, Years, Levels, Randomcode
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.http import HttpResponse
import random
import logging

logger = logging.getLogger(__name__)

def render(len=8, num_flag=True, low_flag=True, up_flag=True, special_flag=True):
    num = "0123456789"
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    special = "~!@#$%^&*()[]{}_=+-"

    str = ''
    if num_flag:
        str += num
    if low_flag:
        str += lower
    if up_flag:
        str += upper
    if special_flag:
        str += special
    if str == '':
        str = num + lower
    return ''.join(random.sample(str, len)).replace(" ", "")

@login_required
def getentity(request):
    response_data = {'state':'failure'}
    try:
        years = [y.yearname for y in Years.objects.all()]
        subjects = [s.subjectname for s in Subjects.objects.all()]
        levels = [l.levelname for l in Levels.objects.all()]
        response_data['year'] = years
        response_data['subject'] = subjects
        response_data['level'] = levels
        response_data['state'] = 'success'
    except:
        pass
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def generaterandomcode(request):
    response_data = {'status': 'failure'}
    codes = []
    i = 0
    while(i < 10):
        code = render()
        try:
            Randomcode.objects.create(randomcode = code)
        except Exception, e:
            logger.error(e)
        else:
            codes.append(code)
            i += 1
    response_data['status'] = 'success'
    response_data['randomcode'] = codes
    print response_data
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

