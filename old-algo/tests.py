from django.test import TestCase
from django.utils import unittest
import logging
from standard import Standard
from markscheme import MarkScheme
from algo.answer import Answer
import os
import re
import nltk
import math
import pprint
import random
from django.conf import settings


def overrides(interface_class):

    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


class abStandard(Standard):

    @overrides(Standard)
    def CalVector(self, sentencelist):
        text_words = []
        for id, sentence in enumerate(sentencelist):
            raw = self.ParseKeyword(sentence['KeyS'])
            text = nltk.word_tokenize(raw)
            stopwords_list = nltk.corpus.stopwords.raw('english').split()
            '''
            words = list(nltk.corpus.wordnet.morphy(word.lower())
                         for word, tag in nltk.pos_tag(text)
                         if (tag.startswith('V') or tag == 'NN' or tag == 'NNS')
                         and word not in stopwords_list)
            '''
            words = [nltk.corpus.wordnet.morphy(word.lower())
                     for (word, tag) in nltk.pos_tag(text)
                     if (tag.startswith('V') or tag.startswith('NN') or tag == 'JJ' or tag == 'DET' or tag == 'RB')
                     and word not in stopwords_list]
            sentence['SenWords'] = list(word for word in words if word)
            text_words += sentence['SenWords']
        textfdist = nltk.FreqDist(text_words)
        return textfdist

    @overrides(Standard)
    def SentenceCal(self, sentencelist, textfdist):
        for sentence in sentencelist:
            #text = nltk.word_tokenize(sentence['KeyS'])
            fdist = nltk.FreqDist(sentence['SenWords'])
            senvec = {}
            sen_len = len(sentencelist)
            for word in sorted(textfdist):
                if fdist[word]:
                    #the frequency of sentence which contains this word in all sentencelist
                    sentencefreq = sum(1 for senten in sentencelist if word in senten['SenWords'])
                    senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * sen_len / sentencefreq)
                    #senvec[word] = (1 + math.log(1.0 * fdist[word])) * math.log(1.0 * sen_len / sentencefreq)
                else:
                    senvec[word] = 0
            sentence['KeySVec'] = senvec
        return sentencelist


class abAnswer(Answer):

    @overrides(Answer)
    def __init__(self, **kwargs):
        self.dist_threshold = kwargs.get('dist_threshold') or 0.3
        self.multisen_matchrate = kwargs.get('multisen_matchrate') or 0.3
        self.sen_threshold = kwargs.get('sen_threshold') or 0.15
        self.multisen_threshold = kwargs.get('multisen_threshold') or 0.4
        nltk.data.path = [settings.NLTKDATAPATH]

    @overrides(Answer)
    def SentenceAnalysis(self, fulltext, textfdist):
        ans_sentencelist = []
        text = fulltext.replace('\n', ' ')
        #p = re.compile(r'.+\.')
        p = re.compile(r'([\w\"\'\<\(][\S ]+?[\.!?])[ \n\"]')
        keysen = p.findall(text)
        sen_no = 0
        for sen in keysen:
            sen_no += 1
            text = nltk.word_tokenize(sen)
            text_words = list(nltk.corpus.wordnet.morphy(word.lower()) for (word, tag) in nltk.pos_tag(text))
            ans_sentencelist.append({'StuS': sen,
                                     'StuWords': list(word for word in text_words if word),
                                     'No': sen_no})
        for sentence in ans_sentencelist:
            fdist = nltk.FreqDist(sentence['StuWords'])
            senvec = {}
            for word in sorted(textfdist):
                if fdist[word]:
                    wordfreq = sum(1 for senten in ans_sentencelist if word in senten['StuWords'])
                    senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * len(keysen) / wordfreq)
                    #senvec[word] = (1 + math.log(1.0 * fdist[word])) * math.log(1.0 * len(keysen) / wordfreq)
                else:
                    senvec[word] = 0
            sentence['StuSVec'] = senvec
        return ans_sentencelist

    @overrides(Answer)
    def CalCosDist(self, ans_sentencelist, std_sen):
        match_sen = None
        max_cos = 0

        '''
        def pearson(ans_sentencelist, std_sen):
            n = len(std_sen['KeySVec'])
            sum_stu = sum(stu_sen['StuSVec'][word] for word in std_sen['KeySVec'] for stu_sen in ans_sentencelist)
            sum_std = sum(std_sen['KeySVec'][word] for word in std_sen['KeySVec'])
            sum_stu_sq = sum(stu_sen['StuSVec'][word] ** 2 for word in std_sen['KeySVec'] for stu_sen in ans_sentencelist)
            sum_std_sq = sum(std_sen['KeySVec'][word] ** 2 for word in std_sen['KeySVec'])
            psum = sum(stu_sen['StuSVec'][word] * std_sen['KeySVec'][word] for word in std_sen['KeySVec'] for stu_sen in ans_sentencelist)
            num = psum - (sum_stu * sum_std / n)
            den = ((sum_stu_sq - math.pow(sum_stu, 2) / n) * (sum_std_sq - math.pow(sum_std, 2) / n)) ** .5
            if den == 0:
                return 1
            r = num / den
            return r
        print pearson(ans_sentencelist, std_sen)
        '''

        for stu_sen in ans_sentencelist:
            q, s, qs = 0, 0, 0
            for word in std_sen['KeySVec']:
                q += std_sen['KeySVec'][word] * std_sen['KeySVec'][word]
                s += stu_sen['StuSVec'][word] * stu_sen['StuSVec'][word]
                qs += std_sen['KeySVec'][word] * stu_sen['StuSVec'][word]
            if q == 0 or s == 0:
                qs_cos = 0
            else:
                qs_cos = qs / (math.sqrt(q * s))
            stu_words = [word for word in stu_sen['StuSVec'] if stu_sen['StuSVec'][word] > 0]
            if qs_cos > max_cos and len(stu_words) > 0:
                max_cos = qs_cos
                match_sen = stu_sen
        return max_cos, match_sen



