# Settings for testing algorithm code
NLTKDATAPATH = "c:/Program-Misc/python/nltk-2.0.1rc1/nltk_data"

# Debugging stuff
if __debug__:
    import sys
    from common import *
    debug_print("syspath: " + str(sys.path), level=3)
