from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile
from itempool.models import Itempool
from question.models import Question
import traceback
import logging
from django.utils.datastructures import MultiValueDictKeyError

class ItempoolTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        teacher = add_user_data()
        add_itempool_data(teacher)
        self.client=Client()

    def test_alllinks(self):
        #login
        self.assertTrue(self.client.login(username='weiyan', password='1'))
        self.assertFalse(self.client.login(username='weiyan', password='2'))

        #add itempool
        response = self.client.get('/itempool/add/')
        self.assertEqual(response.status_code,200)

        response = self.client.get('/itempool/add/?itempoolid=1')
        self.assertEqual(response.status_code,200)

        #getall itempool
        response = self.client.get('/itempool/getall/')
        self.assertEqual(response.status_code,200)

        #getquestions
        response = self.client.get('/itempool/getquestions/?itempoolid=1')
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'q1', status_code = 200)

        #updataname
        response = self.client.get('/itempool/updatename/?itempoolid=1&itempoolname=i3x')
        self.assertContains(response,'i3x', status_code=200)

        #delete
        response = self.client.post('/itempool/delete/',{'itempoolid':'1'}, follow= True)
        
        try:
            response = self.client.post('/itempool/delete/', follow= False )
        except MultiValueDictKeyError:
            self.logger.info("Passing MultiValueDictKeyError")
        else:
            self.assertTrue(False)

        self.assertEqual(response.status_code,200)

        #getquestions
        response = self.client.get('/itempool/getquestions/?itempoolid=1')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response, 'q1', status_code = 200)

        #updataname
        response = self.client.get('/itempool/updatename/?itempoolid=1&itempoolname=i3i')
        self.assertEqual(response.status_code,404)

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

def add_itempool_data(teacher):
    i1=Itempool.objects.create(poolname='i1', teacher=teacher)
    question = Question.objects.create(qname='q1', itempool=i1, teacher=teacher)

