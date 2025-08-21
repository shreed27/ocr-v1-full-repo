#!/usr/bin/env python
#
# scheme_lang.py: defines MarkingSchemeLang class for parsing the grading key marking scheme.
# Note: includes simple usage example when run standalone.
#
# Grammar:
#   
#   expression ::= <all_sent> | <only_sent> | <any_sent> | <less_ent>
#   
#   all_sent ::= "ALL"
#              | "ALL LESS" <block>
#              | "ALL LESS NUMBER COMBINATIONS OF" <point_list>
#   
#   only_sent ::= "ONLY" <block>
#   
#   less_sent ::= <less_phrase>
#               | <less_phrase> "AND" <less_sent>
#               | <less_phrase> "OR" <less_sent>
#   
#   any_sent  ::= <any_phrase>
#               | <any_phrase> "AND" <any_sent>
#               | <any_phrase> "OR" <any_sent>
#   
#   any_phrase ::= "ANY" <number> "COMBINATIONS OF" <point_list>
#   
#   less_phrase ::= "LESS" <number> "COMBINATIONS OF" <point_list>
#   
#   point_list ::= <point>
#                | <point> ";" <point_list>
#   
#   block ::= <point>
#           | <point> "AND" <block>
#           | <point> "OR" <block>
#   
#   point ::= "P"<number>["."<number>]
#   
#   number ::= [0-9]+
#
#------------------------------------------------------------------------
# TODO: Cut down on excessive use of generators as efficiency is memory overhead
# is not an issue with the parser. This needlessly makes the code hard to maintain:
# the logic is harder to follow, and the code is harder to debug.
#

import ply.lex as lex
import ply.yacc as yacc
import itertools
import collections

# Load supporting libraries
#
from common import *

