# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscMath
import miscMatrix
import miscTCGA
import plotMatrix
import tsvIO

import math
import numpy
import sys

# this flag defines whether we adjust the MAD, IQR, IDR, whichever
# statistic based on the overall threshold or not ...
# --> should be set to 0 or 1
strictStat = 1
## strictStat = 0

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    methodList = ["MAD", "IQR", "IDR", "ITR", "NZC", "DUMMY"]

    if (1):
        if (len(sys.argv) < 4 or len(sys.argv) > 5):
            print " Usage : %s <input file> <output file> <top fraction/count> [method(MAD,IQR,IDR,ITR,NZC)] " % sys.argv[0]
            print "         NOTE: if the 3rd parameter (the top fraction/count) is between 0 and 1, "
            print "               it is assumed to be a fraction, and if it is greater than 10, "
            print "               it is assumed to be a count; also the default method is IDR ) "
            print " "
            print " New options: if the 3rd parameter is negative, and the method is NZC, then the "
            print " absolute value of the numeric parameter is assumed to be the minimun NZC threshold to use "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        inFile = sys.argv[1]
        outFile = sys.argv[2]
        topFrac = float(sys.argv[3])
        topCount = -1

        if (abs(topFrac) > 1.5):
            if (topFrac > 0):
                topCount = int(topFrac + 0.4)
            elif (topFrac < 0):
                topCount = int(topFrac - 0.4)
            topFrac = -1
        elif (topFrac < 0.01 or topFrac > 1.00):
            print " ERROR ??? is the top fraction value correct ??? ", topFrac
            sys.exit(-1)

        if (len(sys.argv) == 5):
            method = sys.argv[4]
            method = method.upper()
            if (method not in methodList):
                print " ERROR ... invalid method ??? <%s> " % (method)
                print "           options are MAD, IQR, IDR, and ITR "
                sys.exit(-1)
        else:
            method = "MAD"

        print " topCount=%f, topFrac=%f, method=%s " % (topCount, topFrac, method)

        if (topCount == -99 and topFrac == -1 and method == "NZC"):
            forceThresh = 1
            print " disabling this ... not sure what this was for and whether it is still behaving as might be expected ... "
            sys.exit(-1)
        else:
            forceThresh = 0

    print " "
    print " "
    print " *************** "
    print " in highVarTSV : "
    print " ***************************************************************** "
    print " calling readTSV ... ", inFile
    testD = tsvIO.readTSV(inFile)
    tsvIO.lookAtDataD(testD)

    try:
        rowLabels = testD['rowLabels']
        colLabels = testD['colLabels']
        dataMatrix = testD['dataMatrix']
    except:
        print " no valid feature matrix "
        sys.exit(-1)

    numRow = len(rowLabels)
    numCol = len(colLabels)

    # print dataMatrix[-1]

    # let's just see what the overall range of values is ...
    # ( note that we are only looking at floating point values ... )
    minVal = NA_VALUE
    maxVal = NA_VALUE
    for iRow in range(numRow):
        for iCol in range(numCol):
            try:
                curVal = float(dataMatrix[iRow][iCol])
                if (curVal == NA_VALUE):
                    continue
                if (minVal == NA_VALUE):
                    minVal = curVal
                if (maxVal == NA_VALUE):
                    maxVal = curVal
                if (curVal < minVal):
                    minVal = curVal
                if (curVal > maxVal):
                    maxVal = curVal
            except:
                doNothing = 1
    print " range of values : ", minVal, maxVal

    # now let's compute a vector of values, one for each row
    numVec = numpy.zeros(numRow)

    medVec = numpy.zeros(numRow)
    qtrVec = numpy.zeros(numRow)
    decVec = numpy.zeros(numRow)
    tweVec = numpy.zeros(numRow)

    madVec = numpy.zeros(numRow)
    iqrVec = numpy.zeros(numRow)
    idrVec = numpy.zeros(numRow)
    itrVec = numpy.zeros(numRow)

    # for binary variables, we also just want to count up zero vs non-zero
    nzcVec = numpy.zeros(numRow)

    numSkip = 0

    for iRow in range(numRow):

        tmpV = numpy.zeros(numCol)
        ii = 0
        for iCol in range(numCol):
            try:
                curVal = float(dataMatrix[iRow][iCol])
                if (curVal != NA_VALUE):
                    try:
                        tmpV[ii] = curVal
                    except:
                        print iRow, ii, iCol, dataMatrix[iRow][iCol]
                        sys.exit(-1)
                    ii += 1
            except:
                doNothing = 1

        # print " iRow=%d  ii=%d " % ( iRow, ii )
        # HACK ... arbitrarily requiring at least 21 data samples to proceed
        # ...
        if (ii < 21):
            # print " --> iRow=%d does not have any (or enough) data (%d)
            # non-NA samples ??? " % ( iRow, ii )
            numSkip += 1
            continue
        tmpV = tmpV[:ii]
        numVec[iRow] = ii
        (madVec[iRow], medVec[iRow]) = miscMath.computeMAD(tmpV)
        (iqrVec[iRow], qtrVec[iRow]) = miscMath.computeIQR(tmpV)
        (idrVec[iRow], decVec[iRow]) = miscMath.computeIDR(tmpV)
        (itrVec[iRow], tweVec[iRow]) = miscMath.computeITR(tmpV)

        for jj in range(len(tmpV)):
            if (tmpV[jj] != 0):
                nzcVec[iRow] += 1

        if (0):
            if (madVec[iRow] > 0.35 and madVec[iRow] < 0.55):
                print " cluster of higher MAD values %7.3f %s " % (madVec[iRow], rowLabels[iRow])

    print " "
    print " number of features skipped because of insufficient data : ", numSkip

    # and take a look at the histogram of MAD values
    print " "
    print " histogram of counts : "
    miscMatrix.oneDhistFromVec(numVec)

    print " "
    print " histogram of median values : "
    miscMatrix.oneDhistFromVec(medVec)

    print " "
    print " histogram of 75% ile values : "
    miscMatrix.oneDhistFromVec(qtrVec)

    print " "
    print " histogram of 90% ile values : "
    miscMatrix.oneDhistFromVec(decVec)

    print " "
    print " histogram of 95% ile values : "
    miscMatrix.oneDhistFromVec(tweVec)

    print " "
    print " histogram of MAD values : "
    miscMatrix.oneDhistFromVec(madVec)

    print " "
    print " histogram of IQR values : "
    miscMatrix.oneDhistFromVec(iqrVec)

    print " "
    print " histogram of IDR values : "
    miscMatrix.oneDhistFromVec(idrVec)

    print " "
    print " histogram of ITR values : "
    miscMatrix.oneDhistFromVec(itrVec)

    print " "
    print " histogram of NZC values : "
    miscMatrix.oneDhistFromVec(nzcVec)

    if (method == "DUMMY"):
        sys.exit(-1)

    if (0):

        # let's make a 2d histogram matrix for plotting ...
        if (1):
            # these values are good for methylation data ...
            xMin = 0.
            xMax = 1.
            xDel = 0.01
            yMin = 0.
            yMax = 0.4
            yDel = 0.004
        if (0):
            # these values are good for gene expression log-ratios ...
            xMin = -10.
            xMax = 10.
            xDel = 0.2
            yMin = 0.
            yMax = 4.
            yDel = 0.04
        if (0):
            # these values are good for CNV segments ...
            xMin = -0.5
            xMax = 1.0
            xDel = 0.01
            yMin = 0.
            yMax = 1.7
            yDel = 0.01

        a2dHist = plotMatrix.makePlotMatrix(
            xMin, xMax, xDel, yMin, yMax, yDel)
        for ii in range(len(medVec)):
            a2dHist = plotMatrix.addSampleToPlotMatrix(
                a2dHist, medVec[ii], madVec[ii], 1)
        a2dHist = plotMatrix.logTransform(a2dHist)
        plotMatrix.writePlotMatrix(a2dHist, "testPlotMatrix.tsv", 999)

    # now we want to figure out what the threshold should be ...
    tmpVec = numpy.zeros(numRow)
    for iRow in range(numRow):
        if (strictStat):
            if (method == "MAD"):
                tmpVec[iRow] = madVec[iRow]
            if (method == "IQR"):
                tmpVec[iRow] = iqrVec[iRow]
            if (method == "IDR"):
                tmpVec[iRow] = idrVec[iRow]
            if (method == "ITR"):
                tmpVec[iRow] = tweVec[iRow]
            if (method == "NZC"):
                tmpVec[iRow] = nzcVec[iRow]
        else:
            # doing it this way also penalizes the lowly-expressed genes ...
            # with the second term knocked down a bit so that it doesn't
            # dominated ...
            if (method == "MAD"):
                tmpVec[iRow] = madVec[iRow] + medVec[iRow] / 6.
            if (method == "IQR"):
                tmpVec[iRow] = iqrVec[iRow] + qtrVec[iRow] / 2.
            if (method == "IDR"):
                tmpVec[iRow] = idrVec[iRow] + decVec[iRow] / 1.
            if (method == "ITR"):
                tmpVec[iRow] = itrVec[iRow] + tweVec[iRow] / 1.
            if (method == "NZC"):
                tmpVec[iRow] = nzcVec[iRow]

    tmpVec.sort()
    print ' lower tail : ', tmpVec[:5]
    print ' upper tail : ', tmpVec[-5:]

    # make sure that 'topCount', if being used, is not "too big" ...
    # THIS WAS NOT DOING WHAT I EXPECTED ... changing SMR 09/10
    if (0):
        if (topFrac < 0):
            if (topCount < 0):
                topCount = len(tmpVec) + topCount
                print " --> reset topCount to ", topCount
            elif (topCount > len(tmpVec)):
                topCount = len(tmpVec)
                print " --> reset topCount to ", topCount
    else:
        if (topFrac < 0):
            if (topCount < 0):
                print " --> NOT resetting topCount ... leaving at ", topCount
            elif (topCount > len(tmpVec)):
                topCount = len(tmpVec)
                print " --> reset topCount to ", topCount

    # tmpVec is now sorted so that the low values come first, the high values last ...
    # find the index of the position above which we have the desired 'topFrac'
    # ( or the 'topCount' )
    if (topFrac > 0.):
        iFrac = int((1. - topFrac) * (len(tmpVec) - numSkip)) + numSkip
        if (iFrac > 1):
            iFrac -= 1
        if (iFrac < 0):
            iFrac = 0
        if (iFrac > (len(tmpVec) - 1)):
            iFrac = len(tmpVec) - 1
        try:
            print " topFrac : ", topFrac, iFrac, numSkip, len(tmpVec), tmpVec[iFrac]
        except:
            print " ERROR in topFrac ??? ", topFrac, iFrac, numSkip, len(tmpVec)
    else:
        print tmpVec[:10]
        print tmpVec[-10:]
        if (topCount > 0):
            iFrac = len(tmpVec) - topCount
        else:
            iFrac = 0
            print "     --> looking for first value that is at least %d ... " % (abs(topCount))
            while (tmpVec[iFrac] < abs(topCount)):
                iFrac += 1
        print " topCounts : ", topCount, iFrac, numSkip, len(tmpVec), tmpVec[iFrac]

    # grab the threshold value that that position corresponds to
    threshVal = tmpVec[iFrac]
    jFrac = iFrac

    # Hijack ...
    if (forceThresh):
        print numCol
        threshVal = int(math.sqrt(numCol) / 3)
        if (threshVal < 3):
            threshVal = 3
        print " --> forcing threshVal to %d " % threshVal
        jFrac = 0
        print tmpVec[:5]
        print tmpVec[-5:]

    # now, walk forward as long as the threshold does not change, and reset
    # the position
    while (tmpVec[jFrac] < threshVal):
        jFrac += 1
    threshVal = tmpVec[jFrac]

    # make sure that the threshold is never 0 for non-zero-counts
    if (method == "NZC"):
        if (threshVal == 0):
            threshVal = 1

    print " --> setting threshold on %s at %f (%d) " % (method, threshVal, jFrac)
    print tmpVec[jFrac - 3:jFrac + 4]

    # and now we can figure out which rows to remove ...
    rmRowList = []
    for iRow in range(numRow):

        # we will not filter out categorical features based on "high
        # variability"
        if (rowLabels[iRow].startswith("C:")):
            continue

        # and we won't filter out binary features unless the filter type is NZC
        if (method != "NZC"):
            if (rowLabels[iRow].startswith("B:")):
                continue

        # likewise, if the filter type is NZC, this will only apply to binary features
        if (method == "NZC"):
            ## actually, we are using this type of filtering on MIRN data ...
            if (not rowLabels[iRow].startswith("N:MIRN:")):
                if (not rowLabels[iRow].startswith("B:")):
                    continue

        # now start grabbing the test statistic ...
        if (method == "MAD"):
            if (strictStat):
                testVal = madVec[iRow]
            else:
                testVal = madVec[iRow] + medVec[iRow] / 6.
        elif (method == "IQR"):
            if (strictStat):
                testVal = iqrVec[iRow]
            else:
                testVal = iqrVec[iRow] + qtrVec[iRow] / 2.
        elif (method == "IDR"):
            if (strictStat):
                testVal = idrVec[iRow]
            else:
                testVal = idrVec[iRow] + decVec[iRow] / 1.
        elif (method == "ITR"):
            if (strictStat):
                testVal = itrVec[iRow]
            else:
                testVal = itrVec[iRow] + tweVec[iRow] / 1.
        elif (method == "NZC"):
            testVal = nzcVec[iRow]

        else:
            print " FATAL ERROR ??? invalid method ??? ", method
            sys.exit(-1)

        # and here is where we actually decide whether or not to remove this
        # feature
        if (testVal < threshVal):
            rmRowList += [iRow]
            print "     --> will remove row #%4d <%s> ( %f < %f ) " % (iRow, rowLabels[iRow], testVal, threshVal)

    print " --> removing %d rows from data matrix ... " % len(rmRowList)
    newD = tsvIO.filter_dataMatrix(testD, rmRowList, [])
    tsvIO.lookAtDataD(newD)

    print " "
    print " ready to write output file ... ", outFile
    tsvIO.writeTSV_dataMatrix(newD, 0, 0, outFile)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
