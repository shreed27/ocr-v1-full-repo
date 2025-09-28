import sys
import logging
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from django.shortcuts import redirect
from django.contrib import messages
from portal.models import TProfile, SProfile
from django.contrib.auth.models import User
from student.models import StudentAnswer
from django.views.debug import technical_500_response
from django.conf import settings


logger = logging.getLogger(__name__)


class UserBasedExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())

def getGroupNameByRequest(request):
    groups = request.user.groups.all()
    if groups and len(groups) > 0:
        return groups[0].name
    else:
        return None


def getTpByRequest(request, redirectUrl):
    group = getGroupNameByRequest(request)
    if group == "teachers":
        try:
            tp = TProfile.objects.get(user=request.user)
        except:
            messages.add_message(request, messages.SUCCESS, "No this user" % request.user.username)
            if redirectUrl:
                return None, redirect(redirectUrl)
            else:
                return None, None
    else:
        if redirectUrl:
            messages.add_message(request, messages.SUCCESS, "You(%s) are not tearchers" % request.user.username)
            res = redirect(redirectUrl)
            return None, res
        else:
            return None, None
    return tp, None


def getSpByRequest(request, redirectUrl):
    group = getGroupNameByRequest(request)
    if group == "students":
        try:
            sp = SProfile.objects.get(user=request.user)
        except:
            messages.add_message(request, messages.SUCCESS, "No this user" % request.user.username)
            if redirectUrl:
                return None, redirect(redirectUrl)
            else:
                return None, None
    else:
        if redirectUrl:
            messages.add_message(request, messages.SUCCESS, "You(%s) are not students" % request.user.username)
            res = redirect(redirectUrl)
            return None, res
        else:
            return None, None
    return sp, None


def getSpById(sp_id):
    try:
        sp = SProfile.objects.get(user=User.objects.get(id=sp_id))
    except:
        sp = None
        logger.info("sprofile not found:%s" % sp_id)
        pass
    return sp


def getTpById(tp_id):
    try:
        tp = TProfile.objects.get(user=User.objects.get(id=tp_id))
    except:
        tp = None
        logger.info("tprofile not found:%s" % tp_id)
        pass
    return tp


def stripHTMLStrings(html):
    """
        Strip HTML tags from any string and transfrom special entities
    """
    text = html

    # replace special strings
    special = {'&nbsp;': ' ', '&amp;': '&', '&quot;': '"',
               '&lt;': '<', '&gt;': '>', '&ldquo;': '"',
               '&rdquo;': '"', '&hellip;': '...'}

    for (k, v) in list(special.items()):
        text = text.replace(k, v)
    return text


def stripBody(html):
    return html.split('<body')[0]



def getTakedStuanswers(questionset, student):
    try:
        stuanswer_set = list(StudentAnswer.objects.filter(question=question,
                                                          student=student, taked=True).latest('timestamp') for question in questionset)
    except:
        stuanswer_set = list(StudentAnswer.objects.filter(question__in=questionset,
                                                          student=student, taked=True))
    return stuanswer_set


def getStuanswers(questionset, student):
    try:
        stuanswer_set = list(StudentAnswer.objects.filter(question=question,
                                                          student=student).latest('timestamp') for question in questionset)
    except:
        stuanswer_set = list(StudentAnswer.objects.filter(question__in=questionset,
                                                          student=student))
    return stuanswer_set

def retake_option(stuanswer_set):
    from paper.templatetags.paper_tags import actual_mark
    retake_flag = True
    actual_total_mark = 0
    paper_total_mark = 0
    for stu_ans in stuanswer_set:
        actual_total_mark = actual_total_mark + actual_mark(stu_ans)
    print(actual_total_mark,"Full mark")

    # for stu_ans in stuanswer_set:
    #     paper_total_mark = paper_total_mark + stu_ans.mark
    # print paper_total_mark,"paper total mark"
    paper_total_mark = sum(ans.mark for ans in stuanswer_set)
    #
    try:
        if paper_total_mark == actual_total_mark:
            retake_flag = False
        else:
            raise Exception
    except:
        for stud in stuanswer_set:
            if stud.attempted_count > 3:
                print(stud.attempted_count, "count count count")
                retake_flag = False
    return retake_flag

def std_embedded_latex(content):
    bs_obj = BeautifulSoup(content)
    # bs_obj = BeautifulSoup(content, 'html5lib') #uncomment this for apache run
    for img_tag in bs_obj.find_all("img"):
        _title = str(img_tag["title"]).replace(" ", "~")
        img_tag.replace_with("$$"+_title+" ")
    return bs_obj.prettify()

def stu_embedded_latex(content):
    bs_obj = BeautifulSoup(content)
    # bs_obj = BeautifulSoup(content, 'html5lib') #uncomment this for apache run
    for img_tag in bs_obj.find_all("img"):
        _title = str(img_tag["title"]).replace(" ", "~")
        img_tag.replace_with("$$"+_title+" ")
    return bs_obj.prettify()

def latex_to_img(text, width=0, height=0):
    return_txt = ""
    for p_text in text.split():
        temp_text = p_text
        if p_text.startswith("$$"):
            strip_text = str(p_text.strip("$$"))
            url_encode = urllib.parse.urlencode({"":strip_text})[1:]
            temp_text = '<img '
            if width and height:
                temp_text += 'width="' + str(width)+ '" height="'+ str(height) + '"'
            temp_text += 'class="mathImg" title="' +  strip_text
            temp_text +='" src="http://latex.codecogs.com/gif.latex?'
            temp_text += url_encode + '">'
        return_txt += str(" "+temp_text)
    return return_txt

def remove_latex(text):
    new_text = " ".join([word
                     for word in text.split()
                     if word and not word.startswith("$$")])
    if new_text.strip() in [".", ","]:
        return ""
    else:
        return new_text