class MarkingSchemeLang(object):

    # List of supported token names from scheme language
    tokens = (
        'NUMBER',
        'POINT',
        'ALL',
        'ONLY',
        'LESS',
        'OF',
        'AND',
        'OR',
        'ANY',
        'COMBINATIONS',
        'PSEP'
    )

    #-------------------------------------------------
    #lexicon lay
    #lex like
    #-------------------------------------------------

    # Regular expression rules for simple tokens
    t_ALL = r'\ball\b'
    t_LESS = r'\bless\b'
    t_ONLY = r'\bonly\b'
    t_OF = r'\bof\b'
    t_AND = r'\band\b'
    t_OR = r'\bor\b'
    t_ANY = r'\bany\b'
    t_COMBINATIONS = r'\bcombinations\b'
    t_PSEP = r';'

    def t_NUMBER(self, t):
        r'\b\d+\b'
        t.value = int(t.value)
        return t

    def t_POINT(self, t):
        r'\bP\d+(\.\d+)*\b'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    #ignore white space and tab
    t_ignore = ' \t'

    def t_error(self, t):
        debug_print("Illegal character '%s', %s" % (t.value[0],t.type))
        t.lexer.skip(1)
        self.valid = False

    #-------------------------------------------------
    #syntax layer
    #yacc like
    #-------------------------------------------------

    def p_expression(self, p):
        '''expression   : allsent
                        | onlysent
                        | anysent
                        | lesssent'''

    def p_allsent(self, p):
        '''allsent  : ALL
                    | ALL LESS block
                    | ALL LESS NUMBER COMBINATIONS OF pointlist'''
        if len(p) == 2:
            self.allFlag = 0
        elif len(p) == 4:
            self.allFlag = 1
        elif len(p) == 7:
            self.allFlag = 2
            self.allNum = p[3]
        else:
            print "len:%d" % len(p)

    def p_onlysent(self, p):
        '''onlysent : ONLY block'''
        if len(p) == 3:
            self.orFlag = 0

    def p_lesssent(self, p):
        '''lesssent  : lessphrase
                    | lessphrase AND lesssent
                    | lessphrase OR lesssent'''
        self.lessFlag = 1
        if len(p) == 2:
            self.lessOpsArray.append("last")
        else:
            self.lessOpsArray.append(p[2])

    def p_anysent(self, p):
        '''anysent  : anyphrase
                    | anyphrase AND anysent
                    | anyphrase OR anysent'''
        self.anyFlag = 1
        if len(p) == 2:
            self.anyOpsArray.append("last")
        else:
            self.anyOpsArray.append(p[2])

    def p_anyphrase(self, p):
        '''anyphrase : ANY NUMBER COMBINATIONS OF pointlist'''
        self.phrasePointlistArray.append(self.pointlistArray)
        self.phraseAnyNumArray.append(p[2])
        self.pointlistArray = []

    def p_lessphrase(self, p):
        '''lessphrase : LESS NUMBER COMBINATIONS OF pointlist'''
        self.phrasePointlistArray.append(self.pointlistArray)
        self.phraseAnyNumArray.append(p[2])
        self.pointlistArray = []

    def p_pointlist(self, p):
        '''pointlist : POINT
                     | POINT PSEP pointlist'''
        if len(p) > 2:
            self.pointlistArray.append(p[1])
        elif len(p) == 2:
            self.pointlistArray.append(p[1])
        else:
            print p

    def p_block(self, p):
        '''block    : POINT
                    | POINT AND block
                    | POINT OR block'''

        if len(p) > 2:
            self.blockArray.append((p[1], p[2]))
        elif len(p) == 2:
            self.blockArray.append((p[1], "last"))
        else:
            print p

    # Error rule for syntax errors
    def p_error(self, p):
        debug_print("MarkingSchemeLang:p_error(%s)" % p)
        self.valid = False

    # Build the lexer & parser
    def build(self, **kwargs):
        debug_print("MarkingSchemeLang:build(%s)" % str(kwargs), level=5)
        self.lexer = lex.lex(module=self, **kwargs)
        self.parser = yacc.yacc(write_tables=0, debug=0, module=self, **kwargs)

    #-------------------------------------------------
    #following parts are coupled with Marking System
    #-------------------------------------------------
    def clear(self):
        debug_print("MarkingSchemeLang:clear()", level=5)
        self.allFlag = None
        self.orFlag = None
        self.anyFlag = None
        self.lessFlag = None
        self.blockArray = []
        self.pointlistArray = []
        self.anyOpsArray = []
        self.lessOpsArray = []
        self.phrasePointlistArray = []
        self.phraseAnyNumArray = []
        self.valid = True

    def flatten(self, l):
        debug_print("MarkingSchemeLang:flatten(%s)" % l, level=5)
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
                for sub in self.flatten(el):
                    yield sub
            else:
                yield el

    def calCombinations(self):
        debug_print("MarkingSchemeLang.calCombinations()", level=5)
        if self.allFlag == 0:
            yield self.allpoints
        elif self.allFlag == 1:
            self.blockArray.reverse()
            combs = []
            onecomb = []
            allpointsSet = set(self.allpoints)
            for p, ops in self.blockArray:
                debug_print("p:%s,ops:%s" % (p, ops), level=5)
                if p in allpointsSet:
                    onecomb.append(p)
                if ops == "or" or ops == "last":
                    yield list(allpointsSet - set(onecomb))
                    onecomb = []
                elif ops == "and":
                    pass
                else:
                    assert False
            for comb in combs:
                yield comb
        elif self.allFlag == 2:
            allpointsSet = set(self.allpoints)
            usefulArray = list(p for p in self.pointlistArray if p in allpointsSet)
            if self.allNum > len(usefulArray):
                usefulNum = len(usefulArray)
            else:
                usefulNum = self.allNum
            combs = []
            for onecomb in itertools.combinations(usefulArray, usefulNum):
                combs.append(list(allpointsSet - set(onecomb)))
            for comb in combs:
                yield comb
        # TODO: remove following old code
        #elif self.orFlag == 1:
        #    combs=[]
        #    for comb in itertools.combinations(self.allpoints,self.orNum):
        #        combs.append(list(comb))
        #    yield combs
        elif self.orFlag == 0:
            self.blockArray.reverse()
            combs = []
            onecomb = []
            allpointsSet = set(self.allpoints)
            for p, ops in self.blockArray:
                if p not in allpointsSet:
                    continue
                onecomb.append(p)
                if ops == "or" or ops == "last":
                    combs.append(onecomb)
                    onecomb = []
                elif ops == "and":
                    pass
                else:
                    assert False
            for comb in combs:
                yield comb
        elif self.anyFlag == 1:
            if len(self.phraseAnyNumArray) != len(self.phrasePointlistArray) or len(self.phraseAnyNumArray) != len(self.anyOpsArray):
                assert False
            combs = []
            phrasecombs = []
            allpointsSet = set(self.allpoints)
            self.anyOpsArray.reverse()
            for i in range(len(self.phraseAnyNumArray)):
                debug_print("NUM:%d, List:%s, ops:%s" % (self.phraseAnyNumArray[i], self.phrasePointlistArray[i], self.anyOpsArray[i]), level=6)
                if len(self.phrasePointlistArray[i]) == 0:
                    continue
                usefulArray = list(p for p in self.phrasePointlistArray[i] if p in allpointsSet)
                if self.phraseAnyNumArray[i] < 0:
                    usefulNum = 0
                elif self.phraseAnyNumArray[i] > len(self.phrasePointlistArray[i]):
                    usefulNum = len(self.phrasePointlistArray[i])
                else:
                    usefulNum = self.phraseAnyNumArray[i]
                    debug_print("NUM:%d, List:%s" % (usefulNum, str(usefulArray)), level=6)
                debug_print("usefulArray=%s, usefulNum=%d" % (str(usefulArray), usefulNum), level=6)
                onecombs = list(list(comb) for comb in itertools.combinations(usefulArray, usefulNum))
                phrasecombs.append(onecombs)
                debug_print("phrasecombs:%s, len:%d" % (phrasecombs, len(phrasecombs)), level=6)
                if self.anyOpsArray[i] == "and":
                    pass
                else:
                    if len(phrasecombs) == 1:
                        for comb in phrasecombs[0]:
                            combs.append(comb)
                        phrasecombs = []
                    elif len(phrasecombs) > 1:
                        for comb in reduce(lambda x, y: itertools.product(x, y), phrasecombs):
                            flattenComb = list(flattenItem for flattenItem in self.flatten(comb))
                        phrasecombs = []
                    else:
                        assert False
            for comb in combs:
                yield comb
        elif self.lessFlag == 1:
            if len(self.phraseAnyNumArray) != len(self.phrasePointlistArray) or len(self.phraseAnyNumArray) != len(self.lessOpsArray):
                assert False
            combs = []
            phrasecombs = []
            allpointsSet = set(self.allpoints)
            self.lessOpsArray.reverse()
            for i in range(len(self.phraseAnyNumArray)):
                debug_print("NUM:%d, List:%s, ops:%s" % (self.phraseAnyNumArray[i], self.phrasePointlistArray[i], self.anyOpsArray[i]), level=6)
                if len(self.phrasePointlistArray[i]) == 0:
                    continue
                usefulArray = list(p for p in self.phrasePointlistArray[i] if p in allpointsSet)
                if self.phraseAnyNumArray[i] < 0:
                    usefulNum = 0
                elif self.phraseAnyNumArray[i] > len(self.phrasePointlistArray[i]):
                    usefulNum = len(self.phrasePointlistArray[i])
                else:
                    usefulNum = self.phraseAnyNumArray[i]
                debug_print("usefulArray=%s, usefulNum=%d" % (str(usefulArray), usefulNum), level=6)
                usefulSet = set(usefulArray)
                onecombs = list(list(usefulSet - set(comb)) for comb in itertools.combinations(usefulArray, usefulNum))
                phrasecombs.append(onecombs)
                debug_print("phrasecombs:%s, len:%d" % (phrasecombs, len(phrasecombs)), level=6)
                if self.lessOpsArray[i] == "and":
                    pass
                else:
                    if len(phrasecombs) == 1:
                        for comb in phrasecombs[0]:
                            combs.append(comb)
                        phrasecombs = []
                    elif len(phrasecombs) > 1:
                        for comb in reduce(lambda x, y: itertools.product(x, y), phrasecombs):
                            flattenComb = list(flattenItem for flattenItem in self.flatten(comb))
                            combs.append(flattenComb)
                        phrasecombs = []
                    else:
                        assert False
            for comb in combs:
                yield comb

    # MarkingSchemeLang(point_list): Initialize for marking question names in POINT_LIST.
    # EX: msl = MarkingSchemeLang(['P1.1', 'P1.2', 'P2', 'P3', 'P4'])
    #
    def __init__(self, allpoints):
        debug_print("MarkingSchemeLang:clear()", level=5)
        self.build()
        self.allpoints = allpoints
        self.clear()

    # analysis(GRADING_SPEC, SCORE): Generator for converting GRADING_SPEC into sequence of
    # rules having the associated SCORE. If valid each item is a tuple with rule text and score value,
    # otherwise, None is generated.
    # EX: [r for r in msl.analysis("all less P4", 75.5)] => [(['P2', 'P1.2', 'P1.1', 'P3'], 75.5)]
    #
    def analysis(self, sent, mark):
        debug_print("in MarkingSchemeLang:analysis(\"%s\", %d)" % (sent, mark), level=5)
        if __debug__:
            debug_print("lexical analysis:", level=5)
            self.lexer.input(sent)
            while True:
                tok = self.lexer.token()
                if not tok: 
                    break
                debug_print("tok=%s" % tok, level=6)
        self.clear()
        debug_print("parsing sent:", level=5)
        self.parser.parse(sent, lexer=self.lexer)
        if self.valid:
            for rule in self.calCombinations():
                debug_print("MarkingSchemeLang:analysis() yields %s" % str((rule, mark)), level=6)
                yield rule, mark
        else:
            debug_print("MarkingSchemeLang:analysis() yields None", level=6)
            yield None
        debug_print("out MarkingSchemeLang:analysis()", level=5)


