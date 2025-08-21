#! /usr/bin/python
#
# tests.py: System tests for essay grading algorithm.
#

# tests.py: 
from django.test import TestCase
from django.utils import unittest
import logging
from standard import Standard
from markscheme import MarkScheme
## OLD: from algo.answer import Answer
from answer import Answer
import os
import re
import nltk
import math
import pprint
import random
from django.conf import settings

# Note: following is used for invoking tests directly. This requires unittest2 in order
# to be compatible with Python versions less than 2.7
import unittest2

from common import *
debug_print("algo/tests.py start: " + debug_timestamp())

#------------------------------------------------------------------------
# Globals

# Analyze correspondence annotations (e.g., [[s1c => k2a]]
CHECK_LINKAGES = getenv_boolean("CHECK_LINKAGES", False)

# Allow for correspondence annotations without square brackets (provided on line by itself)
ALLOW_LOOSE_ANNOTATIONS = getenv_boolean("ALLOW_LOOSE_ANNOTATIONS", False)

# Ratio of character offset overlap for lines to be considered a match
OVERLAP_THRESHOLD = getenv_number("OVERLAP_THRESHOLD", 0.5)

# Number of times to test each student repsonse for question 1
NUM_TRIALS = getenv_int("NUM_TRIALS", 10)

# Maximum number of essays to process  (n.b., use only to speed up debugging)
MAX_ESSAYS = getenv_int("MAX_ESSAYS", 32)

# Whether to exclude units tests known to take a while (i.e. most of them!)
EXCLUDE_LONG_TESTS = __debug__ and getenv_boolean("EXCLUDE_LONG_TESTS", True)

# Skip the class overrides defined here for Standard and Answer (on by default)
SKIP_OVERRIDES = __debug__ and getenv_boolean("SKIP_OVERRIDES", False)
USE_OVERRIDES = (not SKIP_OVERRIDES)

# Whether test_Q1_all applies random sentence matching thresholds (on by default)
RANDOM_THRESHOLDS = getenv_boolean("RANDOM_THRESHOLDS", True)

# Random seed to use (if nonzero)
RANDOM_SEED = getenv_int("RANDOM_SEED", 0)

# Use the student frequent distirbution for global documents counts (not teacher)
USE_STUDENT_TEXT_DIST = __debug__ and getenv_boolean("USE_STUDENT_TEXT_DIST", False)

#------------------------------------------------------------------------

# Defines overrides method for @overrides annotation
# TODO: Just define if not already defined
#
def overrides(interface_class):

    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

#------------------------------------------------------------------------
# Supporting classes
#

