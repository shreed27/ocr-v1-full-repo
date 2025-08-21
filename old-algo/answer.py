import re
import nltk
import math
from django.conf import settings
import logging


class Answer:

    def __init__(self):
        self.dist_threshold = 0.25
        self.multisen_matchrate = 0.3
        self.sen_threshold = 0.33
        self.multisen_threshold = 0.4
        self.logger = logging.getLogger(__name__)
        nltk.data.path = [settings.NLTKDATAPATH]

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
                else:
                    senvec[word] = 0
            sentence['StuSVec'] = senvec
        return ans_sentencelist

    def CalCosDist(self, ans_sentencelist, std_sen):
        match_sen = None
        max_cos = 0
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

    def Mark(self, std_sentencelist, std_pointlist_no, ans_sentencelist):
        detailedmarklist = []
        marklist = []
        for point_no, std_sen in zip(std_pointlist_no, std_sentencelist):
            if 'P0.' in point_no:
                continue
            std_senlist = []
            stu_senlist = []
            keyword_num = 0
            keyword_sum = 0
            sen_match = 0
            len_match = 0
            std_senlist = std_sen['KeyS'].split('.')
            keyword_sum += len(std_sen['KeyBVec'])
            max_cos, match_sen = self.CalCosDist(ans_sentencelist, std_sen)
            if max_cos > self.dist_threshold:
                sen_match += max_cos
                len_match += 1
                if std_sen['KeyBVec']:
                    keyword_freq = sum(1 for keyword in std_sen['KeyBVec']
                                        if keyword.lower() in match_sen['StuS'].lower())
                    keyword_num += keyword_freq
                    keyword_match = 1.0 * keyword_freq / len(std_sen['KeyBVec'])
                else:
                    keyword_match = None
                stu_senlist.append({'StdNo': std_sen['No'],
                                    'Max_Match': std_sen.get('TotalS_No'),
                                    'Stu': match_sen['StuS'], 'Mat_Deg': max_cos,
                                    'Keyword_Match': keyword_match})

            if std_senlist and len_match:
                keyword_rate = 1.0 * keyword_num / keyword_sum if keyword_sum > 0 else 0
                sen_rate = 1.0 * sen_match
                #sen_rate = 1.0 * sen_match / math.log(len(std_senlist) + 1)
                #moderate
                sen_rate_match = 1.0 * sen_match / len_match if (1.0 * len_match / len(std_senlist) > self.multisen_matchrate) and len(std_senlist) > 1 else 0
                #loose
                #sen_rate_match = 1.0 * sen_match / len_match if (1.0 * len_match / len(std_senlist) > self.multisen_matchrate) and len(std_senlist) > 1 else 0
            else:
                sen_rate = 0
                sen_rate_match = 0
                keyword_rate = 0
            '''
            # xiangguandu juzi
            print "Point_No:", point_no
            print 'stdsen:', std_sen['No'], '---', std_sen['KeyS']
            print 'stdvec:', std_sen['KeySVec']
            print 'stusen:', match_sen['No'], '---', match_sen['StuS']
            print 'stuvec:', match_sen['StuSVec']
            print 'Max Relevance:', sen_rate
            #print 'Relevant Keyword:', [word for word in match_sen['StuSVec'] if match_sen['StuSVec'][word] > 0]
            '''

            detailedmarklist.append({'Point_No': point_no,
                                     'Std_senList': std_senlist,
                                     'Stu_SenList': stu_senlist,
                                     'Keyword_Rate': keyword_rate,
                                     'Sentence_Rate': sen_rate,
                                     'Sentence_Rate_Match': sen_rate_match})
        marklist = list(point['Point_No'] for point in detailedmarklist
                        if point['Sentence_Rate'] > self.sen_threshold
                        or point['Sentence_Rate_Match'] > self.multisen_threshold)
        return marklist

    def Comparison(self, marklist, rulelist):
        match = True
        for rule in rulelist:
            for point in rule['Point']:
                if point not in marklist:
                    match = False
            if match:
                return rule['Mark'], rule['Point']
            else:
                match = True
        return 0, None

    def Omitted(self, marklist, std_pointlist, rulelist):
        mark, rule = self.Comparison(marklist, rulelist)
        omitted = []
        for point in std_pointlist:
            if 'P0.' not in point['Point_No']:
                if point['Point_No'] in marklist:
                    omitted.append('C' + point['Point_No'][1:] + point['Point_Text'])
                else:
                    omitted.append('W' + point['Point_No'][1:] + point['Point_Text'])
        return mark, omitted

    def Analysis(self, fulltext, textfdist, std_sentencelist, std_pointlist, rulelist):
        if not fulltext or not textfdist or not std_sentencelist or not std_pointlist or not rulelist:
            return None, None, None
        ans_sentencelist = self.SentenceAnalysis(fulltext, textfdist)
        std_pointlist_no = list(point['Point_No'] for point in std_pointlist)
        marklist = self.Mark(std_sentencelist, std_pointlist_no, ans_sentencelist)
        mark, omitted = self.Omitted(marklist, std_pointlist, rulelist)
        return mark, marklist, omitted


class ImageAnswer(object):
    def __init__(self,):
        self.logger = logging.getLogger(__name__)

    def Comparison(self, marklist, rulelist):
        match = True
        for rule in rulelist:
            for point in rule['Point']:
                if point not in marklist:
                    match = False
            if match:
                return rule['Mark'], rule['Point']
            else:
                match = True
        return 0, None

    def Omitted(self, marklist, std_pointlist, rulelist):
        mark, rule = self.Comparison(marklist, rulelist)
        omitted = []
        for point in std_pointlist:
            if 'P0.' in point['Point_No']:
                if point['Point_No'] in marklist:
                    omitted.append('C' + point['Point_No'][1:] + point['Point_Text'])
                else:
                    omitted.append('W' + point['Point_No'][1:] + point['Point_Text'])
        return mark, omitted

    def Analysis(self, imgpoints, std_pointlist, rulelist):
        if imgpoints:
            marklist = list(imagepoint['Point_No'] for imagepoint, stuansimage in imgpoints)
            mark, omitted = self.Omitted(marklist, std_pointlist, rulelist)
            return mark, marklist, omitted