#@unittest.skip("Too much time")
class AlgorithmTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)

    @unittest.skip("Too much time")
    def test_standard(self):
        self.logger.info("Test Standard Answer Analysis")
        testStandardAnswerFile = "ans_Q1.txt"
        filePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        self.logger.info("filepath:%s" % filePath)
        if not os.path.isfile(filePath):
            self.logger.error("Test file doesn't exist:%s" % testStandardAnswerFile)
            assert False
        fh = file(filePath, "r")
        filetext = fh.read()
        fh.close()
        sinst = Standard()
        pointlist, textfdist, slist = sinst.Analysis(filetext)
        #for word,freq in textfdist.items():
        #    print "%s:%d" % (word,freq)
        pprint.pprint(slist)
        self.logger.info("Test Standard Answer Analysis finished")

    @unittest.skip("Too much time")
    def test_markscheme(self):
        self.logger.info("Test Marking Scheme Analysis/Rule Generation")

        mockplist = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P3.4']
        mocktemplates = ""
        #Negative
        mocktemplates += 'all except P3 and P22,8,'
        mocktemplates += 'only P1 or Ps,1,'
        mocktemplates += 'only some from all,8,'
        mocktemplates += 'only 2 from all,8,'
        #Positive
        mocktemplates += 'all less two combination of p1 and p2 and p3 and p4\
                and p5 and p6 and p7 and p8 and p9 and p10 and 11'
        mocktemplates += 'all less P5,8,'
        mocktemplates += 'all less P3 and P22 or P4 and P5 or P6 or P7,8,'
        mocktemplates += 'all,10,'
        mocktemplates += 'only P1 or P6 and P7 and P4 or P88 or P89 or P90 and P2,8,'
        mocktemplates += 'only P1 or P3.4,8,'
        mocktemplates += 'any 2 combinations of P1;P3;P5;P99;P7,8,'
        mocktemplates += 'any 2 combinations of P1;P3;P5;P99;P7 and \
                any 1 combinations of P4;P6 and any 3 combinations of P2;P3.4,8,'
        mocktemplates += 'less 2 combinations of P1;P3;P5;P99;P7 and\
                less 1 combinations of P4;P6 and less 3 combinations of P2;P3.4,8,'
        mocktemplates += 'all less 2 combinations of P1;P3;P5;P9,1,'
        mocktemplates += 'all less 0 combinations of P1;P3;P5;P9,1,'
        mocktemplates += 'all less -1 combinations of P1;P3;P5;P9,1,'

        #be careful, last case has no trailing comma
        mocktemplates += 'all less 4 combinations of P1;P3;P5,1'
        ms = MarkScheme(mockplist)
        rulelist = ms.GetRules(mocktemplates)
        pprint.pprint(rulelist)
        self.logger.info("Test Marking Scheme Analysis/Rule Generation Finished")

    @unittest.skip("Too much time")
    def test_answer(self):
        self.logger.info("Test Student Answer Analysis")

        testStandardAnswerFile = "ans_Q1.txt"
        stdFilePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        self.logger.info("stdanswer filepath:%s" % stdFilePath)
        if not os.path.isfile(stdFilePath):
            self.logger.error("Standard Test file doesn't exist:%s" % testStandardAnswerFile)
            assert False
        fh = file(stdFilePath, "r")
        stdtext = fh.read()
        fh.close()

        sinst = Standard()
        pointlist, textfdist, slist = sinst.Analysis(stdtext)
        std_pointlist_no = [point['Point_No'] for point in pointlist]
        self.logger.info("Points:%s" % std_pointlist_no)

        testAnswerFile = "ans_Q1.txt"
        ansFilePath = os.path.join("algo/testdata/raw/Q1", testAnswerFile)
        self.logger.info("answer filepath:%s" % ansFilePath)
        if not os.path.isfile(ansFilePath):
            self.logger.error("Answer file doesn't exist:%s" % testAnswerFile)
            assert False
        fh = file(ansFilePath, "r")
        anstext = fh.read()
        fh.close()

        mockrulelist = [
            {'Mark': 10, 'Point': ['P1.1', 'P1.2', 'P1.3', 'P2', 'P3', 'P4', 'P5']},
            {'Mark': 7, 'Point': ['P1.1', 'P2', 'P3', 'P4', 'P5']},
            {'Mark': 6, 'Point': ['P1.1', 'P2', 'P3', 'P4']},
            {'Mark': 5, 'Point': ['P1.1', 'P2', 'P3']},
            {'Mark': 3, 'Point': ['P1.1', 'P2']},
            {'Mark': 2, 'Point': ['P1.1']}]
        pprint.pprint(mockrulelist)

        ans = Answer()
        mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, mockrulelist)
        pprint.pprint(mark)
        pprint.pprint(ommited)
        self.logger.info("Test Student Answer Analysis Finished")

    def __parsescheme(self, rawschemes):
        rawschemelist = rawschemes.split(',')
        txtschemelist = []
        if len(rawschemelist) >= 2:
            for i in range(0, len(rawschemelist), 2):
                str1 = str(rawschemelist[i])
                str2 = str(rawschemelist[i + 1])
                txtschemelist.append([str1, str2])
        txtschemelist.sort(key=lambda x: int(x[1]), reverse=True)
        return txtschemelist

    def __updaterulelist(self, scheme, pointlist):
        txtplist = list(point['Point_No'] for point in pointlist if 'P0.' not in point['Point_No'])
        txtrulelist = []
        if txtplist:
            try:
                ms = MarkScheme(txtplist)
                txtrulelist = list(rule for rule in ms.GetRules(scheme))
            except:
                pass
        return txtrulelist

    def parse_Q1(self):
        testStandardAnswerFile = "ans_Q1.txt"
        filePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        self.logger.info("filepath:%s" % filePath)
        if not os.path.isfile(filePath):
            self.logger.error("Test file doesn't exist:%s" % testStandardAnswerFile)
            assert False
        fh = file(filePath, "r")
        filetext = fh.read()
        fh.close()
        sinst = abStandard()
        pointlist, textfdist, slist = sinst.Analysis(filetext)
        rulelist = [{'Mark': 10, 'Point': ['P1.1', 'P1.2', 'P2', 'P3', 'P4', 'P5', 'P6']},
                    {'Mark': 9, 'Point': ['P2', 'P1.1', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P1.2', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5', 'P1.2']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5', 'P1.1']},
                    {'Mark': 9, 'Point': ['P3', 'P6', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 8, 'Point': ['P3', 'P6', 'P4', 'P5']},
                    {'Mark': 7, 'Point': ['P2', 'P6', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 6, 'Point': ['P6', 'P4', 'P5']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P6', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P6', 'P4', 'P1.2', 'P1.1']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P4', 'P1.2']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P1.2', 'P5']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P6', 'P1.2']},
                    {'Mark': 3, 'Point': ['P2', 'P3', 'P1.1', 'P1.2']},
                    {'Mark': 2, 'Point': ['P3', 'P1.2']},
                    {'Mark': 2, 'Point': ['P3', 'P1.1']},
                    {'Mark': 2, 'Point': ['P1.2', 'P1.1']},
                    {'Mark': 1, 'Point': ['P1.1']},
                    {'Mark': 1, 'Point': ['P1.2']},
                    {'Mark': 1, 'Point': ['P2']},
                    {'Mark': 1, 'Point': ['P3']}]
        return pointlist, textfdist, slist, rulelist

    @unittest.skip("Too much time")
    def test_Q1_single(self):
        pointlist, textfdist, slist, rulelist = self.parse_Q1()
        ans = abAnswer()
        ansfile = 'algo/testdata/raw/Q1/Q1_SS16.docx.txt'
        fh = file(ansfile, "r")
        anstext = fh.read()
        fh.close()
        manualmark = 1
        mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
        err = mark - manualmark
        print("%s\t%d\t%s\t%d" % (ansfile, mark, marklist, err))

    #@unittest.skip("Too much time")
    def test_Q1_all(self):
        pointlist, textfdist, slist, rulelist = self.parse_Q1()
        manuallist = [9, 7, 9, 7, 7, 10, 7, 7, 7, 7, 7, 1, 2, 2, 0, 1, 2, 2, 1, 1, 8, 9, 4, 9, 7, 9, 0, 7, 4, 10, 7, 7]
        minmaxerr = 0
        minrd = 0
        minerrcount = 0
        for i in range(10):
            maxerr = 0
            errcount = 0
            var = 0
            rd = random.uniform(0.32, 0.36)
            print rd
            ans = abAnswer(dist_threshold=rd, multisen_matchrate=0.3, sen_threshold=rd, multisen_threshold=0.4)
            for root, dirs, files in os.walk('algo/testdata/raw/Q1'):
                if 'Standard' in dirs:
                    dirs.remove('Standard')
                for idx in range(0, 32):
                    ansfile = 'Q1_SS' + str(idx + 1) + '.docx.txt'
                    filePath = os.path.join(root, ansfile)
                    fh = file(filePath, "r")
                    anstext = fh.read()
                    fh.close()
                    mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
                    err = mark - manuallist[idx]
                    maxerr += math.fabs(err)
                    var += err ** 2
                    errcount += 1 if math.fabs(err) > 3 else 0
                    print("%s\t%d\t%s\t%d" % (ansfile, mark, marklist, err))
                    if errcount < minerrcount:
                        minerrcount = errcount
                        minmaxerr = maxerr
                        minrd = rd
            print "maxerr:%d, maxvar:%d, errcount:%d" % (maxerr, var, errcount)
        print "minmaxerr:%d rd:%d count:%d" % (minmaxerr, minrd, minerrcount)

    def __traversal_process(self, testdir):
        ans = Answer()
        for root, dirs, files in os.walk(testdir):
            if 'Standard' in dirs:
                dirs.remove('Standard')
            for stdfile in files:
                if 'ans' in stdfile:
                    testno = stdfile[4:-4]
                    self.logger.info("no:%s" % testno)
                    stdPath = os.path.join(root, stdfile)
                    if not os.path.isfile(stdPath):
                        self.logger.error("Test file doesn't exist:%s" % stdfile)
                        assert False
                    fh = file(stdPath, "r")
                    filetext = fh.read()
                    fh.close()
                    sinst = Standard()
                    pointlist, textfdist, slist = sinst.Analysis(filetext)
                    schemename = 'scheme_' + testno + '.txt'
                    schemepath = os.path.join(root, schemename)
                    fr = file(schemepath, 'r')
                    scheme = self.__parsescheme(fr.read())
                    fr.close()
                    rulelist = self.__updaterulelist(scheme, pointlist)
                    for idx in range(0, 10):
                        ansfile = 'stud' + str(idx + 1) + '_' + testno + '.txt'
                        ansPath = os.path.join(root, ansfile)
                        if os.path.isfile(ansPath):
                            fa = file(ansPath, 'r')
                            anstext = fa.read()
                            fa.close()
                            if anstext:
                                mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
                            else:
                                mark = 0
                                marklist = []
                            print("%s\t%d\t%s" % (ansfile, mark, marklist))

    @unittest.skip("Too much time")
    def test_Q2(self):
        self.__traversal_process('algo/testdata/raw/Q2')

    @unittest.skip("Too much time")
    def test_Q3(self):
        self.__traversal_process('algo/testdata/raw/Q3')

    @unittest.skip("Too much time")
    def test_Q4(self):
        self.__traversal_process('algo/testdata/raw/Q4')
