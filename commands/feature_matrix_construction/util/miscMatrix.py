#!/usr/bin/env python

import commands
import math
import numpy
import sys

import miscIO
import miscMath

#------------------------------------------------------------------------------


def getHistogramInfo(xMin, xMax, xSigma):

    # first we estimate the # of bins so that there are approximately
    # 5 bins for each standard deviation ...
    try:
        numBins = int(5. * (xMax - xMin) / xSigma)
    except:
        if ((xMax - xMin) <= abs(xMax / 1000000.)):
            numBins = 1
        else:
            print " fatal error in getHistogramInfo ... ", xMin, xMax, xSigma
            sys.exit(-1)

    if (numBins > 1):
        deltaX = (xMax - xMin) / float(numBins - 1)
    else:
        xMinHist = xMin
        xMaxHist = xMax
        deltaX = 0.
        numBins = 1
        return (xMinHist, xMaxHist, deltaX, numBins)

    # then we adjust them so that we have "round" numbers ...
    logDeltaX = math.log10(deltaX)
    intLog1 = int(logDeltaX) - 1
    dx1 = 10. ** intLog1

    idx1 = (int(deltaX / dx1))
    if (idx1 < 0):
        print ' how can this be ??? ', deltaX, dx1, idx1
        sys.exit(-1)

    if (idx1 <= 3):
        idx1 = 1
    elif (idx1 <= 7):
        idx1 = 5
    else:
        idx1 = 10

    dx1a = idx1 * dx1
    xMin1 = (int(xMin / dx1a) - 6) * dx1a
    xMax1 = (int(xMax / dx1a) + 6) * dx1a

    xMinHist = xMin1
    xMaxHist = xMax1

    deltaX = dx1a

    # HACK
    ## deltaX = 0.1

    numBins = (xMaxHist - xMinHist) / deltaX
    numBins = int(numBins) + 2
    if (numBins < 1):
        numBins = 1

    print ' histogram over : ', xMinHist, xMaxHist, deltaX, numBins
    return (xMinHist, xMaxHist, deltaX, numBins)

#------------------------------------------------------------------------------


def getHistogramInfo2(xMin, xMax, deltaX):

    # in this case we are *told* what deltaX should be ...
    numBins = int((xMax - xMin) / deltaX) + 2

    xMin1 = (int(xMin / deltaX) - 6) * deltaX
    xMax1 = (int(xMax / deltaX) + 6) * deltaX

    xMinHist = xMin1
    xMaxHist = xMax1
    numBins = (xMaxHist - xMinHist) / deltaX
    numBins = int(numBins) + 2
    if (numBins < 1):
        numBins = 1

    print ' histogram over : ', xMinHist, xMaxHist, deltaX, numBins
    return (xMinHist, xMaxHist, deltaX, numBins)

#------------------------------------------------------------------------------


def statsByCol(matrixFilename):

    (fh, reZip) = openInputFileForReading(matrixFilename)

    # if failed to open file, just return ...
    if (reZip < 0):
        return

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)

    tokenList = firstLine.split()
    numCols = len(tokenList)

    print ' <%s> : %d rows and %d columns ' % \
        (matrixFilename, numLines, numCols)

    minVals = [+99999999] * numCols
    maxVals = [-99999999] * numCols

    sum1 = [0] * numCols
    sum2 = [0] * numCols

    fh.seek(0)

    iRow = 0
    for inLine in fh:
        tokenList = inLine.split()
        if (len(tokenList) == numCols):
            for iCol in range(numCols):
                fVal = float(tokenList[iCol])
                if (fVal < minVals[iCol]):
                    minVals[iCol] = fVal
                if (fVal > maxVals[iCol]):
                    maxVals[iCol] = fVal
                sum1[iCol] += (fVal)
                sum2[iCol] += (fVal * fVal)
            iRow += 1
        else:
            # print ' skipping ... ', len(tokenList), tokenList
            true = 1

    fh.close()

    print ' --> got %d rows of data ... ' % iRow

    for iCol in range(numCols):
        mean1 = sum1[iCol] / float(iRow)
        mean2 = sum2[iCol] / float(iRow)
        sigma = math.sqrt(mean2 - (mean1 * mean1))
        print '         column #%3d : min=%16.8f  max=%16.8f   mean=%16.8f   sigma=%16.8f ' % \
            (iCol, minVals[iCol], maxVals[iCol], mean1, sigma)

