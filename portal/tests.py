from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group,Permission
from portal.models import TProfile,SProfile
from portal.forms import InfoModForm
import logging
import re

class PortalTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        add_groups_data()
        add_user_data()
        self.client=Client()
        self.infoModForm = {
                'username':'weiyan',
                'newpassword':'2',
                'newpasswordc':'2',
                'email':'weiyan@gmail.com'
                }

    def test_forms(self):
        f = InfoModForm({})
        self.assertFalse(f.is_valid())
        f = InfoModForm(self.infoModForm)
        self.assertTrue(f.is_valid())
        self.logger.info("test_forms finished")

    def test_alllinks(self):
        #login page
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/',{'username':'yan','password':'12'},follow=False)
        self.assertTemplateUsed(response, 'login.html')
        self.assertEqual(response.status_code,200)

        #register page
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'register.html')
        response = self.client.post('/accounts/register/',{'username':'yan','password':'12'},follow=False)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'register.html')

        #forgot password page
        response = self.client.get('/accounts/forgot-password/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/accounts/forgot-password/',{'username':'yan','password':'12'},follow=False)
        self.assertEqual(response.status_code,200)

        #LOGIN STATE  as teacher
        self.assertTrue(self.client.login(username='weiyan', password='1'))
        self.assertFalse(self.client.login(username='weiyan', password='2'))

        #home page
        response = self.client.get('/home/')
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/teacher/index/')

        #teacher index page
        response = self.client.get('/teacher/index/')
        self.assertEqual(response.status_code,200)

        #info modify page
        response = self.client.get('/accounts/info-modify/')
        self.assertEqual(response.status_code,200)

        #LOGOUT STATE
        self.client.logout()

        #LOGIN STATE  as student
        self.assertTrue(self.client.login(username='w1', password='1'))

        #student index page
        response = self.client.get('/student/index/')
        self.assertEqual(response.status_code,200)

        #info modify page
        response = self.client.get('/accounts/info-modify/')
        self.assertEqual(response.status_code,200)
        response = self.client.post('/accounts/info-modify/', follow=False)
        self.assertEqual(response.status_code,200)

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
