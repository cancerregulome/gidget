# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addSampleType(dataD):

    print " "
    print " in addSampleType ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    zRow = -1
    for iRow in range(numRow):
        if (rowLabels[iRow].find("sampleType") >= 0):
            print " ERROR in addSampleType ... this matrix already seems to have this feature ", rowLabels[iRow]
            print "     --> make sure that it is current and up to date ... "
            zRow = iRow

    if (zRow < 0):
        numRow += 1
        rowLabels += ["C:SAMP:sampleType:::::"]
        zRow = numRow - 1

        newM = [0] * numRow
        for iR in range(numRow):
            newM[iR] = [NA_VALUE] * numCol
            if (iR != (numRow - 1)):
                for iC in range(numCol):
                    newM[iR][iC] = dataMatrix[iR][iC]

    else:
        newM = dataMatrix

    # outer loop is over columns ...

    print " "
    print " starting loop over %d columns ... " % numCol

    for iCol in range(numCol):
        curSample = colLabels[iCol]

        # 01 --> tumor primary		TP
        # 02 --> tumor recurring	TR
        # 06 --> tumor metastatic	TM
        # 11 --> normal tissue		NT
        # 20 --> control cell-line	CELLC

        if (curSample[13:15] == "01"):
            newM[zRow][iCol] = "TP"
        elif (curSample[13:15] == "02"):
            newM[zRow][iCol] = "TR"
        elif (curSample[13:15] == "03"):
            newM[zRow][iCol] = "TB"
        elif (curSample[13:15] == "04"):
            newM[zRow][iCol] = "TRBM"
        elif (curSample[13:15] == "05"):
            newM[zRow][iCol] = "TAP"
        elif (curSample[13:15] == "06"):
            newM[zRow][iCol] = "TM"
        elif (curSample[13:15] == "07"):
            newM[zRow][iCol] = "TAM"
        elif (curSample[13:15] == "08"):
            newM[zRow][iCol] = "THOC"
        elif (curSample[13:15] == "09"):
            newM[zRow][iCol] = "TBM"
        elif (curSample[13:15] == "10"):
            newM[zRow][iCol] = "NB"
        elif (curSample[13:15] == "11"):
            newM[zRow][iCol] = "NT"
        elif (curSample[13:15] == "20"):
            newM[zRow][iCol] = "CELLC"
        else:
            print " ERROR !!! need to handle more sample types !!! "
            print curSample
            sys.exit(-1)

    newD = {}
    newD['rowLabels'] = rowLabels
    newD['colLabels'] = colLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = newM

    return (newD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addTNtype(dataD):

    print " "
    print " in addTNtype ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    zRow = -1
    for iRow in range(numRow):
        if (rowLabels[iRow].find("TNtype") >= 0):
            print " ERROR in addTNtype ... this matrix already seems to have this feature ", rowLabels[iRow]
            print "     --> make sure that it is current and up to date ... "
            zRow = iRow

    if (zRow < 0):
        numRow += 1
        rowLabels += ["C:SAMP:TNtype:::::"]
        zRow = numRow - 1

        newM = [0] * numRow
        for iR in range(numRow):
            newM[iR] = [NA_VALUE] * numCol
            if (iR != (numRow - 1)):
                for iC in range(numCol):
                    newM[iR][iC] = dataMatrix[iR][iC]

    else:
        newM = dataMatrix

    # outer loop is over columns ...

    print " "
    print " starting loop over %d columns ... " % numCol

    for iCol in range(numCol):
        curSample = colLabels[iCol]

        # anytime there is a '0' it is a tumor sample of some
        # sort and anytime there is a '1' it is a normal sample
        if (curSample[13] == "0" ):
            newM[zRow][iCol] = "Tumor"
        elif (curSample[13] == "1" ):
            newM[zRow][iCol] = "Normal"
        else:
            newM[zRow][iCol] = "NA"

    newD = {}
    newD['rowLabels'] = rowLabels
    newD['colLabels'] = colLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = newM

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

    # add a new feature called sampleType
    dataD = addSampleType(dataD)

    # add a new feature called TNtype
    dataD = addTNtype(dataD)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
