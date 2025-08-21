from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile, SProfile
from itempool.models import Itempool
from question.models import Question
from classroom.models import Classroom
from student.forms import *
import logging
import traceback
from datetime import datetime,timedelta

class StudentTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        self.weiyantp, self.student_id = add_user_data()
        clazz1_id = add_ClassRoom_data()
        self.client=Client()
        self.studentDetailForm = {
                'realname': 'yanchao',
                'username': 'yanchao',
                'password1': '1',
                'password2': '2',
                'email': 'yanchao@gmail.com',
                'clazz': clazz1_id,
                }

    def test_forms(self):
        #f = StudentDetailForm({})
        #self.assertFalse(f.is_valid())
        f = StudentDetailForm(self.studentDetailForm, teacher=self.weiyantp)
        self.assertFalse(f.is_valid())
    def test_alllinks(self):
        #login
        self.assertTrue(self.client.login(username='weiyan', password='1'))

        #test index
        response = self.client.get('/student/index/')
        self.assertEqual(response.status_code,302)

        #student_getall
        response = self.client.get('/student/getall/')
        self.assertEqual(response.status_code,200)

        #student_add
        response = self.client.post('/student/add/')
        self.assertEqual(response.status_code,200)

        #student_modify
        response = self.client.get('/student/modify/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/student/modify/')
        self.assertEqual(response.status_code,200)

        #student_delete
        response = self.client.post('/student/delete/', {'studentid':self.student_id}, follow=True)
        self.assertEqual(response.status_code,200)

        #student_profile
        response = self.client.get('/student/profile/'+str(self.student_id)+"/")
        self.assertEqual(response.status_code,404)
        response = self.client.get('/student/profile/9999/')
        self.assertEqual(response.status_code,404)

        #student_getassignedassignments
        self.assertTrue(self.client.login(username='weiyan2', password='1'))
        response = self.client.get('/student/getassignedassignments/')
        print response , "!!!!!!!!!!!!!!!!!!!!!!!!"
        if response == []:
            pass
        else:
            self.assertEqual(response.status_code,200)

        #student_takeassignment

        #save client's session
        cur = datetime.now()
        startkey = "__assignment_time_start"
        totalkey = "__assignment_time_total"
        session = self.client.session
        session[startkey] = cur
        session[totalkey] = 18000
        session.save()

        try:
            response = self.client.get('/student/takeassignment/')
        except AttributeError:
            logger.info("Passing AttributeError: no paperid")
        else:
            traceback.print_exc()

        #student_custompaper
        response = self.client.post('/student/custompaper/')
        self.assertEqual(response.status_code,200)

        #student_checktime
        response = self.client.post('/student/checktime/')
        self.assertEqual(response.status_code,200)

        #student_submitanswer
        response = self.client.post('/student/submitanswer/')
        self.assertEqual(response.status_code,200)

        #student_submitpaper
        response = self.client.post('/student/submitpaper/')
        self.assertEqual(response.status_code,200)

        #student_papersummarize
        response = self.client.get('/student/summarize/')
        self.assertEqual(response.status_code,200)

        #student_gethistoryanswers
        response = self.client.get('/student/gethistoryanswers/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/student/gethistoryanswers/')
        self.assertEqual(response.status_code,200)


        #LOGOUT STATE
        self.client.logout()

def add_groups_data():
    try:
        tg = Group.objects.create(name="teachers")
        sg = Group.objects.create(name="students")
    except:
        return

    p1=Permission.objects.get(codename="add_user")
    p2=Permission.objects.get(codename="change_user")
    p3=Permission.objects.get(codename="delete_user")
    p4=Permission.objects.get(codename="add_session")
    p5=Permission.objects.get(codename="change_session")
    p6=Permission.objects.get(codename="delete_session")
    tg.permissions.add(p1)
    tg.permissions.add(p2)
    tg.permissions.add(p3)
    tg.permissions.add(p4)
    tg.permissions.add(p5)
    tg.permissions.add(p6)
    sg.permissions.add(p4)
    sg.permissions.add(p5)
    sg.permissions.add(p6)

def add_user_data():
    weiyan=User.objects.create_user("weiyan","yan,wei_sjtu@yahoo.cn","1")
    weiyan2=User.objects.create_user("weiyan2","yan,wei2_sjtu@yahoo.cn","1")
    weiyantp=TProfile.objects.create(user=weiyan,gender="male",cellphone="13671670930")
    weiyansp=SProfile.objects.create(user=weiyan2,gender="male",cellphone="13671670930",
            teacher=weiyantp)
    w1=User.objects.create_user("w1","yan,wei_sjtu@yahoo.cn","1")
    return weiyantp, weiyansp.user.id

def add_ClassRoom_data():
    clazz1 = Classroom.objects.create(roomname="room1", volume=100)
    return clazz1.id
