import logging
from scheme_lang import *


class MarkScheme(object):

    def __init__(self, plist):
        self.logger = logging.getLogger(__name__)
        self.sc = MarkingSchemeLang(plist)
        self.plist = plist

    '''def filterZero(self,string):
        string = string.group(0)
        if string[2] == '0':
            return 'P'+string[0]
        else:
            return 'P'+string'''

    def GetRules(self, templates):
        for rule, mark in templates:
            rlist = self.sc.analysis(rule, int(mark))
            for rule, score in rlist:
                yield {'Point': rule, 'Mark': score}
