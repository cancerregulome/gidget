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

    # print " in computeRho ... "
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

    # print rho, pValue

    return (rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) != 6):
            print " Usage : %s <input meth file> <input other file> <otherType> <outputFile> <corrThresh> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        methFile = sys.argv[1]
        othrFile = sys.argv[2]
        othrType = sys.argv[3]
        outFile = sys.argv[4]
        corrThresh = abs(float(sys.argv[5]))
        if (not othrType.startswith("N:")):
            othrType = "N:" + othrType

    ## corrThresh = 0.40
    ## corrThresh = 0.20

    print " "
    print " "
    print " ************* "
    print " in methCorr : "
    print " ***************************************************************** "
    print " calling readTSV ... ", methFile
    methD = tsvIO.readTSV(methFile)
    tsvIO.lookAtDataD(methD)

    print " calling readTSV ... ", othrFile
    othrD = tsvIO.readTSV(othrFile)
    tsvIO.lookAtDataD(othrD)

    try:
        methRowLabels = methD['rowLabels']
        methColLabels = methD['colLabels']
        methDataMatrix = methD['dataMatrix']
    except:
        print " no valid METH feature matrix "
        sys.exit(-1)

    numMethRow = len(methRowLabels)
    numMethCol = len(methColLabels)

    try:
        othrRowLabels = othrD['rowLabels']
        othrColLabels = othrD['colLabels']
        othrDataMatrix = othrD['dataMatrix']
    except:
        print " no valid METH feature matrix "
        sys.exit(-1)

    numOthrRow = len(othrRowLabels)
    numOthrCol = len(othrColLabels)

    dThresh = 10000
    minCount = 30

    keepMeth = {}
    keepOthr = {}

    print " "
    print " outer loop over %d features " % numOthrRow
    for iRow in range(numOthrRow):

        featName = othrRowLabels[iRow]
        if (not featName.startswith(othrType)):
            continue

        nameTokens = featName.split(':')

        # print nameTokens
        # N:GEXP:TP53:chr17:7565097:7590863:-:7157

        zChr = nameTokens[3]
        if (zChr == ""):
            continue

        zStart = int(nameTokens[4])
        zStop = int(nameTokens[5])

        zVec = othrDataMatrix[iRow]
        zV = squishOne(zVec)
        if (len(zV) < minCount):
            continue

        maxNeg = 0.
        maxPos = 0.
        jNeg = -1
        jPos = -1

        for jRow in range(numMethRow):

            methName = methRowLabels[jRow]
            if (not methName.startswith("N:METH:")):
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

            print " %6d  %6d   comparing <%s> and <%s> (%d) " % (iRow, jRow, featName, methName, dMin)
            # print mPos, zStart, zStop
            # print dStart, dStop, dThresh

            mVec = methDataMatrix[jRow]

            rho = computeRho(zVec, mVec, minCount)
            print " (a) Spearman rho \t %.3f " % rho

            if (0):
                if (abs(rho) >= 0.20):
                    keepOthr[iRow] = 1
                    keepMeth[jRow] = 1
                    print " Spearman : %.3f    %6d %6d " % (rho, len(keepOthr), len(keepMeth))

            if (1):
                if (rho < maxNeg):
                    maxNeg = rho
                    jNeg = jRow
                if (rho > maxPos):
                    maxPos = rho
                    jPos = jRow

        # now we have tested this gene against all nearby methylation probes
        # ...
        if (jNeg >= 0):
            if (maxNeg <= -corrThresh):
                keepMeth[jNeg] = 1
                print " (b) keeping Spearman rho \t %.3f " % maxNeg
        if (jPos >= 0):
            if (maxPos >= corrThresh):
                keepMeth[jPos] = 1
                print " (c) keeping Spearman rho \t %.3f " % maxPos

    # and at this point we have tested all genes!!!
    print " length of keepMeth dictionary : ", len(keepMeth)
    print " original number of rows in methylation file : ", numMethRow

    rmMethRowList = []

    for jRow in range(numMethRow):
        if (jRow not in keepMeth.keys()):
            rmMethRowList += [jRow]
    print " number of rows to be removed : ", len(rmMethRowList)

    methD = tsvIO.filter_dataMatrix(methD, rmMethRowList, [])

    sortRowFlag = 0
    sortColFlag = 0

    tsvIO.writeTSV_dataMatrix(methD, sortRowFlag, sortColFlag, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