# Annotations: class for representing annotations on essays, such as the
# clause-level correspondence between the student answer and the teacher's
# key.
#
class Annotations:

    # constructor: initialize hash from labels to text units (e.g., clause)
    # as well as hash giving correspondence of student textual units to key.
    def __init__(self):
        debug_print("Annotations.__init__(%s)" % self, level=6)
        self.textual_units = dict()
        self.start_offset = dict()
        self.end_offset = dict()
        self.correspondences = dict()
        self.original_text = None
        self.text_proper = None
        self.last_label = None

    # interpret_annotation(annotation): Analyze ANNOTATION which can either be a label
    # or a correspodence section. 
    # Notes:
    # - this maintained result a hash from each student label to linked standard label(s)
    # - this also keeps track of starting offset for labels in start_offset, assuming
    # text_proper is incrementally being updated elsewhere along with this invocation.
    # - annotation labels are converted to uppercase
    #
    def interpret_annotation(self, annotation_text):
        debug_print("interpret_annotation(_)", level=5)
        debug_print("\tannotation_text=%s" % annotation_text, level=6)
        assert((self.text_proper != None) and (len(self.text_proper) >= 0))
        annotation_text = annotation_text.upper()
        match = re.search("=>", annotation_text)
        if not match:
            # Handle text label
            current_offset = len(self.text_proper)
            self.start_offset[annotation_text] = current_offset
            if not self.last_label is None:
                self.end_offset[self.last_label] = current_offset
            self.last_label = annotation_text
        else:
            # Handle correspondence linkages
            while (len(annotation_text) > 0):
                # TODO: check for weight (e.g., "p1a => 1b (0.5)")
                ## OLD: match = re.search(r"(\S+)\s*=>\s*(\S+)", annotation_text)
                ## OLD: match = re.search(r"([^:; \t\]])\s*=>\s*([^:; \t\]]+)", annotation_text)
                match = re.search("([^:;= \t\n\[\]]+)\s*=>\s*([^:;= \t\n\[\]]+)", annotation_text)
                if (match):
                    student = match.group(1)
                    key = match.group(2)
                    if (not self.correspondences.has_key(key)):
                        self.correspondences[key] = []
                    self.correspondences[key].append(student)
                    debug_print("Adding correspondence: '%s' => '%s'" % (student, key), level=4)
                    if (re.search("=\s*>", annotation_text[0: match.start(0)])):
                        # TODO: pass in filename to function and add to warning (likewise below)
                        print_stderr("Warning: missed annotation-like text in '%s'" % annotation_text[0: match.start(0)])
                    annotation_text = annotation_text[match.end(0) : ]
                else:
                    if (re.search("=\s*>", annotation_text)):
                        print_stderr("Warning: missed annotation-like text in remainder '%s'" % annotation_text)
                    annotation_text = ""

    # extract_annotations(text): Analyzes text to extract hashes mapping
    # labels into textual units and for mapping student labels into key
    # TODO: track down slight offset problem for annotations from new-Q1-Standard.docx
    #
    def extract_annotations(self, text):
        debug_print("extract_annotations(_)", level=5)
        debug_print("\ttext=%s" % text, level=7)
        self.text_proper = ""
        self.last_label = None
        # Extract label offsets and then label correspondences
        while (len(text) > 0):
            # Check for annotations within double square brackets (e.g., [[p5a]]).
            # As a fallback, this checks for lines consisting just of " label => label ".
            # TODO: Have the annotator fix his annotations that lack the brackets.
            match = re.search(r"\[\[([^[]+)\]\]", text)
            if (not match) and ALLOW_LOOSE_ANNOTATIONS:
                ## OLD: match = re.search(r"\n\s*(([^:;= \t\n\[\]]+)\s*=>\s*([^:;= \t\n\[\]]+))\s*\n", text)
                ## TODO: match = re.search(r"\n\s*(([^:;= \t\n\[\]]+)\s*=>\s*([^:;= \t\n\[\]]+))", text)
                match = re.search(r"(([^:;= \t\n\[\]]+)\s*=>\s*([^:;= \t\n\[\]]+))", text)

            # Extract annotations if found
            if (match):
                ## TODO: annotation = match.group(0)
                annotation_text = match.group(1)
                self.text_proper += text[0 : match.start(0)] + " "
                text = text[match.end(0) : ]
                self.interpret_annotation(annotation_text)
                ## OLD: replacement_spaces = " " * len(annotation)
                ## OLD: self.text_proper += " " + text[0 : match.start(0)] + replacement_spaces

            # Othewise add remainder of text to version sana annotations
            else:
                if not match:
                    self.text_proper += text + " "
                    text = ""

        # Finalize the label tracking
        if self.last_label:
            self.end_offset[self.last_label] = len(self.text_proper)
        # Convert start_offset/end_offset info into textual_unit's
        for unit in self.end_offset.keys():
            start = self.start_offset[unit]
            end = self.end_offset[unit]
            self.textual_units[unit] = self.text_proper[start : end]

        # Display in order by starting offset
        debug_print("Annotation textual units 'label\t[start, end): text', ...:", level=2)
        units = self.textual_units.keys()
        for unit in sorted(units, key=lambda k: self.start_offset[k]):
            debug_print("%s\t[%s, %s): { %s }" % (unit, self.start_offset[unit], self.end_offset[unit], self.textual_units[unit]), level=2)
        debug_print("text_proper={\n%s\n\t}" % self.text_proper, level=7)