#------------------------------------------------------------------------------


def xyCorr(matrixFilename, iX, iY, jStart=-1, jStop=-1, flipFlag=0):

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99)

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)

    tokenList = firstLine.split()
    numCols = len(tokenList)

    print ' <%s> : %d rows and %d columns ' % \
        (matrixFilename, numLines, numCols)

    if (iX >= numCols or iY >= numCols):
        print ' --> ERROR : iX=%d iY=%d ' % (iX, iY)
        return (-99)

    xCol = numpy.zeros(numLines)
    yCol = numpy.zeros(numLines)

    fh.seek(0)

    iRow = 0
    for inLine in fh:
        tokenList = inLine.split()
        if (len(tokenList) == numCols):
            xCol[iRow] = float(tokenList[iX])
            yCol[iRow] = float(tokenList[iY])
            iRow += 1
        else:
            # print ' skipping ... ', len(tokenList), tokenList
            true = 1

    fh.close()

    print ' --> got %d rows of data ... ' % iRow

    if (jStart >= 0 and jStop >= 0):
        print ' --> trimming to [%d:%d] ' % (jStart, jStop)
        xCol = xCol[jStart:jStop + 1]
        yCol = yCol[jStart:jStop + 1]

    if (flipFlag):
        print ' --> reversing one vector '
        lenY = len(yCol)
        tmpY = numpy.zeros(lenY)
        for kk in range(lenY):
            tmpY[kk] = yCol[lenY - 1 - kk]
        yCol = tmpY

    rhoXY = miscMath.PearsonCorr(xCol, yCol)
    print ' Pearson correlation : ', rhoXY

    (a, b, r) = miscMath.linear_regression(xCol, yCol)
    print ' Linear regression :   r2 = %f ' % r
    print '                       slope = %f ' % b
    print '                       offset = %f ' % a

#------------------------------------------------------------------------------


def zipFile(aFile):

    cmdString = "gzip -f %s" % aFile
    (status, output) = commands.getstatusoutput(cmdString)
    if (status != 0):
        print ' WARNING !!! failed to zip <%s> ' % aFile

#------------------------------------------------------------------------------


def openInputFileForReading(aFile):

    # print ' in openInputFileForReading ... <%s> ' % aFile

    if (aFile.endswith('.gz')):
        bFile = aFile[:-3]
        cmdString = "gunzip -f %s" % aFile
        print '     cmdString : <%s> ' % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output
        if (status != 0):
            print ' ERROR ??? failed to unzip <%s> ' % aFile
            try:
                fh = file(bFile)
                return (fh, 0)
            except:
                print ' ERROR ??? failed to open <%s> ' % bFile
        else:
            try:
                fh = file(bFile)
                return (fh, 1)
            except:
                print ' ERROR ??? failed to open <%s> ' % bFile

    else:
        fh = file(aFile)
        return (fh, 0)

    print ' ERROR in openInputFileForReading ... FAILED TO OPEN <%s> ' % aFile
    return (-1, -1)

    print ' ERROR ??? should not get here ??? '
    sys.exit(-1)

#------------------------------------------------------------------------------


def getOneColumn(matrixFilename, iX, nSkip=0):

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99)

    fhName = fh.name

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)
    numLines -= nSkip

    tokenList = firstLine.split()
    numCols = len(tokenList)

    # print ' <%s> : %d rows and %d columns ' % \
    ## 		 ( matrixFilename, numLines, numCols )

    if (iX >= numCols):
        print ' --> ERROR : iX=%d ' % (iX)
        return (-99)

    xCol = numpy.zeros(numLines)

    fh.seek(0)

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    iRow = 0
    for inLine in fh:
        tokenList = inLine.split()
        if (len(tokenList) == numCols and iRow < numLines):
            try:
                xCol[iRow] = float(tokenList[iX])
            except:
                xCol[iRow] = 0.
            iRow += 1
        else:
            print ' skipping ... ', len(tokenList), tokenList
            true = 1

    fh.close()

    if (reZip):
        zipFile(fhName)

    return (xCol)

