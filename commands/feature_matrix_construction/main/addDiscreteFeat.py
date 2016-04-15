# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import addIndicators
import miscIO
import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getFeatureList(featFile):

    featDict = {}

    try:
        fh = file(featFile)
        for aLine in fh:
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            if (len(tokenList) == 2):
                featDict[tokenList[0]] = int(tokenList[1])
            else:
                featDict[tokenList[0]] = 4
    except:
        doNothing = 1

    return (featDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addDiscreteFeature(dataD, featName, numLevels):

    print " "
    print " in addDiscreteFeature ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    # find the specific feature ...
    kFind = []
    for iRow in range(numRow):
        if (rowLabels[iRow].find(featName) >= 0):
            kFind += [iRow]

    if (len(kFind) == 0):
        print " ERROR ... did not find this feature <%s> " % featName
        print " "
        return (dataD)
    elif (len(kFind) > 1):
        print " ERROR ... found too many similar features "
        print featName
        print kFind
        for kk in kFind:
            print rowLabels[kk]
        print " "
        return (dataD)

    iRow = kFind[0]
    origRowLabel = rowLabels[iRow]
    if (not origRowLabel.startswith("N:")):
        print " ERROR ... does not make sense to discretized a non-continuous feature "
        print origRowLabel
        print " "
        return (dataD)

    print " --> discretizing this feature : <%s> " % origRowLabel

    curVec = []
    for iCol in range(numCol):
        curVal = dataMatrix[iRow][iCol]
        if (curVal != NA_VALUE):
            curVec += [curVal]

    curVec.sort()
    # print curVec[:5]
    # print curVec[-5:]
    # print " "
    nPos = len(curVec)
    # print " "
    # print nPos

    numCat = numLevels

    print " "
    print " category thresholds, counts, etc: "
    threshVals = [0] * numCat
    for iCat in range(numCat - 1):
        iPos = int(float(nPos) * float(iCat + 1) / float(numCat) - 0.5)
        if (iPos < 0):
            iPos = 0
        if (iPos >= nPos):
            iPos = nPos - 1
        threshVals[iCat] = curVec[iPos]
        print iCat, iPos, threshVals[iCat]
    threshVals[-1] = curVec[-1] + 0.1
    print numCat - 1, nPos, threshVals[-1]

    # in case we have a bunch of identical values, make sure that the
    # threshold values are all unique and then use that unique list (uTV)
    uTV = []
    for iTV in threshVals:
        if (iTV not in uTV):
            uTV += [iTV]
    print " --> uTV : ", uTV

    catCounts = {}

    newVec = ["NA"] * numCol
    for iCol in range(numCol):
        curVal = dataMatrix[iRow][iCol]
        if (curVal != NA_VALUE):
            iVal = 0
            while (uTV[iVal] < curVal):
                iVal += 1
            newVec[iCol] = "C%d" % iVal

            try:
                catCounts[newVec[iCol]] += 1
            except:
                catCounts[newVec[iCol]] = 1

    print " "
    print " catCounts : ", len(catCounts), catCounts
    print " "

    if (origRowLabel[-1] == ":"):
        newName = "C:" + origRowLabel[2:] + "cat"
    else:
        newName = "C:" + origRowLabel[2:] + "_cat"

    # now we have the new data ...
    print " "
    print " adding new feature: ", newName
    print " "
    newRowLabels = rowLabels + [newName]
    print len(rowLabels), len(newRowLabels)

    newMatrix = dataMatrix + [newVec]
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
        if (len(sys.argv) == 4):
            inFile = sys.argv[1]
            outFile = sys.argv[2]
            featFile = sys.argv[3]
        else:
            print " "
            print " Usage: %s <input TSV file> <output TSV file> <featList file> "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    print " "
    print " Running : %s %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])
    print " "
    print " "

    # first read in the feature names list
    featDict = getFeatureList(featFile)

    # now read in the input feature matrix ...
    dataD = tsvIO.readTSV(inFile)

    if (len(dataD) == 0):
        print " in addDiscreteFeat ... no input data ... nothing to do here ... "

    # loop over specified features and add a discretized version of each one
    for aFeat in featDict.keys():

        numLevels = featDict[aFeat]

        print " "
        print " "
        print " **************************************** "
        print aFeat, numLevels
        print " **************************************** "
        print " "

        dataD = addDiscreteFeature(dataD, aFeat, numLevels)

        rowLabels = dataD['rowLabels']
        tmpMatrix = dataD['dataMatrix']
        (rowLabels, tmpMatrix) = addIndicators.addIndicators4oneFeat(
            rowLabels[-1], rowLabels, tmpMatrix)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