# evaluate_linkages(answer_annotations, detailed_mark_list, good_points): Compares the manual linakge annotations
# with the result of the system.
# Returns: num_good, num_system, num_manual
#
def evaluate_linkages(answer_annotations, detailed_mark_list, good_points):
    debug_print("evaluate_linkages%s" % str((answer_annotations, '_', good_points)), level=5)
    debug_print("\tdetailed_mark_list=%s" % detailed_mark_list, level=7)
    num_good = 0
    # Initialize totals
    ## OLD: num_system = len(good_points)
    num_system = 0
    num_manual = len(answer_annotations.correspondences)
    # Analyze annotation links

    # Check matches established by system against annotations
    # Note: Standard labels subsume the point names (e.g., labels 1.1a and 1.1b for point 1.1)
    for point in good_points:
        debug_print("Point: %s" % point, level=4)
        point_label_prefix = re.sub("^P", "", point.upper())

        # Check student answer annotations linkages that map into standard with corresponding (correct) key
        ## standard_point_labels = [label for label in answer_annotations.correspondences.keys() if (label.find(point_label_prefix) != -1)]
        standard_point_labels = [label for label in answer_annotations.correspondences.keys() if (label.find(point_label_prefix) == 0)]
        for std_label in standard_point_labels:
            debug_print("Standard label: %s" % std_label, level=4)
            
            try:
                # Find out locations indicated by annotations
                student_labels = answer_annotations.correspondences[std_label]
                for stu_label in student_labels:
                    debug_print("Matching student label: %s" % stu_label, level=4)
    
                    # Get annotation offsets
                    annot_start = answer_annotations.start_offset[stu_label]
                    annot_end = answer_annotations.end_offset[stu_label]
                    annot_text = answer_annotations.textual_units[stu_label]
                    debug_print("annot: offsets=(%d, %d) text=%s" % (annot_start, annot_end, annot_text), level=4)
    
                    # Get system answer offsets
                    system_start = -1
                    system_end = -1
                    system_text = "n/a"
                    for mark in detailed_mark_list:
                        if (mark['Point_No'] == point):
                            match_sen = mark['Match_Sen']
                            system_start = match_sen['Start']
                            system_end = match_sen['End']
                            system_text = match_sen['StuS']
                            break
                    debug_print("system: offsets=(%d, %d) text=%s" % (system_start, system_end, system_text), level=4)
    
                    # Make sure offsets overlap significantly
                    ## TODO: rework num_system so not dependent upon annotation labels
                    if (system_start != -1):
                        num_system += 1
                        is_overlap = False
                        if (annot_start <= system_start) and (annot_end >= system_start):
                            overlap_ratio = float(annot_end - system_start) / (annot_end - annot_start)
                            is_overlap = (overlap_ratio >= OVERLAP_THRESHOLD)
                        if (annot_start >= system_start) and (annot_end <= system_start):
                            overlap_ratio = float(annot_start - system_end) / (annot_end - annot_start)
                            is_overlap = (overlap_ratio >= OVERLAP_THRESHOLD)
                        if is_overlap:
                            debug_print("Correct student %s linkage with standard %s" % (stu_label, std_label), level=3)
                            num_good += 1
            except KeyError:
                print_stderr("Exception in evaluate_linkages: " + str(sys.exc_info()))
    if (num_system != len(good_points)):
        print_stderr("Warning: Discrepency in num_system (%d) vs. num good_points (%d)" % (num_system, len(good_points)))
    debug_print("evaluate_linkages() => %s" % str((num_good, num_system, num_manual)), level=3)
    return num_good, num_system, num_manual

# calculate_fscore (case, good, manual, system): Show F-Score for CASE given counts for number GOOD, MANUAL, and SYSTEM.
#
def calculate_fscore (case, num_good, num_manual, num_system):
    recall = 0
    precision = 0
    f_score = 0
    print "%s: Num good %d; num manual %d; num system %d" % (case, num_good, num_manual, num_system)
    if num_manual > 0:
        recall = float(num_good) / num_manual
    if num_system > 0:
        precision = float(num_good) / num_system
    if (recall > 0) or (precision > 0):
        f_score = 2 * (precision * recall) / (precision + recall)
    print "Recall %.3f; Precision %.3f; F-Score %.3f" % (round(recall, 3), round(precision, 3), round(f_score, 3))