#------------------------------------------------------------------------------


def getOneRow(matrixFilename, iY, nSkip=0):

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99)

    fhName = fh.name

    fh.seek(0)
    numLines = miscIO.num_lines(fh)
    if (iY >= numLines):
        print ' --> ERORR : iY=%d ' % (iY)
        return (-99)

    for ii in range(iY + 1):
        aLine = fh.readline()

    tokenList = aLine.split()
    numCols = len(tokenList)
    if (nSkip >= numCols):
        print ' --> ERROR : numCols=%d  nSkip=%d \n' % (numCols, nSkip)
        return (-99)

    xCol = numpy.zeros(numCols - nSkip)
    nGet = 0
    for ii in range(numCols - nSkip):
        try:
            xCol[ii] = float(tokenList[nSkip + ii])
            nGet += 1
        except:
            print ' skipping ... ', tokenList[nSkip + ii]
            true = 1

    fh.close()

    if (reZip):
        zipFile(fhName)

    return (xCol[:nGet])

#------------------------------------------------------------------------------


def getVectorNormSq(xCol):

    magSq = 0.
    absMag = 0.
    for ii in range(len(xCol)):
        absMag += (abs(xCol[ii]))
        magSq += (xCol[ii] * xCol[ii])

    print ' in getVectorNormSq : ', len(xCol), absMag, magSq

    return (magSq)

#------------------------------------------------------------------------------
# this is the version that takes a file ...


