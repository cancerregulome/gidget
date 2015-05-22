# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscTCGA
import tsvIO

import random
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
        if (len(aCode) < 16):
            tumorCode = aCode

        else:
            # if the barcode is at least 16 characters long, then we parse it
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

    fh = file(sampleFile)

    sampleList = []

    for aLine in fh:
        aLine = aLine.strip()
        sampleList += [aLine]

    fh.close()

    return (sampleList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def createOutputFileName ( inFile, rowLabel, aCat ):

    ## we want to decide whether or not to include part of the feature
    ## name in to the output file name ... if the category label is
    ## sufficiently generic that it might not be very unique/informative
    nameFlag = 0
    uCat = str(aCat).upper()
    if ( uCat in [ "0", "1", "NO", "YES", "FALSE", "TRUE", "MUT", "WT", "ALIVE", "DEAD", "MALE", "FEMALE" ] ):
        nameFlag = 1
    if ( len(uCat) == 2 ):
        if ( uCat[0] in [ "T", "N", "M", "C" ] ):
            try:
                iCat = int(uCat[1])
                nameFlag = 1
            except:
                doNothing = 1
    if ( uCat.find("PRIMARY") > 0 ): nameFlag = 1
    if ( uCat.find("METASTA") > 0 ): nameFlag = 1

    if ( nameFlag == 0 ):
        nameStr = ''
    else:
        tokenList = rowLabel.split(':')
        if ( tokenList[2].startswith("I(") ):
            subName = tokenList[2][2:-1]
            i1 = subName.find("|")
            if ( i1 > 0 ): subName = subName[:i1]
            i1 = subName.find(",")
            if ( i1 > 0 ): subName = subName[:i1] + "_vs_" + subName[i1+1:]
        else:
            subName = tokenList[2]
        nameStr = subName + "_"
        try:
            if ( len(tokenList[7]) > 0 ):
                nameStr += tokenList[7] + "_"
        except:
            doNothing = 1
        nameStr += "_"

    if (inFile.endswith(".tsv")):
        outFile = inFile[:-4] + "." + nameStr + str(aCat) + ".tsv"
    else:
        outFile = inFile + "." + nameStr + str(aCat) + ".tsv"

    return ( outFile )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        # there must be exactly 3 arguments ...
        if (len(sys.argv) != 3):
            print " Usage : %s <input file> <categorical feature> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        inFile = sys.argv[1]
        catFeature = sys.argv[2]

    print " "
    print " ***************************************************************** "
    print " calling readTSV ... ", inFile
    dataD = tsvIO.readTSV(inFile)
    if (dataD == {}):
        print "     --> file does not exist or is empty "
        sys.exit(-1)

    tsvIO.lookAtDataD(dataD)

    # make sure that we can find the specified feature ...
    try:
        rowLabels = dataD['rowLabels']
        colLabels = dataD['colLabels']
    except:
        print " ERROR in splitTSVbyCat ??? "
        sys.exit(-1)

    numRow = len(rowLabels)
    numCol = len(colLabels)

    if (catFeature != "random"):

        foundList = []
        for iR in range(numRow):
            if (rowLabels[iR].find(catFeature) >= 0):
                foundList += [iR]
        if (len(foundList) == 0):
            print " ERROR ??? could not find specified feature ??? ", catFeature
            sys.exit(-1)
        elif (len(foundList) > 1):
            if (1):
                print " found several matches ... choosing shortest one "
                strLen = 999999
                for iR in foundList:
                    if (len(rowLabels[iR]) < strLen):
                        strLen = len(rowLabels[iR])
                        jR = iR
                print "         --> %s " % rowLabels[jR]
                foundList = [jR]
            else:
                print " ERROR ??? found too many matches ??? ", catFeature
                for iR in foundList:
                    print rowLabels[iR]
                sys.exit(-1)

        iR = foundList[0]
        if (rowLabels[iR].startswith("N:")):
            print " ERROR ??? splitting should be done on a categorical (or binary) feature ! "
            sys.exit(-1)

        catVec = [0] * numCol
        catUnq = []
        for iC in range(numCol):
            catVec[iC] = dataD['dataMatrix'][iR][iC]
            if (catVec[iC] not in catUnq):
                catUnq += [catVec[iC]]

        catUnq.sort()
        print catUnq

    else:

        # for random splitting, use two arbitrary labels
        catUnq = ["r0", "r1"]
        catVec = [0] * numCol
        num0 = 0
        num1 = 0
        for iC in range(numCol):
            iRand = random.randint(0, 1)
            catVec[iC] = catUnq[iRand]
            if (iRand == 0):
                num0 += 1
            if (iRand == 1):
                num1 += 1
        print " --> generated random labels ... %d %d " % (num0, num1)

    # now we need to filter the matrix for each of the categories ...
    for aCat in catUnq:

        if (aCat == "NA"):
            continue

        print " "
        print " "
        print " handling ", aCat

        rmColList = []
        for iC in range(numCol):
            if (catVec[iC] != aCat):
                rmColList += [iC]

        numRm = len(rmColList)
        numKp = numCol - numRm
        if (numKp < 10):
            print " --> too few columns remaining ... skipping this category ... (%d) " % numKp

        else:

            outD = tsvIO.filter_dataMatrix(dataD, [], rmColList)

            # make sure that we are not left with any features that are all-NA ...
            # or nearly all 0 ... (adding this 10sep12)
            dataMatrix = outD['dataMatrix']
            outLabels = outD['rowLabels']
            numRowOut = len(dataMatrix)
            numColOut = len(dataMatrix[0])
            # print numRowOut, numColOut
            rmRowList = []
            rmTypes = {}
            for iRow in range(numRowOut):
                curType = outLabels[iRow][2:6]
                allNA = 1
                iCol = 0
                while (allNA == 1 and iCol < numColOut):
                    if (dataMatrix[iRow][iCol] != NA_VALUE and dataMatrix[iRow][iCol] != "NA"):
                        allNA = 0
                    iCol += 1
                if (allNA):
                    rmRowList += [iRow]
                    if (curType not in rmTypes.keys()):
                        rmTypes[curType] = 1
                    else:
                        rmTypes[curType] += 1
                    continue

                if (curType == "GEXP"):
                    numZero = 0
                    numNZ = 0
                    for iCol in range(numColOut):
                        if (dataMatrix[iRow][iCol] == 0):
                            numZero += 1
                        else:
                            numNZ += 1
                    if (numZero > 10 * numNZ):
                        rmRowList += [iRow]
                        if (curType not in rmTypes.keys()):
                            rmTypes[curType] = 1
                        else:
                            rmTypes[curType] += 1
                        continue

            if (len(rmRowList) > 0):
                print " "
                print " after checking for all-NA features ... "
                print " number of rows to be skipped : ", len(rmRowList)
                print " data types involved : ", rmTypes
                print " --> number of rows remaining : ", (numRowOut - len(rmRowList))
                print " "
                outD2 = tsvIO.filter_dataMatrix(outD, rmRowList, [])
                outD = outD2

            ## 30apr14 ... changing the way the output file name is created
            outFile = createOutputFileName ( inFile, rowLabels[iR], aCat )

            print " "
            print " calling writeTSV_dataMatrix ... ", outFile
            sortRowFlag = 0
            ### sortRowFlag = 1 # just for TESTING 16aug14
            sortColFlag = 0
            ### sortColFlag = 1 # just for TESTING 16aug14
            tsvIO.writeTSV_dataMatrix(
                outD, sortRowFlag, sortColFlag, outFile)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
