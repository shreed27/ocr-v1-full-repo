Intemass algorithm implementation

This is Python code directory for the Intemass algorithm implementation, as integrated into the Django web interface (e.g., www.intemass.com). This also includes new code for supporting term expansion based on information from WordNet.

Main files:

     Filename           Description
     answer.py          Represents student responses (answer).
     canvascompare.py   Post-hoc analysis of the results of the essay grading.
     common.py          Common utilities (mostly for debugging).
     markscheme.py      Provides access to rules data structure (see scheme_lang.py).
     scheme_lang.py     Support for parsing the grading key marking scheme.
     standard.py        Representing correct answers (standard).
     tests.py           System tests for essay grading algorithm code.
     text.py            Text processing independent of essay grading.
     wordnet.py:        Interface into WordNet (e.g., for term expansion)

Parameters for sentence matching (see answer.py):
    Name		Value	Desciption
    dist_threshold	0.25	cosine similarity threshold for single sentence match
    sen_threshold	0.33	similarity threshold for entire question
    multisen_matchrate	0.30	percentage of sentences that must mtach
    multisen_threshold	0.40	similarity threshold when multile sentences involved

For convenient testing of the new term expansion support, the following environment variables are supported:

    Variable                  Default  Description
    APPLY_SYNONYM_EXPANSION   False    Whether to apply synonym expansion via WordNe
    APPLY_ANCESTOR_EXPANSION  False    Whether to apply ancestor expansion via WordNet hypernys
    MAX_ANCESTOR_LINKS        5        Number of links in WordNet hypernym graph for ancestors
    USE_PART_OF_SPEECH        False    Prefix terms with part-of-speech label (        
    SYNONYM_SCALE_FACTOR      0.90     Factor applied to TF/IDF score after synonym expansion.
    ANCESTOR_SCALE_FACTOR     0.50     Factor applied to TF/IDF score after ancestor expansion.

Similarly, there are a few other environment overrides:
    Variable                  Default  Description
    EXCLUDE_LONG_TESTS 	      True     Allows for running complete set of tests
    USE_STUDENT_TEXT_DIST     False    To support term expansion, the tests in tests.py use the student global distribution (not standard). 
    SKIP_OVERRIDES	      False    Disables use of customized testing classes of code in answer.py and standard.py.
    DEBUG_LEVEL		      0	       Verbosity level for debugging traces.

To enable a setting, set the corresponding environment variable to "True" or "1" (without quotation marks).

Tom O'Hara
thomas.paul.ohara@gmail.com
Dec 2012

------------------------------------------------------------------------
Example illustrating term expansion

Under bash (from parent directory for algo):
  _COMMON_ENV="DEBUG_LEVEL=3 PYTHONPATH="$PWD" DJANGO_SETTINGS_MODULE=settings"
  out_base="answer"

  eval $_COMMON_ENV python -u new-algo/answer.py >| $out_base.default.output 2>&1
  eval $_COMMON_ENV APPLY_SYNONYM_EXPANSION=1 python -u new-algo/answer.py >| $out_base.syn.output 2>&1
  eval $_COMMON_ENV APPLY_ANCESTOR_EXPANSION=1 python -u new-algo/answer.py >| $out_base.anc.output 2>&1
  eval $_COMMON_ENV APPLY_SYNONYM_EXPANSION=1 APPLY_ANCESTOR_EXPANSION=1 python -u new-algo/answer.py >| $out_base.both.output 2>&1

Notes:
- This should be executed from the based directory for the Django code (with settings.py).
- DEBUG_LEVEL=3 is used to get tracing of the input and output.
- Python's -u option (unbuffered output) is used to synchronize standard output and error.

........................................................................
Sample output without term expansion (from answer.default.output)

note: This represents the intemass1009 version from Oct 2012 (see /home/aintemass/intemass1009 under aintemass.com).

Input:

Key: 1 . The attorney chased the ambulance.
2 . The ambulance chased back.

Scheme: [('all', 10), ('only P1 or P2', 5)]
Student: 1 . The lawyer chased the vehicle.
2 . The vehicle chased back.


Point_No: P1
stdsen: 1 ---  The attorney chased the ambulance.
stdvec: {'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}
Max Relevance: 0.912009323576
stusen: 1 --- The lawyer chased the vehicle.
stuvec: {'chased': 1.1736001944781467, 'lawyer': 2.3472003889562933, 'vehicle': 1.1736001944781467}
Relevant Keyword: ['chased', 'lawyer', 'vehicle']
expansion terms: ['attorney->lawyer']
Ingoring already matched sentence 1
Point_No: P2
stdsen: 2 ---  The ambulance chased back.
stdvec: {'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}
Max Relevance: 0.707106781187
stusen: 2 --- The vehicle chased back.
stuvec: {'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}
Relevant Keyword: ['chased', 'vehicle']
expansion terms: []
Result:

Mark: 10
List: ['P1', 'P2']
Omitted: ['C1 The attorney chased the ambulance. ', 'C2 The ambulance chased back. ']

........................................................................
Sample output with both synonym and ancestor term expansion (from answer.both.output)

Input:

Key: 1 . The attorney chased the ambulance downtown.
2 . The ambulance chased back.

Scheme: [('all', 10), ('only P1 or P2', 5)]
Student: 1 . The lawyer chased the vehicle downtown.
2 . The vehicle chased back.


Point_No: P1
stdsen: 1 ---  The attorney chased the ambulance downtown.
stdvec: {'downtown': 2.3472003889562933, 'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}
Max Relevance: 0.998617829333
stusen: 1 --- The lawyer chased the vehicle downtown.
stuvec: {'downtown': 2.3472003889562933, 'chased': 1.1736001944781467, 'lawyer': 2.3472003889562933, 'vehicle': 1.1736001944781467}
Relevant Keyword: ['downtown', 'chased', 'lawyer', 'vehicle']
expansion terms: ['attorney->lawyer', 'ambulance->vehicle']
Point_No: P2
stdsen: 2 ---  The ambulance chased back.
stdvec: {'downtown': 0, 'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}
Max Relevance: 0.998617829333
stusen: 2 --- The vehicle chased back.
stuvec: {'downtown': 0, 'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}
Relevant Keyword: ['chased', 'vehicle']
expansion terms: ['ambulance->vehicle']
Result:

Mark: 10
List: ['P1', 'P2']
Omitted: ['C1 The attorney chased the ambulance downtown. ', 'C2 The ambulance chased back. ']

------------------------------------------------------------------------
Dec. 2013

The scripts new-answer.py and new-standard.py fix the matching restrictions: word-once
and setence-once.