def oneDhist(matrixFilename, iX, deltaX=-1, xMin=-1, xMax=-1, nSkip=0, printFlag=1):

    print ' in oneDhist ... ', matrixFilename, iX, deltaX, xMin, xMax, nSkip, printFlag

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99)

    fhName = fh.name

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)
    numLines -= nSkip

    tokenList = firstLine.split()
    numCols = len(tokenList)

    print ' <%s> : %d rows and %d columns ' % \
        (matrixFilename, numLines, numCols)

    if (iX >= numCols):
        print ' --> ERROR : iX=%d ' % (iX)
        return (-99)

    xCol = numpy.zeros(numLines)

    fh.seek(0)

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    iRow = 0
    numErrSkip = 0
    for inLine in fh:
        tokenList = inLine.split('\t')
        if (len(tokenList) <= iX):
            print " ERROR ??? too few tokens ??? ", iX, len(tokenList)
            print tokenList
            numErrSkip += 1
            # sys.exit(-1)
        elif (len(tokenList) > iX and iRow < numLines):
            if (tokenList[iX] == "NaN"):
                tokenList[iX] = "NA"
            try:
                xCol[iRow] = float(tokenList[iX])
                # print iRow, min(xCol), max(xCol)
                iRow += 1
            except:
                if (1):
                    print ' invalid value ??? ', iX, tokenList, ' ... skipping ... '
                    numErrSkip += 1
                else:
                    print ' ERROR ??? ', iX
                    print tokenList
                    print tokenList[iX]
                    sys.exit(-1)
        else:
            print ' skipping ... ', len(tokenList), tokenList
            numErrSkip += 1

    fh.close()

    if (reZip):
        zipFile(fhName)

    numRows = iRow
    print ' --> got %d rows of data ... ' % numRows
    print '     skipped %d rows of data ... ' % numErrSkip

    if (numErrSkip > 0):
        xCol = xCol[:numRows]

    # now that we have the vector of data we need to decide how to set the
    # range and bin size for the histogram ...
    if (xMin == -1):
        xMin = xCol.min()
    if (xMax == -1):
        xMax = xCol.max()
    xMean = xCol.mean()
    xSigma = xCol.std()
    xMagSq = getVectorNormSq(xCol)
    print '         N=%12d, min=%16.8f, max=%16.8f, mean=%16.8f and sigma=%16.8f :' % (len(xCol), xCol.min(), xCol.max(), xMean, xSigma)
    print '         norm squared = %16.8f ' % xMagSq

    if (deltaX < 0):
        print ' calling getHistogramInfo ... ', xMin, xMax, xSigma
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo(xMin, xMax, xSigma)
        print xMinHist, xMaxHist, deltaX, numBins
    else:
        print ' calling getHistogramInfo2 ... ', xMin, xMax, deltaX
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo2(xMin, xMax, deltaX)
        print xMinHist, xMaxHist, deltaX, numBins

    # and now we can build the histogram of counts ...
    numTooSmall = 0
    numTooBig = 0
    xHist = [0] * numBins
    for iRow in range(numRows):
        xVal = xCol[iRow]
        if (xVal < xMinHist):
            numTooSmall += 1
        elif (xVal > xMaxHist):
            numTooBig += 1
        else:
            iBin = int((xVal - xMinHist) / deltaX + 0.0001)
            try:
                xHist[iBin] += 1
            except:
                print ' ERROR ??? : ', iRow, xVal, iBin, xHist[iBin]
                sys.exit(-1)

    print " "
    print " numTooSmall : ", numTooSmall
    print " numTooBig : ", numTooBig
    print " "

    # and now we can print it out as counts, a PDF, and a CDF ...

    # first we'd like to find the first and last non-zero bins ...
    iStartBin = 0
    while (xHist[iStartBin] == 0):
        iStartBin += 1

    iStopBin = numBins - 1
    while (xHist[iStopBin] == 0):
        iStopBin -= 1

    # and now we can print it out ...
    cumCount = numTooSmall
    modeVal = -1.
    medianVal = 1.
    qqErr = 0.
    for iBin in range(iStartBin, iStopBin + 1):

        if (1):

            cumCount += xHist[iBin]
            cumFrac = float(cumCount) / float(numRows)
            curFrac = float(xHist[iBin]) / float(numRows)
            xVal = float(iBin) * deltaX + xMinHist

            if (cumFrac > 0. and cumFrac < 1.):
                xNormInv = miscMath.normInv(cumFrac, xMean, xSigma)
            else:
                xNormInv = -999999999.

            if (printFlag):
                if (xNormInv != -999999999.):
                    if (xHist[iBin] > 0):
                        print ' %5d  %14.10f  %12d  %14.10f  %14.10f  %14.10f ' % \
                            (iBin, xVal, xHist[iBin],
                             curFrac, cumFrac, xNormInv)
                    qqErr += (abs(xNormInv - xVal) * deltaX)
                else:
                    if (xHist[iBin] > 0):
                        print ' %5d  %14.10f  %12d  %14.10f  %14.10f ' % \
                            (iBin, xVal, xHist[iBin], curFrac, cumFrac)

            if (modeVal < curFrac):
                modeVal = curFrac
                modeBin = iBin
                modeX = xVal

            if (abs(cumFrac - 0.5) < medianVal):
                medianVal = abs(cumFrac - 0.5)
                medianBin = iBin
                medianX = xVal

    # print ' median at ', medianBin, medianX, medianVal
    # print ' mode at   ', modeBin, modeX, modeVal
    print ' integrated abs QQ error : ', qqErr

    # maybe it would also be interesting to compare this to a uniform
    # distribution ...
    xMinVal = float(iStartBin) * deltaX + xMinHist
    xMaxVal = float(iStopBin) * deltaX + xMinHist
    uHeight = 1. / float(iStopBin - iStartBin + 1)
    KLdist = 0.
    for iBin in range(iStartBin, iStopBin + 1):
        curFrac = float(xHist[iBin]) / float(numRows)
        if (uHeight < 1.e-9 and curFrac < 1.e-9):
            KLdist += 0.
        elif (curFrac < 1.e-9):
            # print " warning ... not sure what to do ... ", curFrac, uHeight
            doNothing = 1
        elif (uHeight < 1.e-9):
            # print " warning ... not sure what to do ... ", curFrac, uHeight
            doNothing = 1
        else:
            KLdist += curFrac * \
                math.log(curFrac / uHeight)  +  uHeight * \
                math.log(uHeight / curFrac)
    print ' symmetric KL distance to uniform distribution between %f and %f : %f ' % (xMinVal, xMaxVal, KLdist)

    return (xMinHist, xMaxHist, deltaX, numBins, xHist)