# WARNING: The following overrides the classes for an unapparent testing purpose
# (e.g., abStandard for Standard from standard.py). However, this practice is extremely
# dangerous, as this no longer represents a test of the actual deployed code!!!
#

class abStandard(Standard):

    # constructor: warn about using different version of code
    def __init__(self):
        debug_print("Warning: Using shameless hack (abStandard testing class): FIX ME!")
        Standard.__init__(self)

    # note: There doesn't seem to be any difference in this version and the one in standard.py,
    # except for syntactic variant in using [result for item in list] here rather than
    # list(result for item in list) there.
    #
    @overrides(Standard)
    def CalVector(self, sentencelist):
        debug_print("abStandard.CalVector(_)", level=5)
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

    # There is no difference is this version than in standard.py, except for minor comment changes..
    #
    @overrides(Standard)
    def SentenceCal(self, sentencelist, textfdist):
        debug_print("abStandard.SentenceCal(_)", level=5)
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

    # constructor: initializes default settings
    # note: different thresholds are used here versus those in answer.py:
    #   dist_threshold:  0.30 (vs. 0.25)
    #   sen_threshold:   0.15 (vs. 0.33)
    # multisen_matchrate and multisen_threshold are the same
    # TODO: Use same settings!!!
    #
    @overrides(Answer)
    def __init__(self, **kwargs):
        debug_print("Warning: Using shameless hack (abAnswer testing class): FIX ME!")
        Answer.__init__(self)
        self.dist_threshold = kwargs.get('dist_threshold') or 0.3
        self.multisen_matchrate = kwargs.get('multisen_matchrate') or 0.3
        self.sen_threshold = kwargs.get('sen_threshold') or 0.15
        self.multisen_threshold = kwargs.get('multisen_threshold') or 0.4
        nltk.data.path = [settings.NLTKDATAPATH]

    # note: No difference from answer.py version except for minor comment change
    @overrides(Answer)
    def SentenceAnalysis(self, fulltext, textfdist):
        debug_print("abAnswer.SentenceAnalysis(_)", level=5)
        ans_sentencelist = []
        text = fulltext.replace('\n', ' ')
        ## OLD: p = re.compile(r'.+\.')
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

    # note: no difference from from answer.py version except for Pearson correlation trace here that was commented out
    #
    @overrides(Answer)
    def CalCosDist(self, ans_sentencelist, std_sen):
        debug_print("abAnswer.CalCosDist(_)", level=5)
        match_sen = None
        max_cos = 0

        if __debug__:
            # TODO: Move this elsewhere
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
            debug_print_without_newline("pearson = ")
            try:
                print pearson(ans_sentencelist, std_sen)
            except:
                print "n/a"
                debug_print("Exception during pearson calculation: " + str(sys.exc_info()))

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


#------------------------------------------------------------------------
# Test Cases
#
# Note: These don't actually test for specific conditions (e.g., via assertTrue),
# hence they are more like examples than actual test cases.
#


# Note: The class itself shouldn't be excluded, just the specific method that might take too long.
## OLD: @unittest.skip("Too much time")

class AlgorithmTest(TestCase):

