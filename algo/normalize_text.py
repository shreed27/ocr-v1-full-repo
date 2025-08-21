#! /usr/bin/python
# coding: UTF-8
#
# normalize_text.py: normalize text prior to text criqueing
#
# Sample input:
#    “How now, brown cow”
#
# Sample output:
#    "How now, brown cow"
#

#------------------------------------------------------------------------
# Library packages

from common import *
from text_critique import *

# OS support
import os
import sys

#------------------------------------------------------------------------
# Functions

def read_file(filename):
    """Read all of the text in FILENAME"""
    with open(filename, 'r') as f:
        text = f.read()
    debug_print("read_file(%s) => %s" % (filename, text), 6)
    return text

def main():
    """
    Main routine: parse arguments and perform normalization of file or text.
    Note: main() used to avoid conflicts with globals (e.g., if done at end of script).
    """
    # Init
    debug_print("start %s: %s" % (__file__, debug_timestamp()), 3)

    # Parse command-line, showing usage statement if no arguments given (or --help)
    args = sys.argv
    debug_print("argv = %s" % sys.argv, 3)
    num_args = len(args)
    if ((num_args == 1) or ((num_args > 1) and (args[1] == "--help"))):
        print_stderr("Usage: %s [--text text] [--help] file" % args[0])
        print_stderr("")
        print_stderr("Notes:")
        print_stderr(" - set LANGUAGE_TOOL_HOME environment variable to directory for LanguageTool distribution (available via www.languagetool.org)")
        sys.exit()
    arg_pos = 1
    while (arg_pos < num_args) and (args[arg_pos][0] == "-"):
        debug_print("args[%d]: %s" % (arg_pos, args[arg_pos]), 3)
        if (args[arg_pos] == "-"):
            # note: - is used to avoid usage statement with file input from stdin
            pass
        elif (args[arg_pos] == "--text"):
            arg_pos += 1
            # Normalize text from command line
            print("%s" % normalize(args[arg_pos]))
            sys.exit()
        else:
            print_stderr("Error: unexpected argument '%s'" % args[arg_pos])
            sys.exit()
        arg_pos += 1
    file = args[arg_pos]

    # Normalize text file
    print("%s" % normalize(read_file(file)))

    # Cleanup
    debug_print("stop %s: %s" % (__file__, debug_timestamp()), 3)

#------------------------------------------------------------------------
# Standalone processing

if __name__ == '__main__':
    main()
