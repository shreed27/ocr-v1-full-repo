#!/usr/bin/env python
import ply.lex as lex
import ply.yacc as yacc
import itertools
import collections


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
        #print "Illegal character '%s', %s" % (t.value[0],t.type)
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
        #print "Syntax error in input, near [%s] " % p
        self.valid = False

    # Build the lexer & parser
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.parser = yacc.yacc(write_tables=0, debug=0, module=self, **kwargs)

    #-------------------------------------------------
    #follwoing parts are coupled with Marking System
    #-------------------------------------------------
    def clear(self):
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
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
                for sub in self.flatten(el):
                    yield sub
            else:
                yield el

    def calCombinations(self):
        if self.allFlag == 0:
            yield self.allpoints
        elif self.allFlag == 1:
            self.blockArray.reverse()
            combs = []
            onecomb = []
            allpointsSet = set(self.allpoints)
            for p, ops in self.blockArray:
                #print "p:%s,ops:%s" % (p,ops)
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
                #print "NUM:%d, List:%s, ops:%s" % (self.phraseAnyNumArray[i], self.phrasePointlistArray[i], self.anyOpsArray[i])
                if len(self.phrasePointlistArray[i]) == 0:
                    continue
                usefulArray = list(p for p in self.phrasePointlistArray[i] if p in allpointsSet)
                if self.phraseAnyNumArray[i] < 0:
                    usefulNum = 0
                elif self.phraseAnyNumArray[i] > len(self.phrasePointlistArray[i]):
                    usefulNum = len(self.phrasePointlistArray[i])
                else:
                    usefulNum = self.phraseAnyNumArray[i]
                    #print "NUM:%d, List:%s" % (usefulNum,usefulArray)
                #print usefulArray,usefulNum
                onecombs = list(list(comb) for comb in itertools.combinations(usefulArray, usefulNum))
                phrasecombs.append(onecombs)
                #print "phrasecombs:%s, len:%s" % (phrasecombs, len(phrasecombs))
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
                #print "NUM:%d, List:%s, ops:%s" % (self.phraseAnyNumArray[i], self.phrasePointlistArray[i],self.anyOpsArray[i])
                if len(self.phrasePointlistArray[i]) == 0:
                    continue
                usefulArray = list(p for p in self.phrasePointlistArray[i] if p in allpointsSet)
                if self.phraseAnyNumArray[i] < 0:
                    usefulNum = 0
                elif self.phraseAnyNumArray[i] > len(self.phrasePointlistArray[i]):
                    usefulNum = len(self.phrasePointlistArray[i])
                else:
                    usefulNum = self.phraseAnyNumArray[i]
                #print "NUM:%d, List:%s" % (usefulNum,usefulArray)
                usefulSet = set(usefulArray)
                onecombs = list(list(usefulSet - set(comb)) for comb in itertools.combinations(usefulArray, usefulNum))
                phrasecombs.append(onecombs)
                #print "phrasecombs:%s" % phrasecombs
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

    def __init__(self, allpoints):
        self.build()
        self.allpoints = allpoints
        self.clear()

    def analysis(self, sent, mark):
        #self.lexer.input(sent)
        #while True:
        #    tok = self.lexer.token()
        #    if not tok: break
        #    print tok
        self.clear()
        self.parser.parse(sent, lexer=self.lexer)
        if self.valid:
            for rule in self.calCombinations():
                yield rule, mark
        else:
            yield None

if __name__ == "__main__":
    allpoints = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P3.24', 'P03.240']
    print "All Points:%s\n" % allpoints
    sc = MarkingSchemeLang(allpoints)
    data = []
    ##########################################
    #Negative cases
    data += [("all except P3 and P22", 8)]
    data += [("only P1 or s", 1)]
    data += [("only some  from all", 1)]
    data += [("only 2 from all", 3)]
    ##########################################
    #Positive cases
    data += [("all less P5", 8)]
    data += [("all less P3 and P22 or P4 and P5 or P6 or P7", 8)]
    data += [("all", 10)]
    data += [("only P1 or P6 and P7 and P4 or P88 or P89 or P90 and P2", 3)]
    data += [("only P1 or P3.24", 1)]
    data += [("only P1 or P03.240", 1)]
    data += [("any 2 combinations of P1;P3 ; P5 ;P99; P7", 1)]
    data += [("any 2 combinations of P1;P3 ; P5 ;P99; P7 and any 1 combinations of P4;P6 and any 3 combinations of P2;P3.24", 1)]
    data += [("less 2 combinations of P1;P3 ; P5 ;P99; P7 and less 1 combinations of P4;P6 and less 3 combinations of P2;P3.24", 1)]
    data += [("all less 2 combinations of P1;P3;P5;P9", 1)]
    data += [("all less -1 combinations of P1;P3;P5;P9", 1)]
    data += [("all less 4 combinations of P1;P3;P5;P9", 1)]
    data += [("all less 0 combinations of P1;P3;P5;P9", 1)]
    for sent, score in data:
        print "Sent:%s | Score:%d" % (sent, score)
        rlist = sc.analysis(sent, score)
        if not rlist:
            print "This sentence cannot fit grammar"
            print "--------------------------\n"
            continue
        for rule, score in rlist:
            print "Rule:%s | Score:%d" % (rule, score)
        print "--------------------------\n"
