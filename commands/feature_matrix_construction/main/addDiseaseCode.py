# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def updateDiseaseCode(dataD):

    print " "
    print " in updateDiseaseCode ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    keepRow = -1
    for iRow in range(numRow):
        if (rowLabels[iRow].find("disease_code") >= 0):
            keepRow = iRow

    if ( keepRow < 0 ): sys.exit(-1)

    # outer loop is over columns ...
    print " "
    print " starting loop over %d columns ... " % numCol

    for iCol in range(numCol):
        curSample = colLabels[iCol]
        diseaseCode = miscTCGA.barcode_to_disease(curSample)
        if (diseaseCode == "NA"):
            print " got an unknown disease code ??? ", curSample, diseaseCode
        else:
            if (dataMatrix[keepRow][iCol] == "NA" ):
                dataMatrix[keepRow][iCol] = diseaseCode
                print " updating disease code from NA to %s " % diseaseCode
            else:
                if ( dataMatrix[keepRow][iCol] != diseaseCode ):
                    print " WARNING ??? disease codes do not match ??? !!! ", dataMatrix[keepRow][iCol], diseaseCode
                    print "         current value in disease_code feature : ", dataMatrix[keepRow][iCol]
                    print "         based on the barcode to disease map   : ", diseaseCode
                    print "         leaving as is ... "
                    ## sys.exit(-1)
            

    newD = {}
    newD['rowLabels'] = rowLabels
    newD['colLabels'] = colLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = dataMatrix

    return (newD)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addDiseaseCode(dataD):

    print " "
    print " in addDiseaseCode ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    for iRow in range(numRow):
        if (rowLabels[iRow].find("disease_code") >= 0):
            return ( updateDiseaseCode(dataD) )
            ## print " ERROR in addDiseaseCode ... this matrix already seems to have this feature ", rowLabels[iRow]
            ## print " --> will NOT add a new feature (output TSV == input TSV) "
            ## return (dataD)

    numRow += 1
    rowLabels += ["C:CLIN:disease_code:::::"]

    newM = [0] * numRow
    for iR in range(numRow):
        newM[iR] = [NA_VALUE] * numCol
        if (iR != (numRow - 1)):
            for iC in range(numCol):
                newM[iR][iC] = dataMatrix[iR][iC]

    # outer loop is over columns ...
    print " "
    print " starting loop over %d columns ... " % numCol

    for iCol in range(numCol):
        curSample = colLabels[iCol]
        diseaseCode = miscTCGA.barcode_to_disease(curSample)
        if (diseaseCode == "NA"):
            print " got an unknown disease code ??? ", curSample, diseaseCode
        newM[numRow - 1][iCol] = diseaseCode

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
    dataD = addDiseaseCode(dataD)

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