#------------------------------------------------------------------------------


def oneDhistFromVec(xCol, deltaX=-1, xMin=-1, xMax=-1, printFlag=1):

    print ' in oneDhistFromVec ... ', deltaX, xMin, xMax, printFlag

    # now that we have the vector of data we need to decide how to set the
    # range and bin size for the histogram ...
    if (xMin == -1):
        xMin = xCol.min()
    if (xMax == -1):
        xMax = xCol.max()
    xMean = xCol.mean()
    xSigma = xCol.std()
    xMagSq = getVectorNormSq(xCol)
    print '         min=%16.8f, max=%16.8f, mean=%16.8f and sigma=%16.8f :' % (xCol.min(), xCol.max(), xMean, xSigma)
    print '         norm squared = %16.8f ' % xMagSq

    if (deltaX < 0):
        print ' calling getHistogramInfo ... ', xMin, xMax, xSigma
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo(xMin, xMax, xSigma)
        print xMinHist, xMaxHist, deltaX, numBins
    else:
        print ' calling getHistogramInfo2 ... ', xMin, xMax, deltaX
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo2(xMin, xMax, deltaX)
        print xMinHist, xMaxHist, deltaX, numBins

    # and now we can build the histogram of counts ...
    xHist = [0] * numBins
    numRows = len(xCol)
    for iRow in range(numRows):
        xVal = xCol[iRow]
        try:
            iBin = int((xVal - xMinHist) / deltaX + 0.0001)
        except:
            if (numBins == 1):
                iBin = 0
            else:
                print " ERROR in oneDhistFromVec "
                sys.exit(-1)
        if (iBin >= 0 and iBin < numBins):
            xHist[iBin] += 1

    # and now we can print it out as counts, a PDF, and a CDF ...

    # first we'd like to find the first and last non-zero bins ...
    iStartBin = 0
    while (xHist[iStartBin] == 0):
        iStartBin += 1

    iStopBin = numBins - 1
    while (xHist[iStopBin] == 0):
        iStopBin -= 1

    # and now we can print it out ...
    cumCount = 0
    modeVal = -1.
    medianVal = 1.
    qqErr = 0.
    for iBin in range(iStartBin, iStopBin + 1):

        if (1):

            cumCount += xHist[iBin]
            cumFrac = float(cumCount) / float(numRows)
            curFrac = float(xHist[iBin]) / float(numRows)
            xVal = float(iBin) * deltaX + xMinHist

            if (cumFrac > 0. and cumFrac < 1.):
                xNormInv = miscMath.normInv(cumFrac, xMean, xSigma)
            else:
                xNormInv = -999999999.

            if (printFlag):
                if (xNormInv != -999999999.):
                    if (xHist[iBin] > 0):
                        print ' %5d  %14.10f  %12d  %14.10f  %14.10f  %14.10f ' % \
                            (iBin, xVal, xHist[iBin],
                             curFrac, cumFrac, xNormInv)
                    qqErr += (abs(xNormInv - xVal) * deltaX)
                else:
                    if (xHist[iBin] > 0):
                        print ' %5d  %14.10f  %12d  %14.10f  %14.10f ' % \
                            (iBin, xVal, xHist[iBin], curFrac, cumFrac)

            if (modeVal < curFrac):
                modeVal = curFrac
                modeBin = iBin
                modeX = xVal

            if (abs(cumFrac - 0.5) < medianVal):
                medianVal = abs(cumFrac - 0.5)
                medianBin = iBin
                medianX = xVal

    # print ' median at ', medianBin, medianX, medianVal
    # print ' mode at   ', modeBin, modeX, modeVal
    print ' integrated abs QQ error : ', qqErr

    return (xMinHist, xMaxHist, deltaX, numBins, xHist, cumCount, modeVal, modeBin, medianVal, medianBin)

#------------------------------------------------------------------------------


