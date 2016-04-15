# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import numpy
import sys

# these are my local ones
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def setFeatBits(rowLabels, featPrefix, doesContain, notContain):

    numSet = 0

    numRow = len(rowLabels)
    bitVec = numpy.zeros(numRow, dtype=numpy.bool)
    for iR in range(numRow):
        if (featPrefix != ""):
            if (not rowLabels[iR].startswith(featPrefix)):
                continue
        if (doesContain != ""):
            if (rowLabels[iR].find(doesContain) < 0):
                continue
        if (notContain != ""):
            if (rowLabels[iR].find(notContain) >= 0):
                continue
        bitVec[iR] = 1
        numSet += 1

    print featPrefix, doesContain, notContain, numRow, numSet
    if (numSet == 0):
        print " numSet=0 ... this is probably a problem ... "
        # sys.exit(-1)

    return (bitVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def summaryMeth(dataD):

    print " "
    print " ************************************************************* "
    print " ************************************************************* "
    print " "
    print " in summaryMeth ... "

    # check that the input feature matrix looks ok ...
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in summaryMeth ??? bad data ??? "
        return (dataD)

    # next, we need to find all of the METH features
    print " --> assigning meth flags ... "
    isMeth = setFeatBits(rowLabels, "N:METH:", "", "")

    # we're going to compute some information for each column ...
    sumMeth = [0] * numCol
    sumVals = [0] * numCol

    # now we need to actually loop over the data ...
    dMat = dataD['dataMatrix']
    for iR in range(numRow):

        # if this is a methylation feature ...
        if (isMeth[iR]):

            dVec = []
            sVec = []
            for iCol in range(numCol):
                if ( dMat[iR][iCol] != NA_VALUE ):
                    dVec += [ dMat[iR][iCol] ]
                    sVec += [ dMat[iR][iCol] ]

            sVec.sort()
            print dVec[:10], dVec[-10:]
            print sVec[:10], sVec[-10:]

            for iCol in range(len(dVec)):
                jj = sVec.index ( dVec[iCol] )
                xj = float(jj)/float(len(dVec))
                sumMeth[iCol] += xj
                sumVals[iCol] += 1

    print " summary values obtained "
    newVec = [0] * numCol
    for iCol in range(numCol):
        if ( sumVals[iCol] > 0 ):
            xm = float(sumMeth[iCol]) / float(sumVals[iCol])
            print "%d\t%f\t%f\t%f" % ( iCol, sumMeth[iCol], sumVals[iCol], xm )
            newVec[iCol] = xm
        else:
            newVec[iCol] = NA_VALUE

    newName = "N:SAMP:methSummary:::::"
    newRowLabels = rowLabels + [ newName ]
    newMatrix = dMat + [ newVec ]

    dataD['rowLabels'] = newRowLabels
    dataD['dataMatrix'] = newMatrix

    print " "
    print " --> finished with summaryMeth ... "
    print " "

    return (dataD)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 3):
            inFile = sys.argv[1]
            outFile = sys.argv[2]
            do_summaryMeth = 1
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

    # we want to "check" for "deleted" METH probes
    if (do_summaryMeth):
        newD = summaryMeth(testD)
        ## tsvIO.writeTSV_dataMatrix ( newD, 0, 0, outFile )
        testD = newD

    # and finally write it out ...
    tsvIO.writeTSV_dataMatrix(testD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
