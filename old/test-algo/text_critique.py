#! /usr/bin/python
#
# critique.py: Peforms qualitative analysis of texts (e.g., grammar checking)
#

from common import *

from check_grammar import check_text_grammar  # invokes external grammar checker
import nltk                             # NLP toolkit

#------------------------------------------------------------------------
# Class definition

class TextCritique:
    """Handles the critique of writing to determine specific errors or provide suggestions for improvement"""

    def __init__(self):
        """Initialize class instance"""
        self.text = ""                              # raw text
        self.grammar_issues = ""		    # report from grammar checer
        return
        
    def analyze(self, text):
        """Perform grammar checking of TEXT, etc."""
        self.text = text
        self.sentences = nltk.sent_tokenize(self.text)
        self.grammar_issues = self.get_grammatical_errors()
        return

    def get_grammatical_errors(self):
        """Returns report of grammar problems"""
        return check_text_grammar(self.text)

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

def calc_percentage(count, total):
    """Return percentage of COUNT over TOTAL as floating point value (e.g., 0.25)"""
    percentage = round(float(count) / total, 2) if (total > 0) else 0.0
    percentage = min(percentage, 1)
    return (percentage)

def main():
    """Main entry point for script"""
    debug_print("starting %s: %s" % (__file__, debug_timestamp()), 3)
    print_stderr("Warning: %s not really meant to be run standalone\n" % __file__)
    print_stderr("Running simple unit tests")
    tc = TextCritique()

    # Analyze text and show results
    dawg_text = "My dog has fleas.\nHis dawg were me.\nWho dawg you?\n"
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
