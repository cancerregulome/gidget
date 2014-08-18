# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def dupClinInfo(dataD):

    print " "
    print " in dupClinInfo ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    # outer loop is over all of the rows/features ...

    print " "
    print " starting loop over %d feature names ... " % numRow

    for iRow in range(numRow):
        curLabel = rowLabels[iRow]
        curType = curLabel[2:6]
        if (curType != "CLIN"):
            continue

        for iCol in range(numCol):
            curSample = colLabels[iCol]
            if (len(curSample) < 15):
                print " ERROR in hackTSV.py ... sample ID should be longer !!! ", curSample
                sys.exit(-1)
            try:
                tumorType = int(curSample[13:15])
            except:
                print " ERROR in hackTSV.py ... sample ID should have an integer tumorType ", curSample

            if (dataMatrix[iRow][iCol] != NA_VALUE):
                if (dataMatrix[iRow][iCol] != "NA"):
                    for jCol in range(numCol):
                        if (jCol == iCol):
                            continue
                        newSample = colLabels[jCol]

                        if (len(curSample) < 15):
                            print " ERROR in hackTSV.py ... sample ID should be longer !!! ", curSample
                            sys.exit(-1)
                        try:
                            tumorType = int(curSample[13:15])
                        except:
                            print " ERROR in hackTSV.py ... sample ID should have an integer tumorType ", curSample

                        if (curSample[:12] == newSample[:12]):
                            if (dataMatrix[iRow][jCol] == NA_VALUE or dataMatrix[iRow][jCol] == "NA"):
                                # print " copying ", dataMatrix[iRow][iCol],
                                # curLabel, curSample, newSample
                                dataMatrix[iRow][jCol] = dataMatrix[iRow][iCol]

    return (dataD)

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

    # first we want to copy all CLIN features across multiple columns
    # if there are multiple samples for a particular patient ...
    dataD = dupClinInfo(dataD)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