# show_simple_example(): Runs a simple example of grading scheme parsing.
#
def show_simple_example():
    # Test running example from comments above
    # TODO: Do this via unit testing framework (Python or Django)
    if __debug__:
        debug_print("Debugging example")
        points = ['P1.1', 'P1.2', 'P2', 'P3', 'P4']
        spec = "all less P4"
        mark = 75.5
        debug_print("points=%s spec='%s' mark=%f" % (points, spec, mark))
        msl = MarkingSchemeLang(points)
        result = [r for r in msl.analysis(spec, mark)]
        debug_print("result: %s" % str(result))
    
    # Create the example specification
    print "Simple example"
    print
    points = ['P1.1', 'P1.2', 'P2', 'P3', 'P4']
    spec = "all less 2 combinations of P2;P3;P4"
    mark = 70
    print "Points: %s" % str(points)
    print "Spec: %s" % spec
    print "Mark: %d" % mark

    # Analyze the specification and display the expanded rules
    msl = MarkingSchemeLang(points)
    for (rule, score) in msl.analysis(spec, mark):
        print "Rule: %s; Score: %d" % (rule, score)
    print


# Run simple test if invoked from command line
#
if __name__ == "__main__":
    debug_print("start: " + debug_timestamp())

    # First show simple example if debugging (for tracing purposes)
    if __debug__:
        show_simple_example()

    # Initialize the grading scheme parsing
    print "Test set"
    allpoints = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P3.24', 'P03.240']
    print "All Points:%s\n" % allpoints
    sc = MarkingSchemeLang(allpoints)

    # Create simple test set
    # Note: Negative tests must come first
    data = []
    ##########################################
    #Negative cases
    data += [("all except P3 and P22", 8)]
    data += [("only P1 or s", 1)]
    data += [("only some  from all", 1)]
    data += [("only 2 from all", 3)]
    num_neg_tests = len(data)
    ##########################################
    #Positive cases
    data += [("all less P5", 8)]
    data += [("all less P3 and P22 or P4 and P5 or P6 or P7", 8)]
    data += [("all", 10)]
    data += [("only P1 or P6 and P7 and P4 or P88 or P89 or P90 and P2", 3)]
    data += [("only P1 or P3.24", 1)]
    data += [("only P1 or P03.240", 1)]
    data += [("any 2 combinations of P1;P3 ; P5 ;P99; P7", 1)]
    data += [("any 2 combinations of P1;P3 ; P5 ;P99; P7 and any 1 combinations of P4;P6 and any 3 combinations of P2;P3.24", 1)]	# TODO: make negative
    data += [("less 2 combinations of P1;P3 ; P5 ;P99; P7 and less 1 combinations of P4;P6 and less 3 combinations of P2;P3.24", 1)]	# TODO: make negative
    data += [("all less 2 combinations of P1;P3;P5;P9", 1)]
    data += [("all less -1 combinations of P1;P3;P5;P9", 1)]   # TODO: make negative
    data += [("all less 4 combinations of P1;P3;P5;P9", 1)]
    data += [("all less 0 combinations of P1;P3;P5;P9", 1)]

    # Analyze each case and show results
    num_good = 0
    test_num = 0
    for sent, score in data:
        # Try to parse the grading scheme and point specification.
        # Note: generator output expanded here to encapsulate exceptions.
        negative_test = (test_num < num_neg_tests)
        test_num += 1
        print "Test:%d Sent:'%s' | Score:%d | Negative:%s" % (test_num, sent, score, negative_test)
        try:
            rlist = [tuple for tuple in sc.analysis(sent, score) if tuple]
        except:
            rlist = None
            if (negative_test or (debugging_level() > 3)):
                print_stderr("Exception processing sentence:\n\t%s" % str(sys.exc_info()))

        # See if test worked as expected
        negative_result = (not rlist)
        if (negative_test == negative_result):
            num_good += 1
        else:
            print_stderr("Error: *** Unexpected test result")

        # Display the result
        debug_print("rlist: %s" % str(rlist))
        if negative_result:
            print "This sentence cannot fit grammar"
            print "--------------------------\n"
            continue
        for rule, score in rlist:
            print "Rule:%s | Score:%d" % (rule, score)
            print "--------------------------\n"

    # Print summary
    print "%d of %d rules processed as expected" % (num_good, len(data))

    # End of processing
    debug_print("stop: " + debug_timestamp(), level=2)
