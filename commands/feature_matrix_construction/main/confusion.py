# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscIO
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def printConfusionMatrix(aLine, bLine):

    # --------------------------------------------------------------
    # first, figure out what the values are for these two features,
    # then sort them, but make sure that "NA" is at the end of the
    # sorted list

    aVals = []
    bVals = []

    aTokens = aLine.split('\t')
    aName = aTokens[0]
    aTokens = aTokens[1:]
    for aTok in aTokens:
        if (aTok not in aVals):
            aVals += [str(aTok)]

    bTokens = bLine.split('\t')
    bName = bTokens[0]
    bTokens = bTokens[1:]
    for bTok in bTokens:
        if (bTok not in bVals):
            bVals += [str(bTok)]

    aVals.sort()
    bVals.sort()

    if ("NA" in aVals):
        ii = aVals.index("NA")
        if (ii != (len(aVals) - 1)):
            aVals = aVals[:ii] + aVals[ii + 1:] + ["NA"]
            # print aVals

    if ("NA" in bVals):
        ii = bVals.index("NA")
        if (ii != (len(bVals) - 1)):
            bVals = bVals[:ii] + bVals[ii + 1:] + ["NA"]
            # print bVals

    # --------------------------------------------------------------
    # now print out the row and column details
    print " "
    print " rows in confusion matrix are    : ", aName, aVals
    print " columns in confusion matrix are : ", bName, bVals
    print " "

    # --------------------------------------------------------------
    # and then the table ... the row columns will be abbreviated
    # (if necessary) so that they line up with the integer counts
    outLine = "                  \t"
    dashLine = outLine
    for bTok in bVals:
        if (len(bTok) > 5):
            bShort = bTok[:5]
        else:
            bShort = bTok
            while (len(bShort) < 5):
                bShort = " " + bShort + " "
            bShort = bShort[:5]
        outLine += " " + bShort
        dashLine += "-"
        for ii in range(len(bShort)):
            dashLine += "-"
    print outLine
    print dashLine

    for aTok in aVals:
        outLine = "%16s :\t" % aTok
        for bTok in bVals:
            numAB = 0
            for ii in range(len(aTokens)):
                if (aTokens[ii] == aTok and bTokens[ii] == bTok):
                    numAB += 1
            outLine += " %4d " % numAB
        print outLine

    print " "
    print "-------------------------------------------------------------------"
    print " "

    # DONE

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 4):
        print ' Usage : %s <TSV filename> <feat1> <feat2> ' % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    inFilename = sys.argv[1]
    feat1 = sys.argv[2]
    feat2 = sys.argv[3]

    fh = file(inFilename)
    list1 = []
    list2 = []

    numLines = 0
    for aLine in fh:
        numLines += 1
        if (numLines == 1):
            continue
        if (aLine.startswith("N:")):
            continue
        # if ( aLine.find(":I(") >= 0 ): continue
        aLine = aLine.strip()
        if (aLine.find(feat1) >= 0):
            list1 += [aLine]
        if (aLine.find(feat2) >= 0):
            list2 += [aLine]
    fh.close()

    if (len(list1) < 1):
        print " no features found matching <%s> ??? " % feat1
        sys.exit(-1)

    if (len(list2) < 1):
        print " no features found matching <%s> ??? " % feat2
        sys.exit(-1)

    print " "
    print " %4d matches to <%s> " % (len(list1), feat1)
    print " %4d matches to <%s> " % (len(list2), feat2)
    print " "

    for aLine in list1:
        for bLine in list2:
            printConfusionMatrix(aLine, bLine)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
