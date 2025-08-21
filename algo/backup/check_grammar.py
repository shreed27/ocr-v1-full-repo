#! /usr/bin/python
#
# check-grammar.py: run text through grammar checker (e.g., the one from OpenOffice)
#
# Sample input:
#    This be me car over over there
#
# Sample output:
#    Line 1, column 16, Rule ID: ENGLISH_WORD_REPEAT_RULE
#    Message: Possible typo: you repeated a word
#    Suggestion: over
#    This be me car over over there 
#                   ^^^^^^^^^
#
# ------------------------------------------------------------------------
# Notes:
# - The LANGUAGE_TOOL_HOME environment variable specified the distribution
# directory for the grammar checker. See run-languagetool-grammar-checker.sh.
#

#------------------------------------------------------------------------
# Library packages

from common import *

# OS support
import os
import sys
import commands
import tempfile

#------------------------------------------------------------------------
# Functions

def run_command(command_line, level=5):
    """Runs COMMAND_LINE and returns the output (as a string), with debug tracing at specified LEVEL"""
    # Issue command
    debug_print("Running command: %s" % command_line, level=level)
    (status, output) = commands.getstatusoutput(command_line)
    if (status != 0):
        print_stderr("Warning: problem running command (status=%d): %s" % (status, command_line))

    # Return output
    debug_print("Command output: %s\n" % output, level=level+1)
    return (output)

def read_file(filename):
    """Read all of the text in FILENAME"""
    with open(filename, 'r') as f:
        text = f.read()
    debug_print("read_file(%s) => %s" % (filename, text), 6)
    return text

def check_file_grammar(filename, brief=True, results_hash=None):
    """Run grammar checker over FILENAME, optionally displaying BRIEF descriptions (i.e., non-technical) and also returning detailed results in a HASH with following keys:  score, synopsis, report, and details."""
    # Get command output
    script_dir = os.path.dirname(__file__)
    debug_print("script_dir: %s" % script_dir, 5)
    if script_dir == "":
        script_dir = "."
        debug_print("revised script_dir: %s" % script_dir, 5)
    command_line = "bash %s/run-languagetool-grammar-checker.sh %s" % (script_dir, filename)
    grammar_issues = run_command(command_line)

    # Prepare hash with detailed results
    if not results_hash is None:
        assert(type(results_hash) == dict)
        results_hash['details'] = grammar_issues
        file_text = read_file(filename)
        results_hash['score'] = str(round(score_grammar_results(grammar_issues, file_text), 3))

    # Remove trace messages output
    # ex: "No language specified, using English\nWorking on D:\cartera-de-tomas\apeters-essay-grading\bad-grammar-example.txt...\n"
    # ex: "Time: 171ms for 1 sentences (5.8 sentences/sec)"
    grammar_issues = re.sub(r"No language specified.*", "", grammar_issues)
    grammar_issues = re.sub(r"Expected text language:.*", "", grammar_issues)
    grammar_issues = re.sub(r"Working on.*", "", grammar_issues)
    grammar_issues = re.sub(r"Time:.*", "", grammar_issues)

    # Remove technical labels, etc
    if (brief):
        # ex: "Line 31, column 1, Rule ID: ENGLISH_WORD_REPEAT_BEGINNING_RULE" => "Line 31, column 1:
        grammar_issues = re.sub(",\s*Rule: ID: \S+", "", grammar_issues)

    # Add pruned version to detailed-results hash
    if not results_hash is None:
        results_hash['synopsis'] = grammar_issues
        results_hash['report'] = "Score: " + results_hash['score'] + "\n"
        results_hash['report'] += "Issues: " + (grammar_issues if grammar_issues.strip() else "n/a") + "\n"
    return grammar_issues

def check_text_grammar(text, brief=True, results_hash=None):
    """Run grammar checker over TEXT"""
    temp_file=tempfile.NamedTemporaryFile()
    debug_print("temp_file: %s" % temp_file.name, 3)
    with open(temp_file.name, 'w') as f:
        f.write(text)
    return check_file_grammar(temp_file.name, brief, results_hash)

# Penalties for specific grammar errors. This is only needed if penalty different from default (1):
# it is used to boost the penalty for bad issues, reduce it for trivial ones, and to ignore rules.
ISSUE_PENALTY = {
    # Boost penalty
    'ENGLISH_WORD_REPEAT_RULE': 1.5,
    'ENGLISH_WORD_REPEAT_BEGINNING_RULE': 0.5,    
    # Reduce penalty
    'POSSESIVE_APOSTROPHE[2]': 0.25,
    # Ignore
    'KEY_WORDS[1]': 0.0,
    }

