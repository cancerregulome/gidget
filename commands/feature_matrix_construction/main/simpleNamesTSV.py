# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import math
import numpy
import sys

# these are my local ones
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 3):
            inFile = sys.argv[1]
            outFile = sys.argv[2]
        else:
            print " "
            print " Usage: %s <input TSV file> <output TSV file> "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    print " "
    print " Running : %s  %s  %s  " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print " "

    # read in the input feature matrix first, just in case there
    # actually isn't one yet available ...
    testD = tsvIO.readTSV(inFile)
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
    except:
        print " --> invalid / missing input feature matrix "
        sys.exit(-1)

    # and write it back out ...
    sortColFlag = 1     # sort the sample barcodes
    sortRowFlag = 0     # do NOT sort the feature names
    simpleNamesFlag = 1 # and write out 'simple' names

    tsvIO.writeTSV_dataMatrix ( testD, sortRowFlag, sortColFlag, \
                                outFile, [], [], simpleNamesFlag )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
