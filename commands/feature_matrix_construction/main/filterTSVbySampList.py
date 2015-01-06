# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscTCGA
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# the input is a data dictionary which should have 4 keys:
# 'dataType'	single string, eg 'GEXP'
# 'rowLabels'	vector of feature labels
# 'colLabels'	vector of column (sample) labels
# 'dataMatrix'	matrix of values
# the output is a data dictionary with the same # of rows, but some columns
# may have been removed if they do not represent tumor samples ... also the
# TCGA barcodes are stripped down to the point where they uniquely identify
# tumor samples
#
# FIXME: this should be modified to take a list of rows or columns to remove
# and then return a new dataD ... (put that into tsvIO???)


def removeNonTumorSamples(dataD):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    keepCols = [0] * numCol
    tumorList = []
    numOutCol = 0

    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]
        tumorCode = ''

        # if the barcode is not even long enough to specify the sample type,
        # we will just assume that we keep it ...
        if (len(aCode) < 15):
            tumorCode = aCode

        else:
            # if the barcode is at least 15 characters long, then we parse it
            # ...
            aCode = miscTCGA.fixTCGAbarcode(aCode)
            (site, patient, sample, vial, portion, analyte,
             plate, center) = miscTCGA.parseTCGAbarcode(aCode)
            try:
                iSample = int(sample)
            except:
                iSample = -1
                if (sample != aCode):
                    print " what is going on here ??? ", aCode
                    sys.exit(-1)
            if (iSample > 0 and iSample < 10):
                tumorCode = miscTCGA.sampleLevelCode(aCode)

        if (tumorCode != ''):
            if (tumorCode not in tumorList):
                tumorList += [tumorCode]
                keepCols[jj] = 1
                numOutCol += 1
            else:
                print " WARNING: in removeNonTumorSamples ... multiple columns for the same tumor sample ??? "
                print aCode, tumorCode
                # print tumorList
                print "          --> keeping only the first one "
                # sys.exit(-1)

    rmColList = []
    for jj in range(numCol):
        if (keepCols[jj] == 0):
            rmColList += [jj]
            print "             will remove sample <%s> " % dataD['colLabels'][jj]

    # filter out the columns we don't want ...
    dataD = tsvIO.filter_dataMatrix(dataD, [], rmColList)
    print " back from filter_dataMatrix ... ", dataD['colLabels'][:5]

    # NOTE: this next bit may no longer be necessary ...
    # and also set the shortened TCGA barcodes as labels ...
    if (len(tumorList) != len(dataD['dataMatrix'][0])):
        print " ERROR !!! length of tumorList does not correspond to size of dataMatrix !!! "
        print len(tumorList)
        tsvIO.lookAtDataD(dataD)
        sys.exit(-1)

    dataD['colLabels'] = tumorList
    print " now using shortened barcodes .. ", dataD['colLabels'][:5]

    return (dataD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def dropSampleTypeFromBarcodes(dataD):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    codeList = []
    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]
        if (aCode > 12):
            aCode = aCode[:12]
            dataD['colLabels'][jj] = aCode
        if (aCode not in codeList):
            codeList += [aCode]
        else:
            print " WARNING in dropSampleTypeFromBarcodes ... duplicates ??? ", aCode
            # print codeList
            # sys.exit(-1)

    return (dataD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def intersectLists(aList, bList):
    cList = []
    for aToken in aList:
        if (aToken in bList):
            cList += [aToken]

    return (cList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def unionLists(aList, bList):

    for bToken in bList:
        if (bToken not in aList):
            aList += [bToken]

    return (aList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMappingVector(unionLabels, curLabels):

    mapVec = [-1] * len(curLabels)
    for ii in range(len(curLabels)):
        aLabel = curLabels[ii]
        if (aLabel.startswith("TCGA-")):
            aLabel = miscTCGA.sampleLevelCode(aLabel)
        try:
            jj = unionLabels.index(aLabel)
            mapVec[ii] = jj
        except:
            print " ERROR ... did not find <%s> in union labels ... " % aLabel
            print unionLabels
            sys.exit(-1)

    print "                 mapping vector from %d into %d ... " % (len(curLabels), len(unionLabels))
    print "                 ", mapVec[:20]
    # print curLabels[:20]
    # print unionLabels[:20]
    print " "

    return (mapVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def makeDataTypeString(dTypeList, fTypeList):

    # print " in makeDataTypeString ... "
    # print dTypeList
    # print fTypeList

    if ("MISC" in fTypeList):
        dTypeString = "M:MISC"
        return (dTypeString)

    if (len(dTypeList) == 1):
        dTypeString = dTypeList[0]
    else:
        dTypeString = "M"

    dTypeString += ":"
    for aType in fTypeList:
        if (dTypeString[-1] != ":"):
            dTypeString += "+"
        dTypeString += aType

    print " output data type string : <%s> " % dTypeString

    return (dTypeString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readSampleListFromFile(sampleFile):

    try:
        fh = file(sampleFile)
    except:
        print " FAILED to read input list from <%s> " % sampleFile
        return ([])

    sampleList = []

    for aLine in fh:
        aLine = aLine.strip()
        if (aLine.startswith("TCGA")):
            sampleList += [aLine]
        elif (len(aLine) > 0):
            print "     NOT USING this input line : <%s> " % aLine

    fh.close()

    return (sampleList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def is_in_list(tmpLabel, sampleList, aFlag):

    # so the input sampleList may have variable length barcodes,
    # eg TCGA-BR-4184-11A-01D-1130-01
    # TCGA-BR-4186

    # while the tmpLabel is either a 'patient' barcode, or a 'sample'
    # barcode, or a full-length barcode ...

    lowerT = tmpLabel.lower()

    for aSample in sampleList:
        lowerA = aSample.lower()
        if (aFlag == "strict"):
            if (lowerA == lowerT):
                return (1)
        else:
            if (lowerT.startswith(lowerA)):
                return (1)

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        # there must be 2 + 3N parameters, where N is the # of sample-lists
        # being used for filtering ...
        if (len(sys.argv) < 6):
            print " Usage : %s <input file> <output file> <sample-list> <{black,white}> <{loose,strict}> " % sys.argv[0]
            print " "
            print " Notes : a BLACK list means samples that any samples in this list must be removed "
            print "         from the input file, and this is generally done with LOOSE filtering "
            print "         so that if a patient barcode is given, then all other barcodes that "
            print "         even just partially match that barcode will also be BLACKed out. "
            print " "
            print "         a WHITE list means that ONLY samples that are in this list can be included "
            print "         in the output file, and this is generally done with STRICT filtering so that "
            print "         if the methylation data from a particular sample is in the white list, that "
            print "         does not necessarily mean that the microRNA data from the same sample can "
            print "         automatically be included as well -- it must be listed explicitly. "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        inFile = sys.argv[1]
        outFile = sys.argv[2]

        ii = 3
        listInfo = []
        while (len(sys.argv) >= (ii + 2)):
            listInfo += [sys.argv[ii:ii + 3]]
            ii += 3
        if (len(listInfo) < 1):
            print " ERROR ??? no sample-list information provided ??? "
            sys.exit(-1)

    print " "
    print " in filterTSVbySampList.py ... "
    print "         input file  : ", inFile
    print "         output file : ", outFile
    print "         list info   : ", listInfo
    print " "

    # print " "
    # print " ***************************************************************** "
    # print " calling readTSV ... ", inFile
    dataD = tsvIO.readTSV(inFile)
    if (dataD == {}):
        sys.exit(-1)

    tsvIO.lookAtDataD(dataD)

    # print " "
    # print " reading sample list ... "
    numLists = len(listInfo)
    listDetails = [0] * numLists
    listBW = [0] * numLists
    listLS = [0] * numLists
    for iList in range(numLists):
        print " --> loading sample list #%d from <%s> " % ((iList + 1), listInfo[iList][0])
        listDetails[iList] = readSampleListFromFile(listInfo[iList][0])
        listBW[iList] = listInfo[iList][1]
        listLS[iList] = listInfo[iList][2]
        if (len(listDetails[iList]) > 0):
            print "     %4d samples found, eg <%s> " % (len(listDetails[iList]), listDetails[iList][0])
        else:
            print "        0 samples found "
            if (listLS[iList] == "strict"):
                print "             --> NO strict filtering can/will be applied "

    # now we need to figure out which columns we will keep/remove ...
    colLabels = dataD['colLabels']
    dataMatrix = dataD['dataMatrix']
    numCol = len(dataMatrix[0])
    if (numCol != len(colLabels)):
        print " mismatched sizes ??? ", numCol, len(colLabels)
        sys.exit(-1)

    print " "
    print "     %4d samples in input data matrix " % numCol
    print " debug : colLabels  : ", colLabels[1:5]

    print " "
    print " building up skipColList ... "
    skipColList = []

    ## first, we loop over the black-lists and check each column
    ## label to see if it should be added to the skipColList ...
    numSkip = 0
    print " "
    print " FIRST checking black lists ... "
    for iList in range(numLists):
        bwFlag = listBW[iList]
        if ( bwFlag != "black" ): continue

        sampleList = listDetails[iList]
        if (len(sampleList) == 0): continue

        lsFlag = listLS[iList]
        print "         examining list #%d (%d,%s,%s) " % ((iList + 1), len(sampleList), bwFlag, lsFlag)

        for iCol in range(numCol):
            # print colLabels[iCol], sampleList[1:5]
            tmpLabel = colLabels[iCol]
            # print tmpLabel

            # if this column has already been added to the skip-list,
            # we don't need to add it again ...
            if (iCol in skipColList):
                print "     <%s> is ALREADY in the skip-list (list #%d) " % (tmpLabel, (iList + 1))
                continue

            if (is_in_list(tmpLabel, sampleList, lsFlag)):
                skipColList += [iCol]
                numSkip += 1

        print "         --> %d additional samples to be skipped " % numSkip, listInfo[iList][0], bwFlag, lsFlag

    ## now we're going to loop over the column labels and see if they
    ## are in any of the white lists ...
    print " "
    print " NOW checking white lists ... "
    for iCol in range(numCol):
        tmpLabel = colLabels[iCol]

        ## initialize the isWhite flag to TRUE
        isWhite = 1

        for iList in range(numLists):
            bwFlag = listBW[iList]
            if ( bwFlag == "black" ): continue

            sampleList = listDetails[iList]
            if (len(sampleList) == 0): continue

            ## if we get to here, then we have at least one white list
            ## so reset the isWhite flag to FALSE
            isWhite = 0

            lsFlag = listLS[iList]
            print "         examining list #%d (%d,%s,%s) " % ((iList + 1), len(sampleList), bwFlag, lsFlag)

            if (is_in_list(tmpLabel, sampleList, lsFlag)):
                isWhite = 1

        ## once we get back to here, if isWhite is FALSE, then add to skipColList
        if ( iCol in skipColList):
            print "     <%s> is ALREADY in the skip-list (list #%d) " % (tmpLabel, (iList + 1))
            continue

        if ( isWhite == 0 ):
            skipColList += [iCol]
            numSkip += 1

    print "         --> %d additional samples to be skipped " % numSkip

    # print skipColList

    print " "
    print " number of columns to be skipped : ", len(skipColList)
    print " --> number of columns remaining : ", (numCol - len(skipColList))

    if (0):
        if (len(skipColList) == 1):
            print "     for example ", colLabels[skipColList[0]]
        elif (len(skipColList) > 1):
            print "     for example ", colLabels[skipColList[0]], colLabels[skipColList[-1]]

    else:
        print " "
        print " "
        for iCol in range(len(skipColList)):
            print "    REMOVING SAMPLE %s " % colLabels[skipColList[iCol]]
        print " "
        print " "

    if (len(skipColList) > int(0.90 * numCol)):
        print " "
        print " WARNING !!! more than 90% of the data is going to be lost ??? !!! "
        print " "
        # sys.exit(-1)

    # print " "
    # print " calling filter_dataMatrix ... "
    outD = tsvIO.filter_dataMatrix(dataD, [], skipColList)

    # make sure that we are not left with any features that are all-NA ...
    dataMatrix = outD['dataMatrix']
    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    skipRowList = []
    for iRow in range(numRow):
        allNA = 1
        iCol = 0
        while (allNA == 1 and iCol < numCol):
            if (dataMatrix[iRow][iCol] != NA_VALUE):
                allNA = 0
            iCol += 1
        if (allNA):
            skipRowList += [iRow]

    if (len(skipRowList) > 0):
        print " after checking for all-NA features ... "
        print " number of rows to be skipped : ", len(skipRowList)
        print " --> number of rows remaining : ", (numRow - len(skipRowList))
        outD2 = tsvIO.filter_dataMatrix(outD, skipRowList, [])
        outD = outD2

    # set up sorting options ...
    sortRowFlag = 0
    sortColFlag = 0
    rowOrder = []
    colOrder = []

    # print " "
    # print " calling writeTSV_dataMatrix ... ", outFile
    tsvIO.writeTSV_dataMatrix(outD, sortRowFlag, sortColFlag, outFile, rowOrder, colOrder)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
