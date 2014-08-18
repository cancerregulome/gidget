# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addCustomFeatures(dataD):

    print " "
    print " in addCustomFeatures ... "

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
    exFNames = ["N:GEXP:ESR1:", "N:GEXP:ERBB2:"]
    numExF = len(exFNames)
    exFRows = [-1] * numExF

    for iRow in range(numRow):
        for iEx in range(numExF):
            if (exFNames[iEx] in rowLabels[iRow]):
                print iRow, rowLabels[iRow], iEx, exFNames[iEx]
                if (exFRows[iEx] == -1):
                    exFRows[iEx] = iRow
                else:
                    print " already found a match ??? ", exFNames[iEx], rowLabels[exFRows[iEx]]
                    sys.exit(-1)

    if (-1 in exFRows):
        print " WARNING !!! failed to find one of the existing features ??? ", exFRows, exFNames
        print " --> no additional features will be added "
        return (dataD)

    print exFNames
    print exFRows

    # get the *existing* data vectors that we are going to use ...
    dataVecs = [0] * numExF
    for iEx in range(numExF):
        dataVecs[iEx] = dataMatrix[exFRows[iEx]]
        print dataVecs[iEx][:10], dataVecs[iEx][-10:]

    # now we want to create features that specify the ESR1 and ERBB2 levels as LOW, MED or HI
    # and also all possible combinations:
    # ESR1 LOW + ERBB2 LOW / ESR1 LOW + ERBB2 MED / ESR1 LOW + ERBB2 HI
    # ESR1 MED + ERBB2 LOW ... etc
    # so there are 9 combinations
    newNames = ["C:SAMP:ESR1_level:::::",
                "C:SAMP:ERBB2_level:::::",
                "B:SAMP:ESR1_low,ERBB2_low:::::",
                "B:SAMP:ESR1_low,ERBB2_hi:::::",
                "B:SAMP:ESR1_hi,ERBB2_low:::::",
                "B:SAMP:ESR1_hi,ERBB2_hi:::::",
                "C:SAMP:BLcallA:::::"]
    numNew = len(newNames)

    # double-check that none of these features are already in the matrix ...
    for iNew in range(numNew):
        if (newNames[iNew] in rowLabels):
            print " ERROR ??? duplicate feature name already exists ??? ", newNames[iNew]
            sys.exit(-1)

    newVecs = [0] * numNew
    for iNew in range(numNew):
        newVecs[iNew] = ["NA"] * numCol

        if (iNew == 0):
            # ESR1 level ...
            tVec = []
            for iCol in range(numCol):
                curVal = dataVecs[iNew][iCol]
                if (curVal != NA_VALUE):
                    tVec += [curVal]

            print tVec[:10]
            tVec.sort()
            print tVec[:10]
            tVal = 560

            numHi = 0
            numLo = 0
            for iCol in range(numCol):
                curVal = dataVecs[iNew][iCol]
                if (curVal != NA_VALUE):
                    if (curVal > tVal):
                        newVecs[iNew][iCol] = "HI"
                        numHi += 1
                    else:
                        newVecs[iNew][iCol] = "LO"
                        numLo += 1

            print " <%s>   numHi=%d    numLo=%d " % (newNames[iNew], numHi, numLo)
            print newVecs[iNew][:10]

        elif (iNew == 1):
            # ERBB2 level ...
            tVec = []
            for iCol in range(numCol):
                curVal = dataVecs[iNew][iCol]
                if (curVal != NA_VALUE):
                    tVec += [curVal]

            print tVec[:10]
            tVec.sort()
            print tVec[:10]
            tVal = 31000

            numHi = 0
            numLo = 0
            for iCol in range(numCol):
                curVal = dataVecs[iNew][iCol]
                if (curVal != NA_VALUE):
                    if (curVal > tVal):
                        newVecs[iNew][iCol] = "HI"
                        numHi += 1
                    else:
                        newVecs[iNew][iCol] = "LO"
                        numLo += 1

            print " <%s>   numHi=%d    numLo=%d " % (newNames[iNew], numHi, numLo)
            print newVecs[iNew][:10]

        elif (iNew >= 2 and iNew <= 5):
            # "B:SAMP:ESR1_low,ERBB2_low:::::"
            # "B:SAMP:ESR1_low,ERBB2_hi:::::"
            # "B:SAMP:ESR1_hi,ERBB2_low:::::"
            # "B:SAMP:ESR1_hi,ERBB2_hi:::::"
            for iCol in range(numCol):
                if (newVecs[0][iCol] == "NA" or newVecs[1][iCol] == "NA"):
                    doNothing = 1
                else:
                    newVecs[iNew][iCol] = 0
                    if (iNew == 2):
                        if (newVecs[0][iCol] == "LO" and newVecs[1][iCol] == "LO"):
                            newVecs[iNew][iCol] = 1
                    elif (iNew == 4):
                        if (newVecs[0][iCol] == "LO" and newVecs[1][iCol] == "HI"):
                            newVecs[iNew][iCol] = 1
                    elif (iNew == 4):
                        if (newVecs[0][iCol] == "HI" and newVecs[1][iCol] == "LO"):
                            newVecs[iNew][iCol] = 1
                    elif (iNew == 5):
                        if (newVecs[0][iCol] == "HI" and newVecs[1][iCol] == "HI"):
                            newVecs[iNew][iCol] = 1

            print newVecs[iNew][:10]

        elif (iNew == 6):
            for iCol in range(numCol):
                if (newVecs[0][iCol] == "NA" or newVecs[1][iCol] == "NA"):
                    doNothing = 1
                else:
                    if (newVecs[0][iCol] == "LO" and newVecs[1][iCol] == "LO"):
                        newVecs[iNew][iCol] = "basal"
                    if (newVecs[0][iCol] == "HI" and newVecs[1][iCol] == "LO"):
                        newVecs[iNew][iCol] = "luminal"
                    if (newVecs[1][iCol] == "HI"):
                        newVecs[iNew][iCol] = "her2"

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
    dataD = addCustomFeatures(dataD)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
