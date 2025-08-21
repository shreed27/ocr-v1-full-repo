from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile,SProfile
import logging
import re

class ReportTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        add_user_data()
        self.client=Client()

    def test_alllinks(self):
        #LOGIN STATE  as teacher
        self.assertFalse(self.client.login(username='weiyan', password='2'))
        self.assertTrue(self.client.login(username='weiyan', password='1'))

        #report_teacher
        response = self.client.get('/report/teacher/')
        self.assertEqual(response.status_code,200)

        #report_student
        response = self.client.get('/report/student/')
        self.assertEqual(response.status_code,302)

        #report_studentanswer
        response = self.client.get('/report/studentanswer/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/report/studentanswer/')
        self.assertEqual(response.status_code,200)


        #LOGOUT STATE
        self.client.logout()
        self.logger.info("test_alllinks finished")

    def test_login(self):
        self.assertTrue(self.client.login(username='weiyan', password='1'))
        response = self.client.post('/',{'username':'weiyan','password':'1'},follow=True)
        self.assertEqual(response.status_code,200)
        chain=response.redirect_chain
        #self.logger.info("Chain:%s" % chain)
        arr0=re.split("/",chain[0][0])
        arr0=[a for a in arr0 if a.strip()!=""]
        self.assertEqual(arr0[-1],"home")
        arr1=re.split("/",chain[1][0])
        arr1=[a for a in arr1 if a.strip()!=""]
        self.assertEqual(arr1[-1],"index")
        self.assertEqual(arr1[-2],"teacher")
        self.logger.info("test_login finished")

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


# Yet to be implemented.
class ClosenessReportTest(TestCase):
    """
    test the ClosenessReport functionalities from view function.
    """

    def setUp(self):
        pass

    def testReport(self):
        # 1. get the assignment
        # 2. get the closeness record points
        # 3. check whether all can be updated on student submit answer
        # 4. Test the functions individually for the capabilites
        pass

    def tearDown(self):
        pass