def oneDcondHist(matrixFilename, iX, bitVec, deltaX=-1, xMin=-1, xMax=-1, nSkip=0, printFlag=1):

    print ' in oneDcondHist ... ', matrixFilename, iX, deltaX, xMin, xMax, nSkip, printFlag
    print ' length of input bitVec : ', len(bitVec)

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99, -99, -99, -99, -99, -99)

    fhName = fh.name

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)
    numLines -= nSkip

    tokenList = firstLine.split()
    numCols = len(tokenList)

    print ' <%s> : %d rows and %d columns ' % \
        (matrixFilename, numLines, numCols)

    if (iX >= numCols):
        print ' --> ERROR : iX=%d ' % (iX)
        return (-99, -99, -99, -99, -99, -99)

    xCol = numpy.zeros(numLines)

    fh.seek(0)

    for iSkip in range(nSkip):
        skipLine = fh.readline()

    iRow = 0
    for inLine in fh:
        tokenList = inLine.split()
        if (len(tokenList) == numCols and iRow < numLines):
            try:
                xCol[iRow] = float(tokenList[iX])
            except:
                print ' ERROR ??? ', iX
                print tokenList
                print tokenList[iX]
                sys.exit(-1)
            iRow += 1
        else:
            print ' skipping ... ', len(tokenList), tokenList
            true = 1

    fh.close()

    if (reZip):
        zipFile(fhName)

    numRows = iRow
    print ' --> got %d rows of data ... ' % numRows

    # now that we have the vector of data we need to decide how to set the
    # range and bin size for the histogram ...
    if (xMin == -1):
        xMin = xCol.min()
    if (xMax == -1):
        xMax = xCol.max()
    xMean = xCol.mean()
    xSigma = xCol.std()
    print '         min=%16.8f, max=%16.8f, mean=%16.8f and sigma=%16.8f :' % (xCol.min(), xCol.max(), xMean, xSigma)

    if (deltaX < 0):
        print ' calling getHistogramInfo ... ', xMin, xMax, xSigma
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo(xMin, xMax, xSigma)
        print xMinHist, xMaxHist, deltaX, numBins
    else:
        print ' calling getHistogramInfo2 ... ', xMin, xMax, deltaX
        (xMinHist, xMaxHist, deltaX,
         numBins) = getHistogramInfo2(xMin, xMax, deltaX)
        print xMinHist, xMaxHist, deltaX, numBins

    # and now we can build the histogram of counts ...
    xHist0 = [0] * numBins
    xHist1 = [0] * numBins
    numRows0 = 0
    numRows1 = 0
    print numRows, len(bitVec), len(xCol)
    for iRow in range(numRows):
        # if ( iRow%1000 == 0 ): print iRow, xCol[iRow], bitVec[iRow]
        xVal = xCol[iRow]
        iBin = int((xVal - xMinHist) / deltaX + 0.0001)
        if (abs(bitVec[iRow]) < 0.00001):
            numRows0 += 1
            try:
                xHist0[iBin] += 1
            except:
                print ' ERROR ??? : ', iRow, xVal, iBin, xHist0[iBin]
        else:
            numRows1 += 1
            try:
                xHist1[iBin] += 1
            except:
                print ' ERROR ??? : ', iRow, xVal, iBin, xHist1[iBin]

    # and now we can print it out as counts, a PDF, and a CDF ...

    # first we'd like to find the first and last non-zero bins ...
    iStartBin = 0
    while (xHist0[iStartBin] == 0 and xHist1[iStartBin] == 0):
        iStartBin += 1

    iStopBin = numBins - 1
    while (xHist0[iStopBin] == 0 and xHist1[iStopBin] == 0):
        iStopBin -= 1

    # and now we can print it out ...
    cumCount0 = 0
    modeVal0 = -1.
    medianVal0 = 1.
    qqErr0 = 0.

    meanX0 = 0.
    meanSqX0 = 0.

    cumCount1 = 0
    modeVal1 = -1.
    medianVal1 = 1.
    qqErr1 = 0.

    meanX1 = 0.
    meanSqX1 = 0.

    for iBin in range(iStartBin, iStopBin + 1):

        if (1):

            xVal = float(iBin) * deltaX + xMinHist

            meanX0 += (float(xHist0[iBin]) * xVal / float(numRows0))
            meanX1 += (float(xHist1[iBin]) * xVal / float(numRows1))

            meanSqX0 += (float(xHist0[iBin]) * xVal * xVal / float(numRows0))
            meanSqX1 += (float(xHist1[iBin]) * xVal * xVal / float(numRows1))

            cumCount0 += xHist0[iBin]
            cumFrac0 = float(cumCount0) / float(numRows0)
            curFrac0 = float(xHist0[iBin]) / float(numRows0)

            cumCount1 += xHist1[iBin]
            cumFrac1 = float(cumCount1) / float(numRows1)
            curFrac1 = float(xHist1[iBin]) / float(numRows1)

            if (printFlag):

                print " ERROR ... this code needs to be fixed ... xMean and xSigma are not correct ... "
                sys.exit(-1)

                if (cumFrac0 > 0. and cumFrac0 < 1.):
                    xNormInv0 = miscMath.normInv(cumFrac0, xMean, xSigma)
                else:
                    xNormInv0 = -999999999.

                if (cumFrac1 > 0. and cumFrac1 < 1.):
                    xNormInv1 = miscMath.normInv(cumFrac1, xMean, xSigma)
                else:
                    xNormInv1 = -999999999.

                outLine = ' %5d  %14.8f ' % (iBin, xVal)
                outLine += ' %12d  %14.8f  %14.8f ' % (xHist0[iBin],
                                                       curFrac0, cumFrac0)
                outLine += ' %12d  %14.8f  %14.8f ' % (xHist1[iBin],
                                                       curFrac1, cumFrac1)
                if (xNormInv0 != -999999999.):
                    outLine += ' %14.8f ' % xNormInv0
                    qqErr0 += (abs(xNormInv0 - xVal) * deltaX)
                else:
                    outLine += '                '
                if (xNormInv1 != -999999999.):
                    outLine += ' %14.8f ' % xNormInv1
                    qqErr1 += (abs(xNormInv1 - xVal) * deltaX)
                else:
                    outLine += '                '
                print outLine

            if (modeVal0 < curFrac0):
                modeVal0 = curFrac0
                modeBin0 = iBin
                modeX0 = xVal

            if (abs(cumFrac0 - 0.5) < medianVal0):
                medianVal0 = abs(cumFrac0 - 0.5)
                medianBin0 = iBin
                medianX0 = xVal

            if (modeVal1 < curFrac1):
                modeVal1 = curFrac1
                modeBin1 = iBin
                modeX1 = xVal

            if (abs(cumFrac1 - 0.5) < medianVal1):
                medianVal1 = abs(cumFrac1 - 0.5)
                medianBin1 = iBin
                medianX1 = xVal

    sigmaX0 = math.sqrt(meanSqX0 - (meanX0 * meanX0))
    sigmaX1 = math.sqrt(meanSqX1 - (meanX1 * meanX1))

    print ' conditioned on bit = 0  %12d  %6.3f  %6.3f ' % (numRows0, meanX0, sigmaX0)
    print '     median at ', medianBin0, medianX0, medianVal0
    print '     mode at   ', modeBin0, modeX0, modeVal0
    print ' conditioned on bit = 1  %12d  %6.3f  %6.3f ' % (numRows1, meanX1, sigmaX1)
    print '     median at ', medianBin1, medianX1, medianVal1
    print '     mode at   ', modeBin1, modeX1, modeVal1
    # print ' integrated abs QQ error : ', qqErr0, qqErr1

    return (xMinHist, xMaxHist, deltaX, numBins, xHist0, xHist1)

