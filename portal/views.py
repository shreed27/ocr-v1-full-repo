import logging
import json
import traceback
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from forms import RegisterForm, LoginForm, InfoModForm, ForgotPasswordForm
from models import TProfile, SProfile
from django.views.decorators.csrf import csrf_exempt
from emailtool import EmailTool
from portal.common import getGroupNameByRequest
from django.contrib.auth import get_backends
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from entity.models import Randomcode
from django.db import IntegrityError
from classroom.models import Classroom

logger = logging.getLogger(__name__)


def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        group = "teachers"
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            invitecode = form.cleaned_data['invitecode']
            if invitecode:
                invitecode.used = True
                invitecode.save()
            user = User.objects.create_user(username, email, password)
            user.groups = (Group.objects.get(name=group),)
            t = TProfile(user=user)
            t.save()
            return redirect('index')
    return render_to_response('register.html', {'form': form},
                              context_instance=RequestContext(request))


@login_required
def index(request):
    group = getGroupNameByRequest(request)
    logger.debug("user group:%s" % group)
    if group == 'teachers':
        return redirect('teacher_index')
    if group == 'students':
        return redirect('student_index')
    messages.add_message(request, messages.INFO, 'User has no permission for broswering, please contact admin')
    return redirect('login')


def login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        form = LoginForm(request.POST)
        if form.is_valid():
            if __login(request, username, password):
                nextpage = request.GET.get('next')
                if nextpage:
                    return redirect(nextpage)
                else:
                    return redirect('index')
    return render_to_response('login.html', {'form': form},
                              context_instance=RequestContext(request))


def logout(request):
    auth_logout(request)
    return redirect('login')


def __login(request, username, password):
    ret = False
    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth_login(request, user)
            ret = True
        else:
            messages.add_message(request, messages.INFO, 'User is not active!')
    else:
        messages.add_message(request, messages.INFO, 'User or Password Not Correct!')
    return ret


def __mod_user(username, newpassword, newemail):
    u = User.objects.get(username=username)
    u.set_password(newpassword)
    u.email = newemail
    u.save()
    return True


@login_required
def info_modify(request):
    form = InfoModForm(initial={'username': request.user.username})
    if request.method == 'POST':
        form = InfoModForm(request.POST)
        if form.is_valid() and request.user:
            newpassword = form.cleaned_data['newpassword']
            email = form.cleaned_data['email']
            __mod_user(request.user.username, newpassword, email)
            return redirect('index')
    return render_to_response('info_modify.html', {'form': form},
                              context_instance=RequestContext(request))


def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            et = EmailTool()
            et.send([email], "your new password is:sss")
            messages.add_message(request, messages.SUCCESS,
                                 '%s:Your password has been emailed to you!' % username)
            return redirect('login')
    return render_to_response('forgot_password.html', {'form': form},
                              context_instance=RequestContext(request))

@require_POST
@csrf_exempt
def api_login(request):
    """
    This function used to login into intemass through API call
    :param request:
    :return response:
    """
    response = False
    assert request.method == "POST", "Only accepts POST method"
    assert request.POST.get('api_key') == settings.MEGAFORT_API_KEY, "Not authorized to access this api"
    api_key = request.POST.get('unique_key')
    try:
        print "I am enter"
        tprofile = TProfile.objects.get(api_key=api_key)
        print tprofile,"profile"
        # Login after succecful register
        # Bypass `authenticate()` because we did't get the user password
        user = tprofile.user
        backend = get_backends()[0]
        user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
        auth_login(request, user)
        response = True
    except TProfile.DoesNotExist:
        try:
            sprofile = SProfile.objects.get(api_key=api_key)
            # Login after succecful register
            # Bypass `authenticate()` because we did't get the user password
            user = sprofile.user
            backend = get_backends()[0]
            user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
            auth_login(request, user)
            response = True
        except SProfile.DoesNotExist:
            traceback.print_exc()
    return HttpResponse(json.dumps({'response':response}), content_type="application/json")


def api_logout(request):
    auth_logout(request)
    response = True
    return HttpResponse(json.dumps({'response':response}), content_type="application/json")


@require_POST
@csrf_exempt
def teacher_registration_API(request):
    """
    This function get the required parameters for registration through API
    and return success response
    :param request:
    :return : response['response_status'], response['response_msg']
    """
    response = dict()
    try:
        group = "teachers"
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password2')
        invitecode = request.POST.get('invitecode')
        print request.POST
        print invitecode,"code"
        try:
            randomcode = Randomcode.objects.get(randomcode = invitecode, used = False)
            randomcode.used = True
            randomcode.save()
        except:
            traceback.print_exc()
            response['response_status'] = False
            response['response_msg'] = "Invalid Invite Code"
            return HttpResponse(json.dumps(response), content_type="application/json")
        user = User.objects.create_user(username, email, password)
        user.groups = (Group.objects.get(name=group),)
        user.save()
        t = TProfile(user=user)
        t.api_key = request.POST.get('api_key')
        t.save()
        response['response_status'] = True
        response['response_msg'] = "Success"
        return HttpResponse(json.dumps(response), content_type="application/json")
    except:
        traceback.print_exc()


@require_POST
@csrf_exempt
def student_registration_API(request):
    """
    This function get the required parameters for student registration through API
    and return success response
    :param request:
    :return response['response_status'], response['response_msg']:
    """
    response = dict()
    print request.POST
    try:
        teacher_api_key = request.POST.get('teacher_api_key')
        username = request.POST.get('username')
        password = request.POST.get('password2')
        email = request.POST.get('email')
        gender = request.POST.get('gender')

        try:
            classroom = request.POST.get('class')
        except:
            classroom = None
        student_api_key = request.POST.get('student_api_key')
        print username, password, email, gender, student_api_key
        try:
            tp = TProfile.objects.get(api_key=teacher_api_key)
        except TProfile.DoesNotExist:
            response['response_status'] = False
            response['response_msg'] = "Teacher Profile doesn't exist"
            return HttpResponse(json.dumps(response), content_type="application/json")

        try:
            user = User.objects.create_user(username, email, password)
            user.groups = (Group.objects.get(name='students'),)
        except IntegrityError:
            traceback.print_exc()
            response['response_status'] = False
            response['response_msg'] = 'Username Already exists'
            return HttpResponse(json.dumps(response), content_type="application/json")
        if classroom:
            try:
                class_room = Classroom.objects.get(roomname=classroom)
            except Classroom.DoesNotExist:
                response['response_status'] = False
                response['response_msg'] = "Classroom Doesn't Exist"
                return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            class_room = None
        sp = SProfile.objects.create(user=user, teacher=tp,
                                     gender=gender, classroom=class_room, api_key = student_api_key)
        response['response_status'] = True
        response['response_msg'] = 'Success'
        return HttpResponse(json.dumps(response), content_type="application/json")
    except:
        traceback.print_exc()

# @require_POST
# @csrf_exempt
