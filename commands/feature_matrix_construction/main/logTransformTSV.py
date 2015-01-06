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


def logTransform(dataD, featTypes):

    print " "
    print " ************************************************************* "
    print " ************************************************************* "
    print " "
    print " in logTransform ... "

    # check that the input feature matrix looks ok ...
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in logTransform ??? bad data ??? "
        return (dataD)

    # now we need to actually loop over the data ...

    dMat = dataD['dataMatrix']
    numLog = 0
    numNA = 0

    for iR in range(numRow):

        featName = dataD['rowLabels'][iR]
        featTokens = featName.split(':')

        logFlag = 0
        if (featTokens[0] == "N"):
            if (featTokens[1] in featTypes):
                logFlag = 1

        if (not logFlag):
            continue

        print " transforming ", featName

        for iC in range(numCol):
            if (dMat[iR][iC] == "NA"):
                doNothing = 1
            elif (dMat[iR][iC] == NA_VALUE):
                doNothing = 1
            else:
                dataVal = dMat[iR][iC]
                try:
                    logVal = math.log((dataVal + 1), 2)
                    dMat[iR][iC] = logVal
                    numLog += 1
                except:
                    dMat[iR][iC] = NA_VALUE
                    numNA += 1

    dataD['dataMatrix'] = dMat

    print " "
    print " --> finished with logTransform ... ", numLog, numNA
    print " "

    return (dataD)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) >= 4):
            inFile = sys.argv[1]
            outFile = sys.argv[2]
            featTypes = sys.argv[3:]
        else:
            print " "
            print " Usage: %s <input TSV file> <output TSV file> <featType1> [featType2] [featType3] ... "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    print " "
    print " Running : %s  %s  %s  " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print "           ", featTypes
    print " "

    # read in the input feature matrix first, just in case there
    # actually isn't one yet available ...
    testD = tsvIO.readTSV(inFile)
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
    except:
        print " --> invalid / missing input feature matrix "
        sys.exit(-1)

    newD = logTransform(testD, featTypes)

    # and finally write it out ...
    tsvIO.writeTSV_dataMatrix(newD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