def score_grammar_results(grammar_issues, text):
    """Returns score for grammatical ISSUES that occurred in TEXT in rangle [0, 1] with 0 being worst"""
    # Note: The score is based on number of grammatical errors relative to the size of the text.
    # In the Kaggle essay grading data, which covers upper middle school and lower high school,
    # there is an average of one grammar error every 150 words (0.0067).
    debug_print("score_grammar_results(_,_)", 4)
    tokens = [t.strip() for t in re.split("(\W+)", text) if (len(t.strip()) > 0)]
    num_tokens = len(tokens)
    all_issues = re.findall(r"Rule ID: (\S+)", grammar_issues)
    total_penalty = 0.0
    num_issues = 0
    for issue in all_issues:
        penalty = ISSUE_PENALTY[issue] if issue in ISSUE_PENALTY else 1
        assert(penalty >= 0)
        if penalty > 0:
            total_penalty += penalty
            num_issues += 1
    debug_print("Num grammar issues: %s; penalty: %s; issues: %s" % (num_issues, total_penalty, all_issues), 4)

    # Determine factor for excessive number of errors relative to size of text
    issue_ratio = (num_issues / float(num_tokens)) if (num_tokens > 0) else 0.0
    excess_factor = issue_ratio / 0.0067
    debug_print("Num tokens: %d; issue ratio: %g; excess factor: %g" % (num_tokens, issue_ratio, excess_factor), 5)

    # Calculate final score (with excess factor used only to decrease score not improve)
    if (excess_factor > 1):
        total_penalty += excess_factor
    score = (1.0 / (1 + total_penalty)) if (total_penalty > 0) else 1.0
    debug_print("Grammar score: %g; total penalty: %g" % (score, total_penalty), 4)
    assert(0.0 <= score <= 1.0)
    return (score)

def main():
    """
    Main routine: parse arguments and perform grammar checking over file or text.
    Note: main() used to avoid conflicts with globals (e.g., if done at end of script).
    """
    # Init
    debug_print("start %s: %s" % (__file__, debug_timestamp()), 3)

    # Parse command-line, showing usage statement if no arguments given (or --help)
    args = sys.argv
    debug_print("argv = %s" % sys.argv, 3)
    num_args = len(args)
    if ((num_args == 1) or ((num_args > 1) and (args[1] == "--help"))):
        print_stderr("Usage: %s [--brief | --full] [--score] [--text text] [--help] file" % args[0])
        print_stderr("")
        print_stderr("Notes:")
        print_stderr(" - set LANGUAGE_TOOL_HOME environment variable to directory for LanguageTool distribution (available via www.languagetool.org)")
        sys.exit()
    arg_pos = 1
    detailed_results_hash = None
    brief_output = False
    while (arg_pos < num_args) and (args[arg_pos][0] == "-"):
        debug_print("args[%d]: %s" % (arg_pos, args[arg_pos]), 3)
        if (args[arg_pos] == "-"):
            # note: - is used to avoid usage statement with file input from stdin
            pass
        elif (args[arg_pos] == "--brief"):
            brief_output = True
        elif (args[arg_pos] == "--full"):
            brief_output = False
        elif (args[arg_pos] == "--score"):
            detailed_results_hash = {}
        elif (args[arg_pos] == "--text"):
            arg_pos += 1
            # Run grammar checker over sentence from command line
            grammar_issues = check_text_grammar(args[arg_pos], brief=brief_output, results_hash=detailed_results_hash)
            if detailed_results_hash:
                ## OLD: print("score: %s: synopsis: %s" % (detailed_results_hash['score'], detailed_results_hash['synopsis']))
                print(detailed_results_hash['report'])
            else:
                print(grammar_issues)
            sys.exit()
        else:
            print_stderr("Error: unexpected argument '%s'" % args[arg_pos])
            sys.exit()
        arg_pos += 1
    file = args[arg_pos]

    # Run grammar checker over sentences in file
    grammar_issues = check_file_grammar(file, brief=brief_output, results_hash=detailed_results_hash)
    if detailed_results_hash:
        ## OLD: print("score: %s: synopsis: %s" % (detailed_results_hash['score'], detailed_results_hash['synopsis']))
        print(detailed_results_hash['report'])
    else:
        print(grammar_issues)

    # Cleanup
    debug_print("stop %s: %s" % (__file__, debug_timestamp()), 3)

#------------------------------------------------------------------------
# Standalone processing

if __name__ == '__main__':
    main()
