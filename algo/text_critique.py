#! /usr/bin/python
#
# critique.py: Peforms qualitative analysis of texts (e.g., grammar checking)
#

from common import *

from check_grammar import check_text_grammar  # invokes external grammar checker
import nltk                             # NLP toolkit

# OS support
import sys

#------------------------------------------------------------------------
# Class definition

class TextCritique:
    """Handles the critique of writing to determine specific errors or provide suggestions for improvement"""

    def __init__(self):
        """Initialize class instance"""
        self.text = ""                              # raw text
        self.grammar_issues = ""		    # report from grammar checer
        self.detailed_grammar_results = {}	    # hash with grammar checking details
        return
        
    def analyze(self, text):
        """Perform grammar checking of TEXT, etc."""
        self.text = normalize(text)
        self.sentences = nltk.sent_tokenize(self.text)
        self.grammar_issues = self.get_grammatical_errors()
        return

    def get_grammatical_errors(self):
        """Returns report of grammar problems"""
        # TODO: put percent-ungrammatical support in check_grammar
        if (self.grammar_issues == ""):
            self.grammar_issues = check_text_grammar(self.text, results_hash=self.detailed_grammar_results)
            self.detailed_grammar_results['percent-ungrammatical'] = str(self.percent_grammar_errors())
        return self.grammar_issues

    def get_detailed_grammar_results(self):
        """Returns hash with detailed results of grammar checking, includes following keys:  score, synopsis, report and details."""
        return self.detailed_grammar_results

    def num_grammatical_errors(self):
        """Returns number of grammar errors in current text"""
        return (len(re.findall(r"^\d+\.\)", self.grammar_issues, re.MULTILINE)))

    def percent_grammar_errors(self):
        """Returns degree of grammar errors as percentage of sentences"""
        num_grammar_errors = self.num_grammatical_errors()
        # TODO: use number of clauses rather than number of sentences
        num_sentences = len(self.sentences)
        result = calc_percentage(num_grammar_errors, num_sentences)
        return result

#------------------------------------------------------------------------
# Functions

def hex_string(text):
    """Returns TEXT as string of hexadecimal (i.e., hexdump)"""
    return(":".join(b.encode('hex') for b in text))

def utf8(text):
    """Converts unicode string to UTF8"""
    result = text.encode('utf8')
    debug_print("utf8(%s) => %s (%s)" % (text, result, hex_string(result)), 7)
    return result

def normalize(text):
    """Normalize text to account for likely problems with the critiques, mostly with non-ascii characters like smart quotes converted to ascii"""
    debug_print("normalize(): text={\n%s}\ntype=%s: hex=%s\n" % (text, type(text), hex_string(text)), 6)
    text = text.replace("\t", "    ")         # expand tabs
    if (type(text) == unicode):
        text = text.replace(u'\u2018', "'")   # opening single quote
        text = text.replace(u'\u2019', "'")   # closing single quote
        text = text.replace(u'\u201C', '"')   # opening double quote
        text = text.replace(u'\u201D', '"')   # closing double quote
        text = text.replace(u'\u00A0', " ")   # non-breaking space
        text = text.replace(u'\u2013', "-")   # en dash
    else: 
        text = text.replace("\x91", "'")      # opening single quote (U+2018)
        text = text.replace("\x92", "'")      # closing single quote (U+2019)
        text = text.replace("\x93", '"')      # opening double quote (U+201C)
        text = text.replace("\x94", '"')      # closing double quote (U+201D)
        text = text.replace("\xA0", " ")      # non-breaking space (U+00A0)
        text = text.replace("\x96", "-")      # en dash (U+2013)

    # Replace question point indicators with spaces
    # ex: "1 . Lawyers practice law." => "Lawyers practice law."
    # Note: dummy newline added temporarily to facilitate pattern matching
    text = "\n" + text
    match = True
    while (not match is None):
        match = re.search(r"^(.*)\n(\s*\d+\s+\.\s+)(.*)$", text, re.DOTALL)
        if match:
            spaces = " " * len(match.group(2))
            text = match.group(1) + "\n" + spaces + match.group(3)
    assert(text[0] == "\n")
    text = text[1:]

    debug_print("normalize()=>{%s}\nhex=%s\n" % (text, hex_string(text)), 6)
    return (text)

def calc_percentage(count, total):
    """Return percentage of COUNT over TOTAL as floating point value (e.g., 0.25)"""
    percentage = round(float(count) / total, 2) if (total > 0) else 0.0
    percentage = min(percentage, 1.0)
    return (percentage)

def read_file(filename):
    """Read all of the text in FILENAME"""
    with open(filename, 'r') as f:
        text = f.read()
    debug_print("read_file(%s) => %s" % (filename, text), 6)
    return text

def main():
    """Main entry point for script"""
    debug_print("starting %s: %s" % (__file__, debug_timestamp()), 3)
    tc = TextCritique()

    # If argument given, run grammar checking over file
    if len(sys.argv) > 1:
        text = read_file(sys.argv[1])
        tc.analyze(text)
        ## OLD: print "results: %s" % tc.get_detailed_grammar_results()
        print "results:"
        results = tc.get_detailed_grammar_results()
        for key in results.keys():
            print "%s: {\t%s\n}" % (key, results[key].replace("\n", "\n\t"))
        return

    # Otherwise run canned example
    print_stderr("Running simple unit tests")

    # Analyze text and show results
    dawg_text = "1 . My dog has fleas.\n2 . His dawg were me.\n3 . Who dawg you?\n"
    tc.analyze(dawg_text)
    print("text: {\n%s}" % dawg_text)
    print("grammar issues: {\n%s}" % tc.get_grammatical_errors())
    print("grammar percentage: %s" % tc.percent_grammar_errors())

    # Run unit tests for expected results
    # TODO: convert assertions into unit tests proper
    assert(tc.num_grammatical_errors() == 1)
    assert(0.30 < tc.percent_grammar_errors() < 0.50)
    print("Unit tests passed!")
    debug_print("ending %s: %s" % (__file__, debug_timestamp()), 3)
    return

if __name__ == '__main__':
    main()
