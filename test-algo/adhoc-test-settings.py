from django.conf import settings

import sys

if settings.DEBUG:
    # Do something
    print >> sys.stderr, "Debugging"
else:
    print >> sys.stderr, "Not Debugging"

# TODO: nltk.data.path = [settings.NLTKDATAPATH]
# print "nltk.data.path = %s" % str(nltk.data.path)
nltk_data_path = [settings.NLTKDATAPATH]
print "nltk_data_path = %s" % str(nltk_data_path)
