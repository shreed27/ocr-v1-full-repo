from django.conf import settings




def get_property_value(object, property_name, default_value=None):
    value = default_value
    if (hasattr(object, property_name)):
        value = getattr(object, property_name)
    # debug_print("get_property_value%s => %s" % (str((object, property_name, default_value)), 
    #                                             value), level=4)
    print "get_property_value%s => %s" % (str((object, property_name, default_value)), value)
    return value

use_part_of_speech = get_property_value(settings, 'USE_PART_OF_SPEECH', False)

def getenv_boolean (var, default=False):
    from algo.common import getenv_text
    bool_value = default
    value_text = getenv_text(var)
    if (len(value_text) > 0):
        bool_value = True
        if (value_text.lower() == "false") or (value_text == "0"):
            bool_value = False
    return (bool_value)



def PointAnalysis(fulltext):
    from algo.common import *                    # common routines (mostly debugging)
    # debug_print("algo/standard.py: " + debug_timestamp())
    print "algo/standard.py: " + debug_timestamp()
    from algo.common import get_property_value, getenv_boolean
    from algo import wordnet                          # word information (dictionary, thesaurus, etc.)
    # from algo import text                             # text preprocessing
    from algo.text_critique import TextCritique   # qualitative critique (e.g., grammar checking)

    # Other packages
    #
    import logging
    from django.conf import settings
    import re
    import sys
    import nltk
    import math

    pointlist = []
    # Perform text normalization, while preserving offsets
    ## OLD: text = fulltext.replace('\t', '')
    text = fulltext.replace('\t', ' ')
    print "text    =    ",text

    # Find all lines starting with digit, recording offset
    ## OLD: m = self.pointtext_pattern.findall(text)
    # TODO: convert into helper function for use elsewhere (e.g., findall_with_offsets)
    offset = 0
    m = []
    starts = []
    ends = []
    #print text
    pointtext_pattern = re.compile(r'^\s*\d.+\n', re.MULTILINE)
    while (len(text) > 0):
        match = pointtext_pattern.search(text)        
        if not match:
            break
        m.append(match.group(0).strip())        
        starts.append(offset + match.start(0))
        ends.append(offset + match.end(0))
        text = text[match.end(0) : ]
        offset += match.end(0)

    if (len(m) == 0):
        print "No points detected in text: %s" % fulltext
        #self.logger.warn("No points detected in text: %s" % fulltext)

    # Create hash entries for point/text representation
    for i in range(0, len(m)):
        # Collect number proper and item text
        ## OLD: num = re.search(r'^(\d+(\.\d)?\s\.)*', m[i]).group()
        num = re.search(r'^\s*(\d+(\.\d)?\s\.)*', m[i]).group().strip()

        #num = re.search(r'^\s*(\d+(\.\d)?\s\.)*', m[i]).group().strip()
        pointlist.append({'Point_No': 'P' + str(num)[:-2],
                          'Point_Text': m[i][len(num):].replace('\n', ' ').strip(),
                          'Start': starts[i], 'End': ends[i]})
    # debug_print("Standard.PointAnalysis(%s) => %s" % (fulltext, str(pointlist)), level=5)
    #print "Standard.PointAnalysis(%s) => %s" % (fulltext, str(pointlist))
    return pointlist


