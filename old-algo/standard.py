import logging
from django.conf import settings
import re
import nltk
import math


class Standard:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        nltk.data.path = [settings.NLTKDATAPATH]
        self.pointtext_pattern = re.compile(r'^\d.+\n', re.M)
        self.keysen_pattern = re.compile(r'.+\.')
        self.keyword_pattern = re.compile(r'\(\(\((.+?)\)\)\)')
        self.choice_pattern = re.compile(r'\s[A-Z]\s')

    def PointAnalysis(self, fulltext):
        pointlist = []
        text = fulltext.replace('\t', '')
        m = self.pointtext_pattern.findall(text)
        for i in range(0, len(m)):
            num = re.search(r'^(\d+(\.\d)?\s\.)*', m[i]).group()
            pointlist.append({'Point_No': 'P' + str(num)[:-2],
                             'Point_Text': m[i][len(num):].replace('\n', ' ')})
        return pointlist

    def SentenceAnalysis(self, pointlist):
        sentencelist = []
        sen_no = 0
        pointsen_no = {}
        for point in pointlist:
            pointsen_no.setdefault(point['Point_No'], [])
            point_text = point['Point_Text']
            #p = re.compile(r'([\w\"\'\(].+?\.\)?)[ \"\n]')
            keysen = self.keysen_pattern.findall(point_text)
            for i in range(0, len(keysen)):
                sen_no += 1
                pointsen_no[point['Point_No']].append(sen_no)
                keyword = self.keyword_pattern.findall(keysen[i])
                #keyword += [choice.strip(' ') for choice in self.choice_pattern.findall(keysen[i])]
                sentencelist.append({'KeyS': keysen[i], 'KeyBVec': keyword,
                                     'Point_No': point['Point_No'], 'No': sen_no})
        for sen in sentencelist:
            sen.setdefault('TotalS_No', pointsen_no.get(sen['Point_No']))
        return sentencelist

    def ParseKeyword(self, text):
        special = {'<': ' ', '>': '', '(': '',
                   ')': '', '.': '', ',': '',
                   '""': ''}
        for (k, v) in special.items():
            text = text.replace(k, v)
        return text

    def CalVector(self, sentencelist):
        text_words = []
        for sentence in sentencelist:
            raw = self.ParseKeyword(sentence['KeyS'])
            text = nltk.word_tokenize(raw)
            stopwords_list = nltk.corpus.stopwords.raw('english').split()
            # word.lower() + '/' + tag
            words = list(nltk.corpus.wordnet.morphy(word.lower())
                         for word, tag in nltk.pos_tag(text)
                         if (tag.startswith('V') or tag.startswith('NN') or tag == 'JJ' or tag == 'DET' or tag == 'RB')
                         and word not in stopwords_list)
            sentence['SenWords'] = list(word for word in words if word)
            text_words += sentence['SenWords']
        textfdist = nltk.FreqDist(text_words)
        return textfdist

    def SentenceCal(self, sentencelist, textfdist):
        for sentence in sentencelist:
            #text = nltk.word_tokenize(sentence['KeyS'])
            # word.lower() + '/' + tag
            fdist = nltk.FreqDist(sentence['SenWords'])
            senvec = {}
            sen_len = len(sentencelist)
            for word in sorted(textfdist):
                if fdist[word]:
                    #the frequency of sentence which contains this word in all sentencelist
                    sentencefreq = sum(1 for senten in sentencelist if word in senten['SenWords'])
                    senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * sen_len / sentencefreq)
                else:
                    senvec[word] = 0
            sentence['KeySVec'] = senvec
        return sentencelist

    def Analysis(self, fulltext):
        pointlist = self.PointAnalysis(fulltext)
        sentencelist = self.SentenceAnalysis(pointlist)
        textfdist = self.CalVector(sentencelist)
        slist = self.SentenceCal(sentencelist, textfdist)
        return pointlist, textfdist, slist
