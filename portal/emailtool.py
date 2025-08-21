#!/usr/bin/env python

import smtplib
from email.MIMEText import MIMEText
import time
from django.conf import  settings
import logging

class EmailTool(object):
    def __init__(self):
        self.logger=logging.getLogger(__name__)
        self.from_addr = settings.EMAIL_HOST_USER
        self.mailpass = settings.EMAIL_HOST_PASSWORD
        self.host=settings.EMAIL_HOST
        self.port=settings.EMAIL_PORT
        self.useTLS=settings.EMAIL_USE_TLS

    def getFormatedTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))


    def send(self,to_addr,text):
        smtp=smtplib.SMTP(timeout=60)
        self.logger.warn("smtp server connecting...")

        #smtp.set_debuglevel(1)

        try:
            smtp.connect(self.host,self.port)
        except:
            self.logger.error("server connect error...")
            return

        if self.useTLS:
            smtp.starttls()
        try:
            smtp.login(self.from_addr,self.mailpass)
        except:
            self.logger.error("account logging error...")
            smtp.quit()
            return

        msg = MIMEText(text,"html")
        msg['From']=self.from_addr
        msg['To']=",".join(to_addr)
        msg['Subject']="[INTEMASS]System Notification"
        smtp.sendmail(self.from_addr,to_addr,msg.as_string())
        smtp.quit()
        self.logger.info("Email Notification Sent At [%s]" % self.getFormatedTime())
