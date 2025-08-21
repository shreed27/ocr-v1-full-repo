#!/usr/bin/env python
from docx import opendocx, getdocumenttext
import logging
import logging.config
import os

class ConvertDocx(object):

    def __init__(self):
        logging.config.fileConfig("logging.conf")
        self.logger=logging.getLogger(__name__)

    def convert(self,filein,fileout):
        if filein[-4:] == "docx":
            self.logger.info("Convert this file:%s" % filein)
            document = opendocx(filein)
            paratextlist = getdocumenttext(document)
            newfile = open(fileout, 'w')
            newparatextlist = []
            for paratext in paratextlist:
                newparatextlist.append(paratext.encode('utf-8'))
            newfile.write('\n\n'.join(newparatextlist))
            newfile.write('\n\n')
            newfile.close()
        elif filein[-3:] == "doc":
            self.logger.info("Convert this file:%s" % filein)
            os.system('catdoc %s > %s' % (filein, fileout))
        else:
            self.logger.info("Cannot convert this file:%s" % filein)
            return
        self.logger.info("Convert finished")


if __name__=="__main__":
    import sys
    if len(sys.argv) !=3:
        print "Usage: ./convertdocx.py input output"
        sys.exit(0)
    else:
        cd=ConvertDocx()
        cd.convert(sys.argv[1],sys.argv[2])