def SentenceAnalysis(pointlist):
    from algo.common import *                    # common routines (mostly debugging)
    # debug_print("algo/standard.py: " + debug_timestamp())
    print "algo/test_pointanalysis.py: " + debug_timestamp()
    from algo.common import get_property_value, getenv_boolean
    from algo import wordnet                          # word information (dictionary, thesaurus, etc.)
    # from algo import text                             # text preprocessing
    from algo.text_critique import TextCritique   # qualitative critique (e.g., grammar checking)

    # Other packages
    #
    import logging
    from django.conf import settings
    import re
    import sys
    import nltk
    import math

    print("Standard.SentenceAnalysis(%s)" % str(pointlist))
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
        keyword_pattern = re.compile(r'\(\(\((.+?)\)\)\)')
        #keyword_pattern = re.compile(r'')
        keysen_pattern = re.compile(r'.+.')
        # keysen_pattern = re.compile(r'')


        while (len(point_text) > 0):
            match = keysen_pattern.search(point_text)
            if not match:
                break
            keysen.append(match.group(0))
            starts.append(offset + match.start(0))
            ends.append(offset + match.end(0))
            point_text = point_text[match.end(0):]
            offset += match.end(0)

        # Create hash entries for each sentence

        for i in range(0, len(keysen)):
            sen_no += 1
            pointsen_no[point['Point_No']].append(sen_no)
            
            # Extract keyword specifications (e.g. "(((recession))) of 2008")
            keyword = keyword_pattern.findall(keysen[i])
            
            ## OLD: #keyword += [choice.strip(' ') for choice in self.choice_pattern.findall(keysen[i])]
            sentencelist.append({'KeyS': keysen[i], 'KeyBVec': keyword,
                                 'Point_No': point['Point_No'], 'No': sen_no,
                                 'Start': starts[i], 'End': ends[i]})
    for sen in sentencelist:
        sen.setdefault('TotalS_No', pointsen_no.get(sen['Point_No']))
        
    debug_print("Standard.SentenceAnalysis() => %s" % str(sentencelist), level=5)
    return sentencelist

def ParseKeyword(text):
    # debug_print_without_newline("Standard.ParseKeyword(%s)" % text, level=5)
    special = {'<': ' ', '>': '', '(': '',
               ')': '', '.': '', ',': '',
               '""': ''}            # TODO: See if this should be '"'
    for (k, v) in special.items():
        text = text.replace(k, v)
    print(" => %s" % text)
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
def CalVector(sentencelist):
    from algo.test_pointanalysis import ParseKeyword, use_part_of_speech
    #from algo.common import *                    # common routines (mostly debugging)
    # debug_print("algo/standard.py: " + debug_timestamp())
    #print "algo/standard.py: " + debug_timestamp()
    from algo.common import get_property_value, getenv_boolean
    from algo import wordnet                          # word information (dictionary, thesaurus, etc.)
    # from algo import text                             # text preprocessing
    from algo.text_critique import TextCritique   # qualitative critique (e.g., grammar checking)

    # Other packages
    #
    import logging
    from django.conf import settings
    import re
    import sys
    import nltk
    import math

    print("Standard.CalVector(%s)" % sentencelist)
    text_words = []
    
    # Gather words from all sentences
    for sentence in sentencelist:
        print("sentence: " + str(sentence))
        raw = ParseKeyword(sentence['KeyS'])
        text = nltk.word_tokenize(raw)
        part_of_speech_tagged_words =  nltk.pos_tag(text)
        print("part_of_speech_tagged_words = %s" % str(part_of_speech_tagged_words))
        stopwords_list = nltk.corpus.stopwords.raw('english').split()
        # OLD: #word.lower() + '/' + tag
        words = list(nltk.corpus.wordnet.morphy(word.lower())
                     for word, tag in part_of_speech_tagged_words
                     # TODO: allow for comparatives and particles (e.g., back/RP)
                     if (tag.startswith('V') or tag.startswith('NN') or tag == 'JJ' or tag == 'DET' or tag == 'RB')
                     and word not in stopwords_list)
        words_proper = list(word for word in words if word)
        if use_part_of_speech:
            # Prefix each word with wordnet part-of-speech indicator (e.g., ['fast', 'car'] => ['a:fast', 'n:car'])
            words_proper = [wordnet.get_part_of_speech(tag) + ":" + word
                            for (word, (token, tag)) in zip(words, part_of_speech_tagged_words) 
                            if word]
        print("words_proper: " + str(words_proper))

        # remove empty words and store in SenWords property
        sentence['SenWords'] = words_proper
        text_words += sentence['SenWords']

    # Get frequency distribution
    print("text_words: " + str(text_words))
    textfdist = nltk.FreqDist(text_words)
    print("Standard.CalVector => %s" % str(textfdist))
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
def SentenceCal(sentencelist, textfdist):
    from algo.common import get_property_value, getenv_boolean 
    # from algo.test_pointanalysis import use_true_tf_idf
    from algo import wordnet                          # word information (dictionary, thesaurus, etc.)
    from algo import text                             # text preprocessing
    from algo.text_critique import TextCritique   # qualitative critique (e.g., grammar checking)

    # Other packages
    #
    import logging
    from django.conf import settings
    import re
    import sys
    import nltk
    import math           
    # debug_print("Standard.SentenceCal%s" % str((sentencelist, textfdist)), level=5)
    print "Standard.SentenceCal%s" % str((sentencelist, textfdist))

    use_true_tf_idf = getenv_boolean("USE_TRUE_TF_IDF", False)
    for sentence in sentencelist:
        # OLD: text = nltk.word_tokenize(sentence['KeyS'])
        # OLD: # word.lower() + '/' + tag
        fdist = nltk.FreqDist(sentence['SenWords'])
        try:
            max_freq = max([f for f in fdist.values()])
        except:
            print("Exception in Standard.SentenceCal: " + str(sys.exc_info()))
            max_freq = 1
            
        log_max_freq = math.log(max_freq) if (max_freq > 1) else 1
        senvec = {}
        sen_len = len(sentencelist)
        for word in sorted(textfdist):
            if fdist[word]:
                # the frequency of sentence which contains this word in all sentencelist
                sentencefreq = sum(1 for senten in sentencelist if word in senten['SenWords'])
                if (use_true_tf_idf):
                    tf = 1 + math.log(fdist[word]) / log_max_freq
                    idf = 1 + math.log(sen_len / sentencefreq)
                    senvec[word] = tf * idf
                else:
                    senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * sen_len / sentencefreq)
            else:
                senvec[word] = 0

            
        sentence['KeySVec'] = senvec
    # debug_print("Standard.SentenceCal => %s" % str(sentencelist), level=5)
    print "Standard.SentenceCal => %s" % str(sentencelist)
    return sentencelist