#------------------------------------------------------------------------------


def twoDhist(matrixFilename, iX, iY,
             tdmFilename='',
             xMin='', xMax='', deltaX='',
             yMin='', yMax='', deltaY=''):

    (fh, reZip) = openInputFileForReading(matrixFilename)
    if (reZip < 0):
        return (-99)

    firstLine = fh.readline()

    fh.seek(0)
    numLines = miscIO.num_lines(fh)

    tokenList = firstLine.split()
    numCols = len(tokenList)

    print ' <%s> : %d rows and %d columns ' % \
        (matrixFilename, numLines, numCols)

    if (iX >= numCols or iY >= numCols):
        print ' --> ERROR : iX=%d  iY=%d ' % (iX, iY)
        return (-99)

    xCol = numpy.zeros(numLines)
    yCol = numpy.zeros(numLines)

    fh.seek(0)

    iRow = 0
    for inLine in fh:
        tokenList = inLine.split()
        if (len(tokenList) == numCols):
            xCol[iRow] = float(tokenList[iX])
            yCol[iRow] = float(tokenList[iY])
            iRow += 1
        else:
            # print ' skipping ... ', len(tokenList), tokenList
            true = 1

    fh.close()

    numRows = iRow
    print ' --> got %d rows of data ... ' % numRows

    if (xMin == ''):
        xMin = xCol.min()
    if (xMax == ''):
        xMax = xCol.max()
    xMean = xCol.mean()
    xSigma = xCol.std()
    print '         ', xMin, xMax, xMean, xSigma

    if (yMin == ''):
        yMin = yCol.min()
    if (yMax == ''):
        yMax = yCol.max()
    yMean = yCol.mean()
    ySigma = yCol.std()
    print '         ', yMin, yMax, yMean, ySigma

    if (deltaX == ''):
        (xMinHist, xMaxHist, deltaX,
         numXbins) = getHistogramInfo(xMin, xMax, xSigma)
    else:
        numXbins = int((xMax - xMin) / deltaX + 2)
        xMinHist = xMin
        xMaxHist = xMax
    print numXbins, deltaX

    if (deltaY == ''):
        (yMinHist, yMaxHist, deltaY,
         numYbins) = getHistogramInfo(yMin, yMax, ySigma)
    else:
        numYbins = int((yMax - yMin) / deltaY + 2)
        yMinHist = yMin
        yMaxHist = yMax
    print numYbins, deltaY

    # check to see if the bins should be square ... if so, we'll take the smaller
    # of the two dimensions ...
    if (0):
        if (min(deltaX, deltaY) / max(deltaX, deltaY) > 0.85):
            if (deltaX > deltaY):
                deltaX = deltaY
                numXbins = int(xMaxHist - xMinHist) / deltaX + 2
            elif (deltaX < deltaY):
                deltaY = deltaX
                numYbins = int(yMaxHist - yMinHist) / deltaY + 2
            print ' --> adjusted to square bins ... ', deltaX, numXbins, numYbins

    xyHist = [0] * numXbins
    for ii in range(numXbins):
        xyHist[ii] = [0] * numYbins

    for iRow in range(numRows):
        xVal = xCol[iRow]
        yVal = yCol[iRow]
        iX = int((xVal - xMinHist) / deltaX + 0.0001)
        iY = int((yVal - yMinHist) / deltaY + 0.0001)
        if (iX >= 0 and iY >= 0 and iX < numXbins and iY < numYbins):
            xyHist[iX][iY] += 1

    # find the one bin with the most counts ...
    modeVal = -1.
    for iX in range(numXbins):
        xVal = float(iX) * deltaX + xMinHist
        for iY in range(numYbins):
            yVal = float(iY) * deltaY + yMinHist
            if (xyHist[iX][iY] > modeVal):
                modeVal = xyHist[iX][iY]
                modeX = xVal
                modeY = yVal
    print ' mode at   ', modeX, modeY, modeVal

    # what is the median count value ?
    allBins = numpy.zeros(numXbins * numYbins)
    kk = 0
    for iX in range(numXbins):
        for iY in range(numYbins):
            allBins[kk] = xyHist[iX][iY]
            kk += 1
    allBins.sort()
    numBins = len(allBins)
    p50 = allBins[int(0.50 * numBins)]
    p90 = allBins[int(0.90 * numBins)]
    print allBins[0], allBins[-1], p50, p90

    if (tdmFilename != ''):
        fhPng = file(tdmFilename, 'w')

        outLine = 'CORNER'
        for iX in range(numXbins):
            outLine += '\t%d' % iX
        outLine += '\n'
        fhPng.write(outLine)

        for iY in range(numYbins - 1, -1, -1):
            outLine = '%d' % iY
            for iX in range(numXbins):
                outLine += '\t%d' % xyHist[iX][iY]
            outLine += '\n'
            fhPng.write(outLine)

        fhPng.close()

#------------------------------------------------------------------------------
