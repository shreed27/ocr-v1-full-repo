#! /usr/bin/python
#
# markscheme.py: Defines simple class for accessing rules produced when parsing
# marking schemes via MarkingSchemeLang (see scheme_lang.py).
# Warning: *** This is not used anywhere except for tests.py. ***
# TODO: Make MarkScheme a class embedded in tests.py (to avoid confusion)???
#

# Local packages
#
from common import *
debug_print("algo/markscheme.py: " + debug_timestamp())
from scheme_lang import *

# Other packages
#
import logging

class MarkScheme(object):

    # constructor: initializes instance using given list of question/point names
    # EX: ms = MarkScheme(['P1.1', 'P1.2', 'P2', 'P3', 'P4'])
    def __init__(self, plist):
        debug_print("MarkScheme(%s)" % str(plist), level=5)
        self.logger = logging.getLogger(__name__)
        self.msl = MarkingSchemeLang(plist)
        self.plist = plist

    ## TODO: remove following unused method 
    '''def filterZero(self,string):
        string = string.group(0)
        if string[2] == '0':
            return 'P'+string[0]
        else:
            return 'P'+string'''

    # GetRules(MARKED_GRADING_SPECS): Parses each of the grading specifications
    # with associated grade in MARKED_GRADING_SPECS, returning list with 
    # EX: list(ms.GetRules([("all less P4", 75), ("only P1.1", 10)])) => [{'Mark': 75, 'Point': ['P2', 'P1.2', 'P1.1', 'P3']}, {'Mark': 10, 'Point': ['P1.1']}]
    def GetRules(self, templates):
        debug_print("in GetRules(%s)" % str(templates), level=5)
        for rule, mark in templates:
            rlist = self.msl.analysis(rule, int(mark))
            for rule, score in rlist:
                rule_hash = {'Point': rule, 'Mark': score}
                debug_print("yielding %s\n" % str(rule_hash), level=6)
                yield {'Point': rule, 'Mark': score}
        debug_print("out GetRules()", level=5)

# Run simple example if invoked from command line
#
if __name__ == "__main__":
    debug_print("start: " + debug_timestamp())
    #
    print "Simple example"
    print

    # Initialize simple rule scheme spcification and display
    points = ['P7', 'P2', 'P13']
    templates = [("all", 100), 
                 ("any two combinations of P7 ; P2 ; P13", 67.7),
                 ("only P7 or P2 or P13", 33.3),
                 ("none", 0)]
    print "Input:"
    print "\tpoints: %s" % points
    print
    print "\ttemplates:\n\t%s\n" % "\n\t".join([str(t) for t in templates])
    print

    # Run through scheme parser
    # Note: generator output expanded here to traps exceptions
    #
    print "Output:"
    try:
        ms = MarkScheme(points)
        rules = [r for r in ms.GetRules(templates)]
    except:
        rules = None
        # Pass along exception if debugging, otherwise just print info to stderr
        if __debug__:
            raise
        print_stderr("Exception processing sentence:\n\t%s" % str(sys.exc_info()))

    # Show result
    #
    for rule_hash in rules:
        for key in rule_hash.keys():
            print "%s: %s" % (key, rule_hash[key]),
        print