if __name__ == "__main__" or __name__ == 'django.core.management.commands.shell':    
    from question.models import Question
    obj = Question.objects.get(id=1026)
    text = obj.stdanswertext

    stdanswer = obj.stdanswer
    print
    print stdanswer.rulelist
    #print text
    # text = "    1 . It captured the vibrancy of India's slums.\n    2 . which are often misperceived as being simply rundown housing areas.\n"
    # # text = "  1.  (x+y)^2=x^2+2xy+y^2  (second power: three terms)    2.  (x+y)^3=x^3+3x^2y+3xy^2+y^3  (third power: four terms)    3.  (x+y)^4=x^4+4x^3y+6x^2y^2+4xy^3+y^4  (fourth power: five terms)    4. Quadratic Formulae:  x\:=\frac{\:-b\mp\sqrt{b^2-4ac}}{2a}    5. Algebraic Equation:  (a+b)^2=a^2+b^2+2ab "
    text = "1 . The attorney chased the ambulance downtown.\n2 . The ambulance chased back.\n"
    text = "1 . (x+y)^2=x^2+2xy+y^2\n"
    point_list = PointAnalysis(text)
    print
    print "point_list"
    print point_list
    print

    sentence_list = SentenceAnalysis(point_list)
    print
    print "sentence_list"
    print sentence_list
    print 
    # pointlist = [{'Point_No': 'P3', 'Point_Text': ' The PPC helps elucidate the meaning of (((scarcity))) , (((choice))) and (((opportunity cost))).  '}]
    # y = StdSentenceAnalysis(pointlist)
    # print y
    frequency_dict = CalVector(sentence_list)
    print
    print "frequency_dict"
    print frequency_dict
    print 

    sentencecal_result = SentenceCal(sentence_list, frequency_dict)
    print
    print "sentencecal_result"
    print sentencecal_result
    print
