#! /usr/bin/python
#
# standard.py: Defines class for representing correct answers (Standard).
#

# Local packages
#
from common import *
debug_print("algo/standard.py: " + debug_timestamp())
import wordnet

# Other packages
#
import logging
from django.conf import settings
import re
import nltk
import math

class Standard:

    # constructor(): initialize globals and compile regex patterns
    # EX: std = Standard(); re.match(r"\.", std.keysen_pattern) => True
    #
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.use_part_of_speech = get_property_value(settings, 'USE_PART_OF_SPEECH', False)
        self.use_true_tf_idf = get_property_value(settings, 'USE_TRUE_TF_IDF', False)
        if __debug__:
            self.use_part_of_speech = getenv_boolean("USE_PART_OF_SPEECH", self.use_part_of_speech)
            self.use_true_tf_idf = getenv_boolean("USE_TRUE_TF_IDF", self.use_true_tf_idf)
        nltk.data.path = [settings.NLTKDATAPATH]
        # TODO: use re.MULTILINE
        self.pointtext_pattern = re.compile(r'^\d.+\n', re.M)
        self.keysen_pattern = re.compile(r'.+\.')
        self.keyword_pattern = re.compile(r'\(\(\((.+?)\)\)\)')
        self.choice_pattern = re.compile(r'\s[A-Z]\s')

    # PointAnalysis(fulltext): Break question text into pieces based on numbered sub-part indicators.
    # The result is returned as a list of hashes with with Point_No and Point_Text keys.
    # In addition, the starting and ending offsets of the point text within the original full
    # text are recorded. This is used when performing comparisons of system results versus
    # manual annotations in tests.py).
    # Note: Minor text normalization is done (e.g., tabs to spaces), but the text offsets are retrained.
    # 
    # EX: std.PointAnalysis("3 . The PPC helps elucidate the meaning of scarcity , choice and opportunity cost. \n")
    # => [{'Point_No': 'P3', 'Point_Text': ' The PPC helps elucidate the meaning of scarcity , choice and opportunity cost.  '}]
    # EX: std.PointAnalysis("1.1 . One dot one.\n3.3 . Three dot three.\n")
    # => [{'Point_No': 'P1.1', 'Point_Text': ' One dot one. '}, {'Point_No': 'P3.3', 'Point_Text': ' Three dot three. '}]
    # TODO: revise example to show Start&End offsets
    #
    def PointAnalysis(self, fulltext):
        pointlist = []
        # Perform text normalization, while preserving offsets
        ## OLD: text = fulltext.replace('\t', '')
        text = fulltext.replace('\t', ' ')

        # Find all lines starting with digit, recording offset
        ## OLD: m = self.pointtext_pattern.findall(text)
        # TODO: convert into helper function for use elsewhere (e.g., findall_with_offsets)
        offset = 0
        m = []
        starts = []
        ends = []
        while (len(text) > 0):
            match = self.pointtext_pattern.search(text)
            if not match:
                break
            m.append(match.group(0))
            starts.append(offset + match.start(0))
            ends.append(offset + match.end(0))
            text = text[match.end(0) : ]
            offset += match.end(0)

        # Create hash entries for point/text representation
        for i in range(0, len(m)):
            # Collect number proper and item text
            num = re.search(r'^(\d+(\.\d)?\s\.)*', m[i]).group()
            pointlist.append({'Point_No': 'P' + str(num)[:-2],
                              'Point_Text': m[i][len(num):].replace('\n', ' '),
                              'Start': starts[i], 'End': ends[i]})
        debug_print("Standard.PointAnalysis(%s) => %s" % (fulltext, str(pointlist)), level=5)
        return pointlist

    # SentenceAnalysis(pointlist): Expands the question (point) information to include the sentence keywords and some accumulators.
    # Both the input ia a list of hashes, as is the result.
    #
    # EX: std.SentenceAnalysis([{'Point_No': 'P3', 'Point_Text': ' The PPC helps elucidate the meaning of (((scarcity))) , (((choice))) and (((opportunity cost))).  '}])
    # => [{'KeyS': ' The PPC helps elucidate the meaning of scarcity , choice and opportunity cost.', 'Point_No': 'P3', 'TotalS_No': [1], 'KeyBVec': ['scarcity', 'choice', 'opportunity cost'], 'No': 1}]
    # EX: std.SentenceAnalysis([{'Point_No': 'P1.1', 'Point_Text': ' One dot one. '}, {'Point_No': 'P3.3', 'Point_Text': ' Three dot three. '}])
    # => [{'KeyS': ' One dot one.', 'Point_No': 'P1.1', 'TotalS_No': [1], 'KeyBVec': [], 'No': 1}, {'KeyS': ' Three dot three.', 'Point_No': 'P3.3', 'TotalS_No': [2], 'KeyBVec': [], 'No': 2}]
    # TODO: add in start/end offsets into examples
    #
    def SentenceAnalysis(self, pointlist):
        debug_print("Standard.SentenceAnalysis(%s)" % str(pointlist), level=7)
        sentencelist = []
        sen_no = 0
        pointsen_no = {}
        for point in pointlist:
            pointsen_no.setdefault(point['Point_No'], [])
            point_text = point['Point_Text']

            # Extract sentences, recording offsets in original
            ## OLD: #p = re.compile(r'([\w\"\'\(].+?\.\)?)[ \"\n]')
            ## OLD: keysen = self.keysen_pattern.findall(point_text)
            offset = point['Start']
            keysen = []
            starts = []
            ends = []
            while (len(point_text) > 0):
                match = self.keysen_pattern.search(point_text)
                if not match:
                    break
                keysen.append(match.group(0))
                starts.append(offset + match.start(0))
                ends.append(offset + match.end(0))
                point_text = point_text[match.end(0) : ]
                offset += match.end(0)

            # Create hash entries for each sentence
            for i in range(0, len(keysen)):
                sen_no += 1
                pointsen_no[point['Point_No']].append(sen_no)
                # Extract keyword specifications (e.g. "(((recession))) of 2008")
                keyword = self.keyword_pattern.findall(keysen[i])
                ## OLD: #keyword += [choice.strip(' ') for choice in self.choice_pattern.findall(keysen[i])]
                sentencelist.append({'KeyS': keysen[i], 'KeyBVec': keyword,
                                     'Point_No': point['Point_No'], 'No': sen_no,
                                     'Start': starts[i], 'End': ends[i]})
        for sen in sentencelist:
            sen.setdefault('TotalS_No', pointsen_no.get(sen['Point_No']))
        debug_print("Standard.SentenceAnalysis() => %s" % str(sentencelist), level=5)
        return sentencelist

    # ParseKeyword(text): Normalize TEXT with respect to special characters.
    # Note: Replaces '<' with space and removes any of the following characters: > ( ) . , "
    #
    # EX: std.ParseKeyword("(((recession))) of 2008") => "recession of 2008"
    #
    def ParseKeyword(self, text):
        debug_print_without_newline("Standard.ParseKeyword(%s)" % text, level=5)
        special = {'<': ' ', '>': '', '(': '',
                   ')': '', '.': '', ',': '',
                   '""': ''}			# TODO: See if this should be '"'
        for (k, v) in special.items():
            text = text.replace(k, v)
        debug_print(" => %s" % text, level=5)
        return text

    # CalVector(sent_list): Returns frequency counts for content words from KeyS property ro each dict in SENT_LIST.
    # and updates corresponding SenWords property to the words (and optionally SenTags to part-of-speech tags).
    # The text is normalized by removing certain special characters and is also lowercased.
    # Basic morphologial stemming is applied via WordNet, and stop words are removed.
    # Final words are stored in SENT_LIST SenWords's.
    # Returns frequency distribution over all of the SenWords's.
    #
    # EX: std.CalVector([{'KeyS': ' One dot one.', 'Point_No': 'P1.1', 'TotalS_No': [1], 'KeyBVec': [], 'No': 1}, {'KeyS': ' Three dot three.', 'Point_No': 'P3.3', 'TotalS_No': [2], 'KeyBVec': [], 'No': 2}]) => <FreqDist: 'one':2, 'dot':2, 'three':2>
    #
    def CalVector(self, sentencelist):
        debug_print("Standard.CalVector(%s)" % sentencelist, level=5)
        text_words = []
        
        # Gather words from all sentences
        for sentence in sentencelist:
            debug_print("sentence: " + str(sentence), level=6)
            raw = self.ParseKeyword(sentence['KeyS'])
            text = nltk.word_tokenize(raw)
            part_of_speech_tagged_words =  nltk.pos_tag(text)
            debug_print("part_of_speech_tagged_words = %s" % str(part_of_speech_tagged_words), level=4)
            stopwords_list = nltk.corpus.stopwords.raw('english').split()
            # OLD: #word.lower() + '/' + tag
            words = list(nltk.corpus.wordnet.morphy(word.lower())
                         for word, tag in part_of_speech_tagged_words
                         # TODO: allow for comparatives and particles (e.g., back/RP)
                         if (tag.startswith('V') or tag.startswith('NN') or tag == 'JJ' or tag == 'DET' or tag == 'RB')
                         and word not in stopwords_list)
            words_proper = list(word for word in words if word)
            if self.use_part_of_speech:
                # Prefix each word with wordnet part-of-speech indicator (e.g., ['fast', 'car'] => ['a:fast', 'n:car'])
                words_proper = [wordnet.get_part_of_speech(tag) + ":" + word
                                for (word, (token, tag)) in zip(words, part_of_speech_tagged_words) 
                                if word]
            debug_print("words_proper: " + str(words_proper), level=7)

            # remove empty words and store in SenWords property
            sentence['SenWords'] = words_proper
            text_words += sentence['SenWords']

        # Get frequency distribution
        debug_print("text_words: " + str(text_words), level=6)
        textfdist = nltk.FreqDist(text_words)
        debug_print("Standard.CalVector => %s" % str(textfdist), level=5)
        return textfdist

    # SentenceCal(sent_list, overall_freq_dist): computes TF/IDF-style frequency distribution for
    # the words in each sentence (SENT_LIST) with respect to entire document (OVERALL_FREQ_DIST).
    # Note: The word weight will be proportional to it's frequency in the sentence (i.e., term frequency [TF])
    # buy inversely proportional to the number of sentences it occurs is (i.e., inverse "document" frequency [IDF]).
    # Note: Changes made here should be synchronized with SentenceAnalysis in answer.py.
    #
    # EX: std.SentenceCal([{'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance', 'downtown'], 'No': 1, 'KeyS': ' The attorney chased the ambulance downtown.', 'Point_No': 'P1', 'KeyBVec': []}, {'TotalS_No': [2], 'SenWords': ['ambulance', 'chased'], 'No': 2, 'KeyS': ' The ambulance chased back.', 'Point_No': 'P2', 'KeyBVec': []}],                        <FreqDist with 4 samples and 6 outcomes>)                                                                   => [{'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance', 'downtown'], 'No': 1, 'KeyS': ' The attorney chased the ambulance downtown.', 'Point_No': 'P1', 'KeyBVec': [], 'KeySVec': {'downtown': 2.3472003889562933, 'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}},                       {'TotalS_No': [2], 'SenWords': ['ambulance', 'chased'], 'No': 2, 'KeyS': ' The ambulance chased back.', 'Point_No': 'P2', 'KeyBVec': [], 'KeySVec': {'downtown': 0, 'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}]
    # TODO: add start/end offsets
    #
    def SentenceCal(self, sentencelist, textfdist):
        debug_print("Standard.SentenceCal%s" % str((sentencelist, textfdist)), level=5)
        for sentence in sentencelist:
            # OLD: text = nltk.word_tokenize(sentence['KeyS'])
            # OLD: # word.lower() + '/' + tag
            fdist = nltk.FreqDist(sentence['SenWords'])
            max_freq = max([f for f in fdist.values()])
            log_max_freq = math.log(max_freq) if (max_freq > 1) else 1
            senvec = {}
            sen_len = len(sentencelist)
            for word in sorted(textfdist):
                if fdist[word]:
                    # the frequency of sentence which contains this word in all sentencelist
                    sentencefreq = sum(1 for senten in sentencelist if word in senten['SenWords'])
                    if (self.use_true_tf_idf):
                        tf = 1 + math.log(fdist[word]) / log_max_freq
                        idf = 1 + math.log(sen_len / sentencefreq)
                        senvec[word] = tf * idf
                    else:
                        senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * sen_len / sentencefreq)
                else:
                    senvec[word] = 0
            sentence['KeySVec'] = senvec
        debug_print("Standard.SentenceCal => %s" % str(sentencelist), level=5)
        return sentencelist

    # Analysis(full_text): Analyzes the text by breaking it into questions (points), isolating keywords,
    # computing term vectors, and then weighting the vectors using a TF/IDF-style scheme.
    #
    # EX: std.Analysis("1 . The attorney chased the ambulance downtown.\n2 . The ambulance chased back.\n")                          => ([{'Point_No': 'P1', 'Point_Text': ' The attorney chased the ambulance downtown. '}, {'Point_No': 'P2', 'Point_Text': ' The ambulance chased back. '}],                                                                              <FreqDist: 'ambulance': 2, 'chased': 2, 'attorney': 1, 'downtown': 1>,                                            [{'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance', 'downtown'], 'No': 1, 'KeyS': ' The attorney chased the ambulance downtown.', 'Point_No': 'P1', 'KeyBVec': [], 'KeySVec': {'downtown': 2.3472003889562933, 'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}, {'TotalS_No': [2], 'SenWords': ['ambulance', 'chased'], 'No': 2, 'KeyS': ' The ambulance chased back.', 'Point_No': 'P2', 'KeyBVec': [], 'KeySVec': {'downtown': 0, 'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}])
    #
    def Analysis(self, fulltext):
        debug_print("Standard.Analysis(%s)" % fulltext, level=99)
        pointlist = self.PointAnalysis(fulltext)
        sentencelist = self.SentenceAnalysis(pointlist)
        textfdist = self.CalVector(sentencelist)
        slist = self.SentenceCal(sentencelist, textfdist)
        debug_print("Standard.Analysis => (%s, %s, %s)" % (pointlist, textfdist, slist), level=6)
        return pointlist, textfdist, slist

# If invoked standalone, show analysis of simple hard-coded example (see tests.py for detailed examples).
#
if __name__ == '__main__':
    full_text = "1 . It captured the vibrancy of India's slums.\n2 . which are often misperceived as being simply rundown housing areas.\n"
    print "Input:\n\n%s\n" % full_text
    std = Standard()
    (pointlist, textfdist, slist) = std.Analysis(full_text)
    print "Output: \n\nPoints: %s\nDist: %s\nSents: %s\n" % (str(pointlist), str(textfdist), str(slist))
    debug_print("stop algo/standard.py: " + debug_timestamp())
