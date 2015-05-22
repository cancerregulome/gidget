# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscTCGA
import tsvIO

import os
import sys
import time

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


def removeNonTumorSamples(dataD):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    keepCols = [0] * numCol
    tumorList = []
    numOutCol = 0

    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]
        tumorCode = ''

        # hack to not mess with ITMI samples ...
        if (aCode.startswith("ITMI-")):
            tumorCode = aCode

        # if the barcode is not even long enough to specify the sample type,
        # we will just assume that we keep it ...
        elif (len(aCode) < 16):
            tumorCode = aCode

        else:
            # if the barcode is at least 16 characters long, then we parse it
            # ...
            if (aCode.startswith("ITMI-")):
                doNothing = 1
            else:
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

def removeDuplicateSamples(dataD, barcodeLen, firstLast=0):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    keepCols = [1] * numCol
    numOutCol = 0

    sampleDict = {}

    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]

        if (aCode.startswith("ITMI-")):
            doNothing = 1

        else:
            aCode = miscTCGA.fixTCGAbarcode(aCode)
            if (len(aCode) < barcodeLen):
                aCode = miscTCGA.get_barcode16(aCode)

        if (aCode not in sampleDict.keys()):
            sampleDict[aCode] = 0

        sampleDict[aCode] += 1

    allKeys = sampleDict.keys()
    allKeys.sort()

    for aKey in allKeys:

        if (sampleDict[aKey] > 1):
            dupList = []
            print " duplicate columns for sample <%s> ??? " % aKey
            for jj in range(numCol):
                aCode = dataD['colLabels'][jj]
                if (aCode.startswith(aKey)):
                    print "        ", aCode
                    dupList += [aCode]
            dupList.sort()
            # print dupList

            ## ['TCGA-A3-3308-01A-01T-0860-13', 'TCGA-A3-3308-01A-02R-1324-13']
            # now decide which one to keep ... we prefer "R" over "T"
            # apparently ...
            keepCode = "NA"
            for kk in range(len(dupList)):
                aCode = dupList[kk]
                if (len(aCode) > 19):
                    if (aCode[19] == "R"):
                        keepCode = aCode

            # if there isn't one with an "R", just take either the first or
            # the last one, based on the firstLast flag ...
            if (keepCode == "NA"):
                if (firstLast == 0):
                    keepCode = dupList[-1]
                elif (firstLast == 1):
                    keepCode = dupList[0]
                else:
                    keepCode = dupList[0]

            # now create the rmList by removing the keepCode from the dupList
            # ...
            rmList = []
            for aCode in dupList:
                if (aCode != keepCode):
                    rmList += [aCode]

            # and finally set the flags to drop the duplicates ...
            for jj in range(numCol):
                aCode = dataD['colLabels'][jj]
                if (aCode in rmList):
                    keepCols[jj] = 0
                    print "         --> will drop column %d <%s> " % (jj, aCode)

    rmColList = []
    for jj in range(numCol):
        if (keepCols[jj] == 0):
            rmColList += [jj]
            print "             will remove sample <%s> " % dataD['colLabels'][jj]

    # filter out the columns we don't want ...
    dataD = tsvIO.filter_dataMatrix(dataD, [], rmColList)
    print " back from filter_dataMatrix ... ", dataD['colLabels'][:5]

    return (dataD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def dropSampleTypeFromBarcodes(dataD):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    codeList = []
    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]
        if (aCode.startswith("ITMI-")):
            doNothing = 1
        elif (len(aCode) > 12):
            aCode = aCode[:12]
            dataD['colLabels'][jj] = aCode
        if (aCode not in codeList):
            codeList += [aCode]
        else:
            print " WARNING in dropSampleTypeFromBarcodes ... duplicates ??? ", aCode, dataD['colLabels'][jj]
            # print codeList
            # sys.exit(-1)

    return (dataD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def dropDetailsFromBarcodes(dataD):

    ## miscTCGA.lookAtBarcodes ( dataD['colLabels'] )
    numCol = len(dataD['colLabels'])
    codeList = []

    for jj in range(numCol):
        aCode = dataD['colLabels'][jj]

        if (aCode.startswith("ITMI-")):
            doNothing = 1

        elif (len(aCode) > 16):
            aCode = aCode[:16]
            dataD['colLabels'][jj] = aCode

        # TCGA-CJ-4635
        # new on 15-apr-13 ... add on the sampleType portion to the barcode
        # modified on 14-feb-15
        elif (len(aCode) < 16):
            aCode = miscTCGA.get_barcode16(aCode)
            dataD['colLabels'][jj] = aCode

        if (aCode not in codeList):
            codeList += [aCode]
        else:
            print " WARNING in dropDetailsFromBarcodes ... duplicates ??? ", aCode, dataD['colLabels'][jj]
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

    print " in getMappingVector ... "
    print len(unionLabels), unionLabels[:3]
    print len(curLabels),   curLabels[:3]

    if (unionLabels[0].startswith("TCGA-")):
        if (curLabels[0].startswith("TCGA-")):
            len1 = len(unionLabels[0])
            len2 = len(curLabels[0])
            print " barcode lengths : ", len1, len2

    mapVec = [-1] * len(curLabels)

    for ii in range(len(curLabels)):

        aLabel = curLabels[ii]
        if (aLabel.startswith("TCGA-")):
            if (len1 < len2):
                aLabel = aLabel[:len1]
            ## aLabel = miscTCGA.sampleLevelCode ( aLabel )

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

def getBarcodeLength ( inFileList ):

    maxBlen = 12
    minBlen = 28

    for aFile in inFileList:
        try:
            fh = file ( aFile, 'r' )
            aLine = fh.readline()
            fh.close()
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            numB = len(tokenList) - 1
            bLen = len(tokenList[1])
            for iB in range(numB):
                bLen = max ( bLen, len(tokenList[iB+1]) )
            if ( bLen > maxBlen ): maxBlen = bLen
            if ( bLen < minBlen ): minBlen = bLen
        except:
            print " failed to read barcodes from ", aFile

    print " "
    print " FOUND range of barcode lengths : ", minBlen, maxBlen
    print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):

        if (len(sys.argv) < 3):
            print " Usage : %s <input files (at least 1)> <output file> [pruneOrder] [colMaxNAfrac] [rowMaxNAfrac] " % sys.argv[0]
            print " NOTE  : either all 3 optional arguments must be specified, or none of them "
            print " ERROR in using mergeTSV.py "
            sys.exit(-1)

        # figure out if the last 3 options specify pruning or not ...
        doPrune = 0
        try:
            pruneOrder = sys.argv[-3].lower()
            colMaxNAfrac = float(sys.argv[-2])
            rowMaxNAfrac = float(sys.argv[-1])
            doPrune = 1
            for ii in range(len(pruneOrder)):
                if (pruneOrder[ii] != 'c' and pruneOrder[ii] != 'r'):
                    doPrune = 0
        except:
            doPrune = 0

        if (doPrune):
            if (len(sys.argv) < 5):
                print " Usage : %s <input files (at least 1)> <output file> [pruneOrder] [colMaxNAfrac] [rowMaxNAfrac] " % sys.argv[0]
                print " NOTE  : either all 3 optional arguments must be specified, or none of them "
                print " ERROR in using mergeTSV.py "
                sys.exit(-1)
            inFileList = sys.argv[1:-4]
            outFile = sys.argv[-4]
        else:
            inFileList = sys.argv[1:-1]
            outFile = sys.argv[-1]
            pruneOrder = "NA"

        # check that at least one of the input files exists ...
        exFileList = []
        for aFile in inFileList:
            if (os.path.isfile(aFile)):
                exFileList += [aFile]
            else:
                print "     WARNING in mergeTSV : input file <%s> does not exist " % aFile
        inFileList = exFileList
        if (len(inFileList) < 1):
            print " "
            print " ERROR: you should have at least one input files that need to be merged ... "
            print " "
            sys.exit(-1)

        # and that the output file does not ...
        if (os.path.isfile(outFile)):
            print "     ERROR in mergeTSV : output file <%s> already exists " % outFile
            sys.exit(-1)

    print " "
    print " in mergeTSV : "
    print " "
    print "  input file list : ", len(inFileList), inFileList
    print " output file name : ", outFile
    print " "
    print ' (a) TIME ', time.asctime(time.localtime(time.time()))

    inputData = []
    dTypeList = []
    fTypeList = []

    # NEW on 14-feb-2015 ... want to check all of the input file(s) 
    # for the input barcode lengths ...
    getBarcodeLength ( inFileList )

    # if trying to prune LOTS of rows and columns, then set the *MaxNAfrac
    # values to small values ... if trying not to prune ANYTHING, then set
    # the values near 1 ...

    ## colMaxNAfrac = 0.90
    ## rowMaxNAfrac = 0.90

    for aFile in inFileList:

        print " "
        print " ***************************************************************** "
        print " calling readTSV ... ", aFile
        testD = tsvIO.readTSV(aFile)

        ## check to see if we actually have any data ...
        skipFile = 0
        try:
            if (len(testD) == 0): skipFile = 1
            if ( len(testD['rowLabels']) == 0 ): skipFile = 1
            if ( len(testD['colLabels']) == 0 ): skipFile = 1
        except:
            print " ERROR in looking at data from <%s> ??? " % ( aFile )
            skipFile = 1

        if ( skipFile ):
            print " --> nothing found ??? continuing ... "
            continue

        tsvIO.lookAtDataD(testD)

        if (1):

            # TCGA-CJ-4635-01A-02R
            # the first 12 characters identify the patient
            # the first 16 characters identify the sample

            # now we check for duplicates at the sample level ...
            print " "
            print " checking for duplicates ... "
            testD = removeDuplicateSamples(testD, 16, 0)

            if (1):
                print " "
                print " dropping details (beyond sample type) at the end of the barcodes ... "
                testD = dropDetailsFromBarcodes(testD)
                tsvIO.lookAtDataD(testD)

        if (0):

            print " "
            print " at the individual input file level, remove rows and then columns with too many missing values ... "
            skipRowList = tsvIO.getSkipList(rowMaxNAfrac, testD, 'row')
            if (skipRowList != []):
                testD = tsvIO.filter_dataMatrix(testD, skipRowList, [])
            tsvIO.lookAtDataD(testD)

            skipColList = tsvIO.getSkipList(colMaxNAfrac, testD, 'col')
            if (skipColList != []):
                testD = tsvIO.filter_dataMatrix(testD, [], skipColList)
            tsvIO.lookAtDataD(testD)

        # finally, add this dictionary to our list of input data sets ...
        inputData += [testD]

        tokenList = testD['dataType'].split(':')
        if (len(tokenList) != 2):
            if (testD['dataType'] == "NA"):
                testD['dataType'] = "M:MISC"
                tokenList = testD['dataType'].split(':')
            print " ERROR in mergeTSV ... the dataType in the upper-left corner of <%s> does not appear to be correct ? " % aFile
            print testD['dataType']
            sys.exit(-1)
        dType = tokenList[0]
        fType = tokenList[1]
        if (dType not in dTypeList):
            dTypeList += [dType]
        if (fType not in fTypeList):
            fTypeList += [fType]

    print " "
    numD = len(inputData)
    print " DONE looping over input files ... have %d input data sets " % numD
    print " "
    print " "
    if (numD == 0):
        print "     --> EXITING "
        sys.exit(-1)

    print ' (b) TIME ', time.asctime(time.localtime(time.time()))

    # now we build up a union of the lists of features (row) and samples
    # (columns)
    print " preparing union label lists ... "
    unionRowLabels = []
    unionColLabels = []
    for iD in range(numD):
        rowLabels = inputData[iD]['rowLabels']
        colLabels = inputData[iD]['colLabels']
        print "                 ", iD, len(rowLabels), len(colLabels)
        unionRowLabels = unionLists(unionRowLabels, rowLabels)
        unionColLabels = unionLists(unionColLabels, colLabels)

    numURow = len(unionRowLabels)
    numUCol = len(unionColLabels)
    print " --> maximum output matrix size : ", numURow, numUCol
    print "     creating output matrix full of ", NA_VALUE
    outMatrix = [0] * numURow
    for iR in range(numURow):
        outMatrix[iR] = [NA_VALUE] * numUCol

    print " "
    print " "
    for iD in range(numD):
        print "                 incorporating dataset %d into union matrix %s " % (iD, inputData[iD]['dataType'])
        curRowLabels = inputData[iD]['rowLabels']
        curColLabels = inputData[iD]['colLabels']
        numRow = len(curRowLabels)
        numCol = len(curColLabels)

        rowMap = getMappingVector(unionRowLabels, curRowLabels)
        colMap = getMappingVector(unionColLabels, curColLabels)

        for ii in range(numRow):
            iu = rowMap[ii]
            for jj in range(numCol):
                ju = colMap[jj]

                # if the value currently in the 'out' matrix is not NA, then evidently
                # there was already something there ... is it different???

                if (outMatrix[iu][ju] != NA_VALUE and outMatrix[iu][ju] != "NA"):
                    if (inputData[iD]['dataMatrix'][ii][jj] != NA_VALUE and inputData[iD]['dataMatrix'][ii][jj] != "NA"):
                        if (outMatrix[iu][ju] != inputData[iD]['dataMatrix'][ii][jj]):
                            # print "     --> WARNING: not replacing previously
                            # set value ... ", iu, ju, outMatrix[iu][ju],
                            # inputData[iD]['dataMatrix'][ii][jj],
                            # curRowLabels[ii], curColLabels[jj]
                            doNothing = 1
                    continue
                else:
                    if (inputData[iD]['dataMatrix'][ii][jj] == ""):
                        print "     ERROR ??? blank data token ??? ", iu, ju, inputData[iD]['dataMatrix'][ii][jj]
                        sys.exit(-1)
                    outMatrix[iu][ju] = inputData[iD]['dataMatrix'][ii][jj]
                    continue

                print " SHOULD NOT GET HERE ANYMORE "
                sys.exit(-1)

                # OLD:
                if (outMatrix[iu][ju] != NA_VALUE):
                    if (inputData[iD]['dataMatrix'][ii][jj] != NA_VALUE and inputData[iD]['dataMatrix'][ii][jj] != "NA"):
                        if (outMatrix[iu][ju] != inputData[iD]['dataMatrix'][ii][jj]):
                            print " WARNING ??? different data already here ??? ", iu, ju, outMatrix[iu][ju], inputData[iD]['dataMatrix'][ii][jj], curRowLabels[ii], curColLabels[jj]
                            sys.exit(-1)
                            outMatrix[iu][ju] = inputData[
                                iD]['dataMatrix'][ii][jj]
                elif (outMatrix[iu][ju] != "NA"):
                    if (inputData[iD]['dataMatrix'][ii][jj] != NA_VALUE and inputData[iD]['dataMatrix'][ii][jj] != "NA"):
                        if (outMatrix[iu][ju] != inputData[iD]['dataMatrix'][ii][jj]):
                            print " WARNING ??? different data already here ??? ", iu, ju, outMatrix[iu][ju], inputData[iD]['dataMatrix'][ii][jj], curRowLabels[ii], curColLabels[jj]
                            sys.exit(-1)
                            outMatrix[iu][ju] = inputData[
                                iD]['dataMatrix'][ii][jj]
                else:
                    outMatrix[iu][ju] = inputData[iD]['dataMatrix'][ii][jj]

    print ' (c) TIME ', time.asctime(time.localtime(time.time()))

    outD = {}
    outD['rowLabels'] = unionRowLabels
    outD['colLabels'] = unionColLabels
    outD['dataMatrix'] = outMatrix

    sortRowFlag = 0  # seems best not to sort the rows
    sortColFlag = 0

    if (sortRowFlag):
        fTypeList.sort()
    outD['dataType'] = makeDataTypeString(dTypeList, fTypeList)

    if (pruneOrder != "NA"):
        print " "
        print " now calling pruneTSV_dataMatrix on the merged dataMatrix ... ", pruneOrder
        outD = tsvIO.pruneTSV_dataMatrix(outD, rowMaxNAfrac, colMaxNAfrac, pruneOrder)
    else:
        print " "
        print " NOT doing any pruning of the merged dataMatrix "

    print " "
    print ' (d) TIME ', time.asctime(time.localtime(time.time()))
    print " calling writeTSV_dataMatrix ... ", outFile
    tsvIO.writeTSV_dataMatrix(outD, sortRowFlag, sortColFlag, outFile)

    print " "
    print " DONE ", dTypeList, fTypeList
    print ' (e) TIME ', time.asctime(time.localtime(time.time()))
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
