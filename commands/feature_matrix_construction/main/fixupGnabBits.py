# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def badFeatureName(featName):

    fName = featName.lower()
    if (fName.find("unknown") >= 0):
        return (1)

    if (fName[1] == '-'):
        if (len(fName) == 5):
            try:
                iDate = int(fName[0])
                print " Excel date gene ERROR !!! ", fName
                return (1)
            except:
                doNothing = 1

    if (fName[2] == '-'):
        if (len(fName) == 6):
            try:
                iDate = int(fName[:2])
                print " Excel date gene ERROR !!! ", fName
                return (1)
            except:
                doNothing = 1

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkFeatures(dataD):

    print " "
    print " in checkFeatures ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    rmRowList = []

    for iRow in range(numRow):
        featName = rowLabels[iRow]

        # watch out for "bad" feature names, eg 1-Dec or unknown
        if (badFeatureName(featName)):
            rmRowList += [iRow]
        continue

        uVals = []
        for iCol in range(numCol):
            if (dataMatrix[iRow][iCol] != "NA"):
                if (dataMatrix[iRow][iCol] != NA_VALUE):
                    if (dataMatrix[iRow][iCol] not in uVals):
                        uVals += [dataMatrix[iRow][iCol]]
        if (len(uVals) < 2):
            rmRowList += [iRow]
            # print " will remove row #%d <%s> " % ( iRow, featName ), uVals
        else:
            if (len(uVals) == 2):
                uVals.sort()
                if (featName[0] != "B"):
                    if (uVals == [0, 1]):
                        newName = "B" + featName[1:]
                        print " fixing feature name : <%s> --> <%s> " % (featName, newName), uVals
                        rowLabels[iRow] = newName

    dataD['rowLabels'] = rowLabels

    print " --> removing %d uniform features " % len(rmRowList)
    newD = tsvIO.filter_dataMatrix(dataD, rmRowList, [])

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
            sys.exit(-1)

    print " "
    print " Running : %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print " "
    print " "

    # now read in the input feature matrix ...
    dataD = tsvIO.readTSV(inFile)

    # and then make sure that all of the barcodes are at least tumor-level
    # barcodes
    dataD = checkFeatures(dataD)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
