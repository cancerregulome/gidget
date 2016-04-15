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
import time

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
        print " not enough data! ", len(zA), minCount
        return (0.)

    (rho, pValue) = scipy.stats.spearmanr(zA, mA)

    # print "Spearman:\t%.2f\t%g\n" % ( rho, pValue )

    return (rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) != 6):
            print " Usage : %s <input tsv file> <output tsv file> <dThresh> <minCount> <corrThresh> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        tsvFile = sys.argv[1]
        outFile = sys.argv[2]
        dThresh = int ( sys.argv[3] )
        minCount = int ( sys.argv[4] )
        corrThresh = float ( sys.argv[5] )

    print " "
    print " "
    print " ************** "
    print " in methCorr3 : ", dThresh, minCount, corrThresh
    print " ***************************************************************** "
    print ' (a) TIME ', time.asctime(time.localtime(time.time()))
    print " calling readTSV ... ", tsvFile
    tsvD = tsvIO.readTSV(tsvFile)
    tsvIO.lookAtDataD(tsvD)

    try:
        tsvRowLabels = tsvD['rowLabels']
        tsvColLabels = tsvD['colLabels']
        tsvDataMatrix = tsvD['dataMatrix']
    except:
        print " no valid METH feature matrix "
        sys.exit(-1)

    numRow = len(tsvRowLabels)
    numCol = len(tsvColLabels)

    keepMeth = {}
    keepGexp = {}

    featType2 = "N:METH:"
    for featType1 in [ "N:GEXP:", "N:MIRN:" ]:

        print " "
        print ' (b) TIME ', time.asctime(time.localtime(time.time()))
        print " outer loop over %d features " % numRow, featType1, featType2

        nFound = 0
        nCorr = 0

        for iRow in range(numRow):

            ## here we need to dig out the GEXP or MIRN features ...
            gexpName = tsvRowLabels[iRow]
            if (not gexpName.startswith(featType1)):
                continue

            nFound += 1

            nameTokens = gexpName.split(':')
            # print nameTokens
            # N:GEXP:TP53:chr17:7565097:7590863:-:7157

            zChr = nameTokens[3]
            if (zChr == ""):
                continue

            zStart = int(nameTokens[4])
            zStop = int(nameTokens[5])

            zVec = tsvDataMatrix[iRow]

            ## if there isn't much data, we can skip this ...
            zV = squishOne(zVec)
            if (len(zV) < minCount):
                continue

            ## for each gene/miRNA we want to look for the largest positive
            ## OR negative correlation ...
            maxNeg = 0.
            maxPos = 0.
            jNeg = -1
            jPos = -1

            ## and now we loop over the features again to look at each METH feature ...
            for jRow in range(numRow):

                methName = tsvRowLabels[jRow]
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
                print " %6d  %6d  comparing <%s> and <%s> " % (iRow, jRow, gexpName, methName)
                # print mPos, zStart, zStop
                # print dStart, dStop, dThresh

                mVec = tsvDataMatrix[jRow]

                nCorr += 1
                rho = computeRho(zVec, mVec, minCount)
                print "Spearman:\t%.2f\t%6d\n" % (rho, dMin)

                if (rho < maxNeg):
                    maxNeg = rho
                    jNeg = jRow

                if (rho > maxPos):
                    maxPos = rho
                    jPos = jRow

            # now we have tested this gene against all nearby methylation probes
            if (jNeg >= 0):
                if (maxNeg <= -corrThresh):
                    keepMeth[jNeg] = 1
                    keepGexp[iRow] = 1
                    print " (b) keeping Spearman rho \t %.3f (%d) " % ( maxNeg, jNeg )
                    
            if (jPos >= 0):
                if (maxPos >= corrThresh):
                    keepMeth[jPos] = 1
                    keepGexp[iRow] = 1
                    print " (c) keeping Spearman rho \t %.3f (%d) " % ( maxPos, jPos )

    if ( nFound==0  or  nCorr==0 ):
        print " WARNING ??? no features found for correlation ??? "

    print ' (c) TIME ', time.asctime(time.localtime(time.time()))

    # and at this point we have tested all genes!!!
    print " length of keepMeth dictionary : ", len(keepMeth)
    print " length of keepGexp dictionary : ", len(keepGexp)
    print " original number of rows in input TSV file : ", numRow

    rmRowList = []

    for jRow in range(numRow):
        if (tsvRowLabels[jRow].lower().find("platform") < 0 ):
            if (jRow not in keepMeth.keys()):
                if (jRow not in keepGexp.keys()):
                    rmRowList += [jRow]
    print " number of rows to be removed : ", len(rmRowList)

    tsvD = tsvIO.filter_dataMatrix(tsvD, rmRowList, [])

    print ' (d) TIME ', time.asctime(time.localtime(time.time()))

    sortRowFlag = 0
    sortColFlag = 0

    tsvIO.writeTSV_dataMatrix(tsvD, sortRowFlag, sortColFlag, outFile)

    print ' (e) TIME ', time.asctime(time.localtime(time.time()))
    print " DONE !!! "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
