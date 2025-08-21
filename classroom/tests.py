from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile,SProfile
from classroom.models import Classroom
from django.utils.datastructures import MultiValueDictKeyError
import logging
import traceback

class ClassroomTest(TestCase):
    room1_id = -1
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        teacher = add_user_data()
        self.client=Client()
        self.room1_id = add_classroom_data(teacher)

    def test_alllinks(self):
        #login
        self.assertTrue(self.client.login(username='weiyan', password='1'))
        #home page
        response = self.client.get('/home/')
        self.assertEqual(response.status_code,302)

        #getall classroom  page
        response = self.client.get('/classroom/getall/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'room1', status_code=200)

        response = self.client.get('/classroom/add/')
        self.assertEqual(response.status_code,200)

        response = self.client.get('/classroom/add/?classroomid=1')
        self.assertEqual(response.status_code,200)

        #response = self.client.post('/classroom/delete/')
        #self.assertEqual(response.status_code,200)

        response = self.client.post('/classroom/getstudents/',{'classid': '1'},follow=True)
        self.assertEqual(response.status_code,200)

        try:
            response = self.client.post('/classroom/getstudents/', follow= False )
        except MultiValueDictKeyError:
            self.logger.info("Passing MultiValueDictKeyError")
        else:
            self.assertTrue(False)
            traceback.print_exc()

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
    weiyantp=TProfile.objects.create(user=weiyan,gender="male",cellphone="13671670930")

    w1=User.objects.create_user("w1","yan,wei_sjtu@yahoo.cn","1")
    return weiyantp

def add_classroom_data(teacher):
    room1=Classroom.objects.create(roomname='room1', volume=30)
    teacher.classrooms.add(room1)

