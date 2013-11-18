# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import numpy
import sys

import miscMath

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def makePlotMatrix(xMin, xMax, xDel,
                   yMin, yMax, yDel):

    numX = int(((xMax - xMin) / xDel) + 1.49)
    numY = int(((yMax - yMin) / yDel) + 1.49)

    # we make a matrix of empty lists ...
    pMat = [0] * numX
    for iX in range(numX):
        pMat[iX] = [0] * numY
        for iY in range(numY):
            pMat[iX][iY] = 0

    pTuple = (pMat, xMin, xMax, xDel, yMin, yMax, yDel)

    return (pTuple)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addSampleToPlotMatrix(pTuple, x, y, z):

    pMat = pTuple[0]
    xMin = pTuple[1]
    xMax = pTuple[2]
    xDel = pTuple[3]
    yMin = pTuple[4]
    yMax = pTuple[5]
    yDel = pTuple[6]

    # just for the x value, we're going to clip it but keep it ...
    if (x > xMax):
        x = xMax

    iX = int((x - xMin) / xDel + 0.4999)
    iY = int((y - yMin) / yDel + 0.4999)
    try:
        pMat[iX][iY] += z
    except:
        print " ERROR in addSampleToPlotMatrix ... "
        print x, xMin, xMax, xDel, iX, len(pMat)
        print y, yMin, yMax, yDel, iY, len(pMat[0])
        # sys.exit(-1)

    pTuple = (pMat, xMin, xMax, xDel, yMin, yMax, yDel)

    return (pTuple)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def writePlotMatrix(pTuple, plotFilename, maxVal, drawGridFlag=0):

    print " "
    print " in writePlotMatrix ... "

    pMat = pTuple[0]
    xMin = pTuple[1]
    xMax = pTuple[2]
    xDel = pTuple[3]
    yMin = pTuple[4]
    yMax = pTuple[5]
    yDel = pTuple[6]

    numX = len(pMat)
    numY = len(pMat[0])
    print " matrix size : %d x %d " % (numX, numY)

    numNZ = 0
    numTot = 0

    maxAbsX = -1
    maxAbsY = -1
    maxZ = -1

    for iX in range(numX):
        xVal = xMin + float(iX) * xDel
        for iY in range(numY):
            yVal = yMin + float(iY) * yDel
            if (pMat[iX][iY] > 0):

                absX = abs(xVal)
                if (absX > maxAbsX):
                    maxAbsX = absX

                absY = abs(yVal)
                if (absY > maxAbsY):
                    maxAbsY = absY

                numNZ += 1
                numPts = pMat[iX][iY]
                if (maxZ < numPts):
                    maxZ = numPts
                numTot += numPts
                ## tmpZ = numpy.zeros(numPts)
                # print " %8.3f %8.3f %5d " % ( xVal, yVal, numPts )

    print " "
    print " number of non-empty bins : %d (%d counts total) " % (numNZ, numTot)
    if (numNZ == 0):
        print " --> empty matrix ... skipping this one ... "
        return
    if (numNZ < 10):
        print " --> nearly empty matrix ... skipping this one ... ", numNZ, (numX * numY)
        return

    print " maximum absolute values : %.3f and %.3f " % (maxAbsX, maxAbsY)
    if (maxAbsX < 0.5):
        print " --> only very low importance values ... skipping this one ... "
        return
    if (maxAbsY < 0.2):
        print " --> only very low correlation values ... skipping this one ... "
        return

    print " maximum counts in a single bin : ", maxZ

    print " "
    print " "

    # find the maximum extent of non-zero bins
    iXmin = -1
    for iX in range(numX):
        for iY in range(numY):
            try:
                if (pMat[iX][iY] > 0):
                    if (iXmin == -1):
                        iXmin = iX
            except:
                jj = 0
    iXmax = -1
    for iX in range(numX - 1, -1, -1):
        for iY in range(numY):
            try:
                if (pMat[iX][iY] > 0):
                    if (iXmax == -1):
                        iXmax = iX
            except:
                jj = 0
    print iXmin, iXmax

    if (0):
        iYmin = -1
        for iY in range(numY):
            for iX in range(numX):
                try:
                    if (pMat[iX][iY] > 0):
                        if (iYmin == -1):
                            iYmin = iY
                except:
                    jj = 0
        iYmax = -1
        for iY in range(numY - 1, -1, -1):
            for iX in range(numX):
                try:
                    if (pMat[iX][iY] > 0):
                        if (iYmax == -1):
                            iYmax = iY
                except:
                    jj = 0
    else:
        iYmin = 0
        iYmax = numY - 1
    print iYmin, iYmax

    iXmin = max(0, iXmin - 5)
    iXmax = min(numX - 1, iXmax + 5)
    iYmin = max(0, iYmin - 5)
    iYmax = min(numY - 1, iYmax + 5)

    print ' final extents : ', iXmin, iXmax, iYmin, iYmax

    plot_xMin = (iXmin) * xDel + xMin
    plot_xMax = (iXmax) * xDel + xMin
    plot_yMin = (iYmin) * yDel + yMin
    plot_yMax = (iYmax) * yDel + yMin
    print '                 ', plot_xMin, plot_xMax, plot_yMin, plot_yMax

    iYskip = int(iYmax - iYmin) / 10

    if (1):

        maxCount = -1
        print ' --> opening output file : ', plotFilename
        fh = file(plotFilename, 'w')
        aLine = "CORNER"

        # for iX in range(numX):
        for iX in range(iXmin, iXmax + 1):
            xVal = xMin + float(iX) * xDel
            if (iX % 2 == 0):
                aLine += "\t%.2f" % xVal
            else:
                aLine += "\t  "
        fh.write("%s\n" % aLine)

        # the very first line should be a "grid" line ...
        if (drawGridFlag):
            print "         note : drawing top-most grid line ... "
            aLine = "  "
            for iX in range(iXmin, iXmax + 1):
                aLine += "\t-1"
            fh.write("%s\n" % aLine)

        # count up the number of data rows that have been "drawn" ...
        # ( note that we will "draw" y=0 twice, once up above the y=0 grid-line, and once below )
        numDrawn = 0

        # we start in the top-half ...
        halfFlag = +1

        # for iY in range(numY-1,-1,-1):
        for iY in range(iYmax, iYmin - 1, -1):

            yVal = yMin + float(iY) * yDel
            if (iY % 2 == 0):
                aLine = "%.2f" % yVal
            else:
                aLine = "  "
            # for iX in range(numX):
            for iX in range(iXmin, iXmax + 1):
                numPts = pMat[iX][iY]
                if (numPts > 0):
                    if (numPts > maxVal):
                        aLine += "\t%d" % maxVal
                    else:
                        aLine += "\t%d" % numPts
                    if (maxCount < numPts):
                        maxCount = numPts
                else:
                    # what to do with '0' ? missing or real value ?
                    aLine += "\t"
                    ## aLine += "\t0"
            fh.write("%s\n" % aLine)
            numDrawn += 1

            # we may want to write out another "grid" line here ...
            if (1):

                # generally we do NOT draw a grid line ...
                drawGrid = 0

                # but we do, every iYskip lines
                if (drawGridFlag):
                    if ((numDrawn - 1) % iYskip == 0):
                        drawGrid = 1
                    # except in a few cases ...
                    if (iY == iYmax):
                        drawGrid = 0
                    elif (iY == 1):
                        drawGrid = 0
                    # and we need to draw a grid line after the very last line
                    if (iY == 0):
                        drawGrid = 1

                if (drawGrid):
                    print "         note : drawing grid line ... iY=%d yVal=%.2f iYskip=%d " % (iY, yVal, iYskip)
                    aLine = "  "
                    for iX in range(iXmin, iXmax + 1):
                        aLine += "\t-1"
                    fh.write("%s\n" % aLine)

            # if we have gotten to the half-way mark, after the grid-line, draw
            # another grid-line and then the y=0 data row one more time ...
            if (numDrawn == (iYmax - iYmin + 2) / 2):

                if (drawGridFlag):
                    print "         note : thicker grid-line ... "
                    aLine = "  "
                    for iX in range(iXmin, iXmax + 1):
                        aLine += "\t-1"
                    fh.write("%s\n" % aLine)

                if (0):
                    print "         note : re-writing out the y=0 data row ... ", iY, numDrawn, (iYmax - iYmin + 2) / 2
                    halfFlag = -1
                    if (iY % 2 == 0):
                        aLine = "%.2f" % yVal
                    else:
                        aLine = "  "
                    for iX in range(iXmin, iXmax + 1):
                        numPts = pMat[iX][iY]
                        if (numPts > 0):
                            if (numPts > maxVal):
                                aLine += "\t%d" % maxVal
                            else:
                                aLine += "\t%d" % int(numPts + 0.49999)
                            if (maxCount < numPts):
                                maxCount = numPts
                        else:
                            # what to do with '0' ? missing or real value ?
                            ## aLine += "\t"
                            aLine += "\t0"
                    fh.write("%s\n" % aLine)
                    numDrawn += 1

        fh.close()
        print "     --> maximum count in bin : ", maxCount


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def logTransform(pTuple):

    print " "
    print " in logTransform ... "

    pMat = pTuple[0]
    xMin = pTuple[1]
    xMax = pTuple[2]
    xDel = pTuple[3]
    yMin = pTuple[4]
    yMax = pTuple[5]
    yDel = pTuple[6]

    numX = len(pMat)
    numY = len(pMat[0])
    print " matrix size : %d x %d " % (numX, numY)

    for iX in range(numX):
        xVal = xMin + float(iX) * xDel
        for iY in range(numY):
            yVal = yMin + float(iY) * yDel
            zVal = pMat[iX][iY]
            if (zVal > 0):
                zVal = miscMath.log2(zVal) + 1
                pMat[iX][iY] = zVal

    pTuple = (pMat, xMin, xMax, xDel, yMin, yMax, yDel)

    return (pTuple)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
