# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addExpFracOnFeature(dataD, fType):

    print " "
    print " in addExpFracOnFeature ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    # the custom features are assumed to be derived in some way
    # from existing features ...
    exFNames = [fType]
    numExF = len(exFNames)
    numExF2 = [0] * numExF
    exFRows = [-1] * numExF

    for iRow in range(numRow):
        for iEx in range(numExF):
            if (exFNames[iEx] in rowLabels[iRow]):
                # print iRow, rowLabels[iRow], iEx, exFNames[iEx]
                if (numExF2[iEx] == 0):
                    exFRows[iEx] = [iRow]
                    numExF2[iEx] = 1
                else:
                    exFRows[iEx] += [iRow]
                    numExF2[iEx] += 1
                    # print " already found a match ??? ", exFNames[iEx], rowLabels[exFRows[iEx]]
                    # sys.exit(-1)

    if (min(numExF2) == 0):
        print " WARNING !!! failed to find one of the existing features ??? ", numExF2, exFNames
        print " --> no additional features will be added "
        return (dataD)

    print " feature names and rows: "
    print " A ", exFNames
    print " B ", exFRows[0][:5], exFRows[0][-5:]
    print " C ", numExF2

    # maybe do a first pass just to see what the sizes of the gene
    # expression values tend to be?
    print " pre-allocating ... ", numExF2[0], numCol, (numExF2[0] * numCol)
    tmpVec = [0] * (numExF2[0] * numCol)
    numVal = 0
    for iEx in range(numExF):
        for iCol in range(numCol):
            for jEx in range(numExF2[0]):
                curVal = dataMatrix[exFRows[iEx][jEx]][iCol]
                if (curVal != NA_VALUE):
                    tmpVec[numVal] = curVal
                    numVal += 1
    print numVal
    tmpVec = tmpVec[:numVal]
    tmpVec.sort()

    numNew = 9
    threshVals = [0] * numNew
    newNames = [0] * numNew
    for iDec in range(numNew):
        jDec = int(float(iDec + 1) * float(numVal) / float(numNew + 1))
        threshVals[iDec] = tmpVec[jDec]
        if (fType == "N:GEXP:"):
            newNames[iDec] = "N:SAMP:gexpFracON_%d:::::" % (iDec + 1)
        elif (fType == "N:MIRN:"):
            newNames[iDec] = "N:SAMP:mirnFracON_%d:::::" % (iDec + 1)
        else:
            newNames[iDec] = "N:SAMP:fracON_%d:::::" % (iDec + 1)
        print iDec, newNames[iDec], threshVals[iDec]

    # now we loop over the sets of input features ...
    # note that in this particular case, numExF should be 1
    if (numExF != 1):
        print " invalid use of this code ??? "
        sys.exit(-1)

    for iEx in range(numExF):

        # get the *existing* data vectors that we are going to use ...
        dataVecs = [0] * numExF2[iEx]
        for jEx in range(numExF2[iEx]):
            dataVecs[jEx] = dataMatrix[exFRows[iEx][jEx]]
            # print dataVecs[jEx][:10], dataVecs[jEx][-10:]

        # double-check that none of these features are already in the matrix
        # ...
        for iNew in range(numNew):
            if (newNames[iNew] in rowLabels):
                print " ERROR ??? duplicate feature name already exists ??? ", newNames[iNew]
                sys.exit(-1)

        newVecs = [0] * numNew
        for iNew in range(numNew):
            newVecs[iNew] = [NA_VALUE] * numCol

            if (1):

                minON = 2.
                maxON = 0.
                numNA = 0

                tVec = []
                print " looping over %d columns " % numCol
                for iCol in range(numCol):
                    numON = 0
                    numOFF = 0
                    print "     col=%d   looping over %d input features " % (iCol, numExF2[0])
                    for jEx in range(numExF2[0]):
                        curVal = dataVecs[jEx][iCol]
                        if (curVal != NA_VALUE):
                            if (curVal > threshVals[iNew]):
                                numON += 1
                            else:
                                numOFF += 1
                    if ((numON + numOFF) > 0):
                        fracON = float(numON) / float(numON + numOFF)
                        newVecs[iNew][iCol] = fracON
                        if (minON > fracON):
                            minON = fracON
                        if (maxON < fracON):
                            maxON = fracON
                        print " QQQ ", fracON
                    else:
                        numNA += 1

                print iNew
                print newVecs[iNew][:10]
                print minON, maxON, numNA
                print " "

    # now we have the new data ...
    print " "
    print " adding these new features: ", newNames
    print " "
    newRowLabels = rowLabels + newNames
    print len(rowLabels), len(newRowLabels)

    newMatrix = dataMatrix + newVecs
    print len(dataMatrix), len(newMatrix)

    newD = {}
    newD['rowLabels'] = newRowLabels
    newD['colLabels'] = colLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = newMatrix

    return (newD)

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
    print " Running : %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print " "
    print " "

    # now read in the input feature matrix ...
    dataD = tsvIO.readTSV(inFile)

    # add new custom features ...
    dataD = addExpFracOnFeature(dataD, "N:GEXP:")
    dataD = addExpFracOnFeature(dataD, "N:MIRN:")

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
