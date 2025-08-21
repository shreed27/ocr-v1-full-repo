from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile,SProfile
from question.models import Question
from itempool.models import Itempool
from paper.models import Paper
from django.utils.datastructures import MultiValueDictKeyError
import traceback
import logging

class PaperTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        self.tp, self.w1 = add_user_data()
        self.p1_id = add_paper_data(self.w1)
        self.client=Client()

    '''
    def assertRaises(self, exception):
        print exception.error_code
    '''

    def test_alllinks(self):
        '''
        with self.assertRaises(someexception) as cm:
        '''
        #LOGIN STATE  as teacher
        self.assertTrue(self.client.login(username='weiyan', password='1'))
        #getall paper
        response = self.client.get('/paper/getall/')
        self.assertEqual(response.status_code,200)

        #add paper
        response = self.client.get('/paper/add/')
        self.assertEqual(response.status_code,200)

        #getquestions
        response = self.client.post('/paper/getquestions/',{'paperid':'1', }, follow= True)
        self.assertEqual(response.status_code,200)
        '''
        negtive trial
        '''
        try:
            response = self.client.post('/paper/getquestions/', follow= False )
        except MultiValueDictKeyError:
            self.logger.info("Passing MultiValueDictKeyError")
        else:
            self.assertTrue(False)
        #paper delete

        response = self.client.post('/paper/delete/',{'paperid':self.p1_id, 'view':'1'}, follow= True)
        self.assertEqual(response.status_code,200)
        try:
            response = self.client.post('/paper/delete/', follow= False)
        except MultiValueDictKeyError:
            self.logger.info("Passing MultiValueDictKeyError")
        else:
            self.assertTrue(False)
        response = self.client.post('/paper/delete/',{'paperid':'22', 'view':'1'}, follow= True)
        self.assertEqual(response.status_code,404)

        self.client.logout()

        self.logger.info("test_alllinks finished")

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
    w1sp=SProfile.objects.create(user=w1,gender="male",cellphone="13671670930",teacher=weiyantp)
    return weiyantp, w1

def add_paper_data(owner):
    p1 = Paper.objects.create(papername='p1',owner=owner, passpoint=60)
    return p1.id