#    # constructor: initialize instance variables
#    def __init__(self):
#        self.standard_annotations = None
#        self.student_annotations = None

    # Setup(): testing setup code
    def setUp(self):
        self.logger = logging.getLogger(__name__)

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
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
        if __debug__:
            print "Word frequencies"
            for word,freq in textfdist.items():
                print "%s:%d" % (word,freq)
        pprint.pprint(slist)
        self.logger.info("Test Standard Answer Analysis finished")

    # Derives frequency distribution and shows old vs. new.
    #
    def get_student_text_distribution(anstext, std_textfdist):
        debug_print("Note: Deriving alternative global frequency distribution (from student text) for use with Answer.Analysis()")
        sinst = Standard()
        stu_pointlist, stu_textfdist, stu_slist = sinst.Analysis(anstext)
        debug_print("\tstandard dist: " + str(std_textfdist), level=4)
        debug_print("\tstudent dist: " + str(stu_textfdist), level=4)
        return stu_textfdist

    # NOTE: MarkScheme is not used in the system, so this should be rewritten 
    # to use MarkingSchemeLang instead.
    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
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

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_answer(self):
        self.logger.info("Test Student Answer Analysis")

        # Read in the correct answer to first question
        # TODO: Create helper function for reading question info as same code sequence used elsewhere.
        testStandardAnswerFile = "ans_Q1.txt"
        stdFilePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        self.logger.info("stdanswer filepath:%s" % stdFilePath)
        if not os.path.isfile(stdFilePath):
            self.logger.error("Standard Test file doesn't exist:%s" % testStandardAnswerFile)
            assert False
        fh = file(stdFilePath, "r")
        stdtext = fh.read()
        fh.close()

        # Perform text processing analysis over correct answer
        sinst = Standard()
        pointlist, textfdist, slist = sinst.Analysis(stdtext)
        std_pointlist_no = [point['Point_No'] for point in pointlist]
        self.logger.info("Points:%s" % std_pointlist_no)

        # Read in the standard as if it were 
        # TODO: Just do an assignment for crying out loud! Such needless code repetiton!
        # ex: anstext = stdtext
        testAnswerFile = "ans_Q1.txt"
        ansFilePath = os.path.join("algo/testdata/raw/Q1", testAnswerFile)
        self.logger.info("answer filepath:%s" % ansFilePath)
        if not os.path.isfile(ansFilePath):
            self.logger.error("Answer file doesn't exist:%s" % testAnswerFile)
            assert False
        fh = file(ansFilePath, "r")
        anstext = fh.read()
        fh.close()

        # Create some dummy grading rules
        mockrulelist = [
            {'Mark': 10, 'Point': ['P1.1', 'P1.2', 'P1.3', 'P2', 'P3', 'P4', 'P5']},
            {'Mark': 7, 'Point': ['P1.1', 'P2', 'P3', 'P4', 'P5']},
            {'Mark': 6, 'Point': ['P1.1', 'P2', 'P3', 'P4']},
            {'Mark': 5, 'Point': ['P1.1', 'P2', 'P3']},
            {'Mark': 3, 'Point': ['P1.1', 'P2']},
            {'Mark': 2, 'Point': ['P1.1']}]
        pprint.pprint(mockrulelist)

        # Create the answer class instance and optionally override global frequency distribution from answer text.
        # TODO: Always use freq dist for student text (not standard).
        ans = Answer()
        if (USE_STUDENT_TEXT_DIST):
            textfdist = get_student_text_distribution(anstext, textfdist)

        # Preprocess the student answer and then compare resulting vectors against standard
        # TODO: Raise an exception if the result is not as expected
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
                debug_print("Exception during __updaterulelist: " + str(sys.exc_info()))
                pass
        return txtrulelist

    # Helper function for testing Q1 sentences, returning result of text processing
    # and term vector creation along with some grading rules for testing.
    #
    def parse_Q1(self):
        debug_print("parse_Q1()", level=4)
        # Read in the correct answer to first question
        testStandardAnswerFile = "ans_Q1.txt"
        filePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        self.logger.info("filepath:%s" % filePath)
        if not os.path.isfile(filePath):
            self.logger.error("Test file doesn't exist:%s" % testStandardAnswerFile)
            assert False
        debug_print("Processing standard file '%s'" % filePath, level=3)
        fh = file(filePath, "r")
        filetext = fh.read()
        fh.close()

        # Check the text for optional annotations and isolate
        if CHECK_LINKAGES:
            self.standard_annotations = Annotations()
            self.standard_annotations.extract_annotations(filetext)
            filetext = self.standard_annotations.text_proper

        # Create the appropriate class instance for Standard
        # TODO: Remove abAnswer method overrides altogether and do everything via proper subclassing (RTFM!!!).
        ## OLD: sinst = abStandard()
        sinst = abStandard() if USE_OVERRIDES else Standard()

        # Perform text processing analysis over sentence and return result along with some mocked up rules
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

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_Q1_single(self):
        debug_print("test_Q1_single()", level=4)
        pointlist, textfdist, slist, rulelist = self.parse_Q1()
        ## OLD: ans = abAnswer()
        ansfile = 'algo/testdata/raw/Q1/Q1_SS16.docx.txt'
        fh = file(ansfile, "r")
        anstext = fh.read()
        fh.close()
        manualmark = 1
        # Create the answer class instance and optionally override global frequency distribution from answer text.
        # TODO: Always use freq dist for student text (not standard).
        ans = abAnswer() if USE_OVERRIDES else Answer()
        if (USE_STUDENT_TEXT_DIST):
            textfdist = get_student_text_distribution(anstext, textfdist)
        mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
        err = mark - manualmark
        print("%s\t%d\t%s\t%d" % (ansfile, mark, marklist, err))

    # test_Q1_all(): grade each of the 32 student papers against the standard key, comparing the system
    # score to that of manual grading.
    # In addition, a separate evaluation is done in terms of recall/precision of matching student answers sentences
    # with those in the standard key by comparison against correspondence annotations (i.e., linkages).
    #
    ## TODO: @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_Q1_all(self):
        debug_print("test_Q1_all()", level=4)
        pointlist, textfdist, slist, rulelist = self.parse_Q1()
        manuallist = [9, 7, 9, 7, 7, 10, 7, 7, 7, 7, 7, 1, 2, 2, 0, 1, 2, 2, 1, 1, 8, 9, 4, 9, 7, 9, 0, 7, 4, 10, 7, 7]
        minmaxerr = 0
        minrd = 0
        minerrcount = 0
        total_good = 0
        total_system = 0
        total_manual = 0

        # Optionally initialize random see (useful for debugging)
        if RANDOM_SEED > 0:
            debug_print("Setting random seed to %d" % RANDOM_SEED)
            random.seed(RANDOM_SEED)

        # Run ten different evaluations with different random sentence matching threshold
        for i in range(NUM_TRIALS):
            trial_num = i + 1
            debug_print("trial %d" % trial_num, level=4)
            maxerr = 0
            errcount = 0
            var = 0

            # Create the appropriate class instance for Answer
            # Note: default thresholds: dist_threshold 0.25, multisen_matchrate 0.3, sen_threshold 0.33, multisen_threshold 0.4
            # TODO: Remove abAnswer method overrides altogether and do everything via proper subclassing (RTFM!!!).
            ## OLD: ans = abAnswer(dist_threshold=rd, multisen_matchrate=0.3, sen_threshold=rd, multisen_threshold=0.4)
            ans = None
            if (USE_OVERRIDES):
                ## OLD: ans = abAnswer(dist_threshold=rd, multisen_matchrate=0.3, sen_threshold=rd, multisen_threshold=0.4)
                ans = abAnswer()
            else:
                ans = Answer()
            if RANDOM_THRESHOLDS:
                rd = random.uniform(0.32, 0.36)
                debug_print_without_newline("rd = ")
                print rd
                ans.dist_threshold=rd
                ans.multisen_matchrate=0.3
                ans.sen_threshold=rd
                ans.multisen_threshold=0.4

            # Test all cases in Q1 directory
            # TODO: replace os.walk with directory read
            Q1_base_dir = 'algo/testdata/raw/Q1'
            for root, dirs, files in os.walk('algo/testdata/raw/Q1'):
                if root != Q1_base_dir:
                    continue
                if 'Standard' in dirs:
                    dirs.remove('Standard')
                for idx in range(0, MAX_ESSAYS):
                    # Read student answer
                    ## OLD: ansfile = 'Q1_SS' + str(idx + 1) + '.docx.txt'
                    ext = '.annot.txt' if CHECK_LINKAGES else '.docx.txt'
                    ansfile = 'Q1_SS' + str(idx + 1) + ext
                    debug_print("Processing student answer '%s'" % ansfile, level=3)
                    filePath = os.path.join(root, ansfile)
                    fh = file(filePath, "r")
                    anstext = fh.read()
                    debug_print("anstext: { %s }" % anstext, level=7)
                    fh.close()

                    # Check the text for optional annotations and isolate
                    if CHECK_LINKAGES:
                        self.answer_annotations = Annotations()
                        self.answer_annotations.extract_annotations(anstext)
                        ## DUH: anstext = self.standard_annotations.text_proper
                        anstext = self.answer_annotations.text_proper

                    # Grade the essay and compare against manual
                    # TODO: Always use freq dist for student text (not standard)
                    if (USE_STUDENT_TEXT_DIST):
                        textfdist = get_student_text_distribution(anstext, textfdist)
                    mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
                    err = mark - manuallist[idx]

                    # Check the system sentence linkages versus the annotations
                    if CHECK_LINKAGES:
                        num_good, num_system, num_manual = evaluate_linkages(self.answer_annotations, ans.detailedmarklist, marklist)
                        calculate_fscore("ss" + str(idx + 1), num_good, num_system, num_manual)
                        total_good += num_good
                        total_system += num_system
                        total_manual += num_manual

                    # Update statistics
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

        # Summarize answer/standard correspondences with respect to manual annotations
        if CHECK_LINKAGES:
            calculate_fscore("Overall", total_good, total_system, total_manual)

    #__traversal_process(dir): Checks DIR for teacher's key (standard), marking scheme, and one or more student
    # answers, using the following naming convention:
    #   ans_qN.txt  scheme_qN.txt  studM_qN.txt  studM_qN.txt
    # where N is th question number, and M is the student number. For example (from in testdata/raw/Q3):
    #   ans_q8.txt  scheme_q8.txt  stud1_q8.txt  stud7_q8.txt
    # 
    def __traversal_process(self, testdir):
        ans = Answer()
        for root, dirs, files in os.walk(testdir):
            if 'Standard' in dirs:
                dirs.remove('Standard')
            for stdfile in files:
                # Check for answer file (e.g., "ans_q8.txt")
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

                    # Check schema file (e.g., "scheme_q8.txt")
                    schemename = 'scheme_' + testno + '.txt'
                    schemepath = os.path.join(root, schemename)
                    fr = file(schemepath, 'r')
                    scheme = self.__parsescheme(fr.read())
                    fr.close()
                    rulelist = self.__updaterulelist(scheme, pointlist)
                    print("ansfile\tmark\tmarklist")
                    for idx in range(0, 10):
                        # Check student response file (e.g., "stud9_q8.txt")
                        ansfile = 'stud' + str(idx + 1) + '_' + testno + '.txt'
                        ansPath = os.path.join(root, ansfile)
                        if os.path.isfile(ansPath):
                            fa = file(ansPath, 'r')
                            anstext = fa.read()
                            fa.close()
                            if anstext:
                                # TODO: Always use freq dist for student text (not standard)
                                if (USE_STUDENT_TEXT_DIST):
                                    textfdist = get_student_text_distribution(anstext, textfdist)
                                debug_print("Calling ans.Analysis%s" % str((anstext, textfdist, slist, pointlist, rulelist)), level=4)
                                mark, marklist, ommited = ans.Analysis(anstext, textfdist, slist, pointlist, rulelist)
                            else:
                                mark = 0
                                marklist = []
                            print("%s\t%d\t%s" % (ansfile, mark, marklist))

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_Q2(self):
        self.__traversal_process('algo/testdata/raw/Q2')

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_Q3(self):
        self.__traversal_process('algo/testdata/raw/Q3')

    @unittest.skipIf(EXCLUDE_LONG_TESTS, "Too much time")
    def test_Q4(self):
        self.__traversal_process('algo/testdata/raw/Q4')


# Run the test if exceuted directly (avoids Django testing overhead)
#
debug_print("__name__ = " + str(__name__), level=4)
if __name__ == '__main__':
    debug_print("Invoking tests directly")
    # Note: following based on Python unittest module description (underlies Django one)
    unittest.main()
    

debug_print("stop algo/tests.py: " + debug_timestamp())
