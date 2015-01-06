# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import miscMath
import miscMatrix
import miscTCGA
import plotMatrix
import tsvIO

import math
import numpy
import scipy.stats
import sys

# this flag defines whether we adjust the MAD, IQR, IDR, whichever
# statistic based on the overall threshold or not ...
# --> should be set to 0 or 1
strictStat = 1
## strictStat = 0

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def squishOne(aVec):
    aT = []
    for ii in range(len(aVec)):
        if (aVec[ii] == NA_VALUE):
            doNothing = 1
        else:
            aT += [aVec[ii]]

    aV = numpy.array(aT)

    return (aV)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def squishTwo(aVec, bVec):

    if (len(aVec) != len(bVec)):
        print " FATAL ERROR in squishTwo ", len(aVec), len(bVec)
        sys.exit(-1)

    aT = []
    bT = []
    for ii in range(len(aVec)):
        if (aVec[ii] == NA_VALUE or bVec[ii] == NA_VALUE):
            doNothing = 1
        else:
            aT += [aVec[ii]]
            bT += [bVec[ii]]

    aV = numpy.array(aT)
    bV = numpy.array(bT)

    return (aV, bV)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def computeRho(zVec, mVec, minCount):

    print " in computeRho ... "

    # print zVec
    # print mVec
    print len(zVec)

    (zA, mA) = squishTwo(zVec, mVec)

    # print zA
    # print mA

    if (len(zA) < minCount):
        print " not enough data ! "
        return (0.)

    (rho, pValue) = scipy.stats.spearmanr(zA, mA)

    # print "Spearman:\t%.2f\t%g\n" % ( rho, pValue )

    return (rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) != 2):
            print " Usage : %s <input tsv file> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        tsvFile = sys.argv[1]

    print " "
    print " "
    print " ************** "
    print " in methCorr2 : "
    print " ***************************************************************** "
    print " calling readTSV ... ", tsvFile
    methD = tsvIO.readTSV(tsvFile)
    tsvIO.lookAtDataD(methD)

    try:
        methRowLabels = methD['rowLabels']
        methColLabels = methD['colLabels']
        methDataMatrix = methD['dataMatrix']
    except:
        print " no valid METH feature matrix "
        sys.exit(-1)

    numMethRow = len(methRowLabels)
    numMethCol = len(methColLabels)

    dThresh = 10000
    minCount = 30
    featType1 = "N:GEXP:"
    featType2 = "N:METH:"

    print " "
    print " outer loop over %d features " % numMethRow
    for iRow in range(numMethRow):

        featName = methRowLabels[iRow]
        if (not featName.startswith(featType1)):
            continue

        nameTokens = featName.split(':')
        print nameTokens
        # N:GEXP:TP53:chr17:7565097:7590863:-:7157

        zChr = nameTokens[3]
        if (zChr == ""):
            continue

        zStart = int(nameTokens[4])
        zStop = int(nameTokens[5])

        zVec = methDataMatrix[iRow]
        zV = squishOne(zVec)
        if (len(zV) < minCount):
            continue

        for jRow in range(numMethRow):

            methName = methRowLabels[jRow]
            if (not methName.startswith(featType2)):
                continue

            methTokens = methName.split(':')

            mChr = methTokens[3]
            if (mChr != zChr):
                continue

            mPos = int(methTokens[4])
            dStart = abs(mPos - zStart)
            dStop = abs(mPos - zStop)
            dMin = min(dStart, dStop)
            if (dMin > dThresh):
                continue

            print " "
            print " "
            print " %6d  %6d  comparing <%s> and <%s> " % (iRow, jRow, featName, methName)
            # print mPos, zStart, zStop
            # print dStart, dStop, dThresh

            mVec = methDataMatrix[jRow]

            rho = computeRho(zVec, mVec, minCount)
            print "Spearman:\t%.2f\t%6d\n" % (rho, dMin)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
