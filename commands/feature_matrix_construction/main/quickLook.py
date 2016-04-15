# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscIO
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtHeaderTokens(aTokens):

    patientList = []
    typeDict = {}

    for a in aTokens:
        if (a.upper().startswith("TCGA-")):
            patientID = a[8:12].upper()
            if (patientID not in patientList):
                patientList += [patientID]
            if (len(a) >= 15):
                typeID = a[13:15]
                if (typeID not in typeDict.keys()):
                    typeDict[typeID] = 0
                typeDict[typeID] += 1
            else:
                print " WARNING : no typeID ??? <%s> " % a

    if (len(patientList) > 0):
        print " "
        print " # of unique patients : ", len(patientList)
        print " sample type counts   : ", typeDict
        print " "
        print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lookAtLine(aLine):

    if (1):
        print len(aLine)

        numTab = 0
        numLF = 0
        numCR = 0
        numSpace = 0
        numDigit = 0
        numLetter = 0

        numLinesOut = 0

        i1 = 0
        for ii in range(len(aLine)):
            ordVal = ord(aLine[ii])
            if (1):
                if (ordVal == 9):
                    # this is a tab ...
                    numTab += 1
                elif (ordVal == 10):
                    numLF += 1
                elif (ordVal == 13):
                    numCR += 1
                elif (ordVal == 32):
                    numSpace += 1
                elif ((ordVal >= 48 and ordVal <= 57) or (ordVal == 46)):
                    numDigit += 1
                elif ((ordVal >= 65 and ordVal <= 90) or (ordVal >= 97 and ordVal <= 122)):
                    numLetter += 1
                elif (ordVal < 32 or ordVal > 126):
                    print " %6d     %3d " % (ii, ordVal)
                else:

                    # print " %6d <%s> %3d " % ( ii, aLine[ii], ord ( aLine[ii]
                    # ) )
                    doNothing = 1
            if (ordVal == 13):
                i2 = ii
                # print " --> writing out from %d to %d " % ( i1, i2 )
                # print " <%s> " % aLine[i1:i2]
                numLinesOut += 1
                ## if ( numLinesOut == 5 ): sys.exit(-1)
                ## fhOut.write ( "%s\n" % aLine[i1:i2] )
                i1 = i2 + 1

        print numTab, numLF, numCR, numSpace, numDigit, numLetter
        print numLinesOut

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 2 and len(sys.argv) != 3):
        print ' Usage : %s <filename> [hist-file] ' % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    inFilename = sys.argv[1]
    if (len(sys.argv) == 3):
        histFilename = sys.argv[2]
        noHist = 0
    else:
        noHist = 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    fh = file(inFilename)
    numLines = 10
    for iLine in range(numLines):
        aLine = fh.readline()
        # look for carriage return / line-feed ?
        ## lookAtLine ( aLine )
        ## aLine = aLine.strip()
        aTokens = aLine.split('\t')
        if (len(aTokens) > 15):
            print len(aTokens), aTokens[:5], aTokens[-5:]
        else:
            print len(aTokens), aTokens

    numLines = miscIO.num_lines(fh)
    print "\n\n total # of lines in file : %d " % numLines
    fh.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    fh = file(inFilename)
    aLine = fh.readline()
    aTokens = aLine.split('\t')
    numA = len(aTokens)
    print " number of header tokens : ", numA
    lookAtHeaderTokens(aTokens)

    done = 0
    iLine = 0
    while not done:
        bLine = fh.readline()
        iLine += 1
        # print bLine
        bTokens = bLine.split('\t')
        # print len(bTokens), bTokens
        numB = len(bTokens)
        if (numB < 2):
            done = 1
            continue
        if (numA != numB):
            print "     wrong number of tokens ??? ", numB, numA, iLine
            print bTokens
            print bLine
            sys.exit(-1)
        for ii in range(numA):
            if (bTokens[ii] == ''):
                print "     WARNING ... blank token ", ii
                print bTokens
                print bLine
                ## sys.exit(-1)
    fh.close()
    # sys.exit(-1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    fh = file(inFilename)
    aLine = fh.readline()
    bLine = fh.readline()
    fh.close()

    try:
        if (aLine[-1] == '\n'):
            aLine = aLine[:-1]
        if (bLine[-1] == '\n'):
            bLine = bLine[:-1]
    except:
        print " ERROR ??? bad data file ??? ", inFilename
        sys.exit(-1)

    aTokens = aLine.split('\t')
    bTokens = bLine.split('\t')

    numA = len(aTokens)
    numB = len(bTokens)
    print numA, numB
    if (numA != numB):
        print " ERROR ??? first two lines do not have the same numbers of tokens ??? "
        sys.exit(-1)
    if (numA < 50):
        for ii in range(numA):
            print ii, "\t", aTokens[ii], "\t:\t", bTokens[ii]
        print " "
        print " "

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print " opening file <%s> " % inFilename
    fh = file(inFilename)
    aLine = fh.readline()

    # hdrTokens has the list of column ids (patients presumably)
    hdrTokens = aLine.split('\t')
    numCol = len(hdrTokens)
    if (numCol > 15):
        print numCol, hdrTokens[:5], hdrTokens[-5:]
    else:
        print numCol, hdrTokens

    # now we make a data matrix, the first dimension will be the column #
    print " --> first dimension of dataMatrix is %d " % numCol
    dataMatrix = [0] * numCol
    for iCol in range(numCol):
        dataMatrix[iCol] = []
    done = 0
    isBinary = 0
    numBinary = 0
    numNotB = 0
    while not done:
        bLine = fh.readline()
        try:
            if ( bLine[-1] == '\n' ): bLine = bLine[:-1]
        except:
            doNothing = 1
        ## bLine = bLine.strip()
        # each bTokens will have a feature name, followed by a list of feature
        # values
        bTokens = bLine.split('\t')
        if (len(bTokens) != numCol):
            done = 1
            print " DONE ", numCol, len(bTokens)
            print bTokens
            print " "
        else:
            # dataMatrix[0]
            for iCol in range(numCol):
                if ( bTokens[iCol] == "" ):
                    dataMatrix[iCol] += ["NA"]
                else:
                    dataMatrix[iCol] += [bTokens[iCol]]
                if (iCol > 0):
                    if (bTokens[iCol]!="NA" and bTokens[iCol]!=""):
                        if (bTokens[iCol] == "0" or bTokens[iCol] == "1"):
                            numBinary += 1
                        else:
                            numNotB += 1
                ## print "         dataMatrix[%d] has %d values " % ( iCol, len(dataMatrix[iCol]) )
    # print numBinary, numNotB
    if (numBinary > numNotB * 1000):
        isBinary = 1
    fh.close()

    print " "
    print len(dataMatrix), len(dataMatrix[0])
    # print dataMatrix[:5]
    print dataMatrix[0][:5]  # this is all of the feature IDs
    print dataMatrix[1][:5]  # this is data for the first patient
    print dataMatrix[-1][:5]  # this is data for the last patient
    print " "

    numRow = len(dataMatrix[0])
    numNA = 0
    notNA = 0
    numNAbyRow = [0] * numRow
    maxNA = 0

    # if this looks like a purely binary feature matrix, then
    # count up the number of ones and 0s ...
    if (isBinary):

        bitD = {}
        bitD["0"] = 0
        bitD["1"] = 1
        for iCol in range(1, numCol):
            for iRow in range(numRow):
                curVal = dataMatrix[iCol][iRow]
                if (curVal in bitD.keys()):
                    bitD[curVal] += 1
        print " "
        print " binary counts : ", bitD, 10000. * (float(bitD["1"]) / float(bitD["0"] + bitD["1"])), (numRow - 1), (numCol - 1)

        maxOn = 0
        maxCol = -1
        for iCol in range(1, numCol):
            numOn = 0
            featName = hdrTokens[iCol]
            if (featName.lower().find("unknown") >= 0):
                continue
            for iRow in range(numRow):
                if (dataMatrix[iCol][iRow] == "1"):
                    numOn += 1
            if (numOn > maxOn):
                maxCol = iCol
                maxOn = numOn
        print " most mutated patient : ", maxCol, hdrTokens[maxCol], maxOn
        print " "

    # if this file looks like a feature matrix with "data types",
    # then lets count up NAs by data type ...
    haveDataTypes = 0
    if (dataMatrix[0][0][1] == ':'):
        if (dataMatrix[0][0][6] == ':'):
            haveDataTypes = 1
            NAbyDataType = {}
            AVbyDataType = {}

            for iRow in range(numRow):
                dataType = dataMatrix[0][iRow][:6]
                if (dataType not in NAbyDataType.keys()):
                    NAbyDataType[dataType] = 0
                    AVbyDataType[dataType] = 0

    for iCol in range(1, numCol):
        for iRow in range(numRow):
            if (dataMatrix[iCol][iRow] == ""):
                print " ERROR ??? blank entry ??? ", iCol, iRow
                print dataMatrix[iCol - 5:iCol + 5][iRow]
                print dataMatrix[iCol][iRow - 5:iRow + 5]
                sys.exit(-1)

            if (haveDataTypes):
                dataType = dataMatrix[0][iRow][:6]

            if ((dataMatrix[iCol][iRow] == "NA") or (dataMatrix[iCol][iRow] == "na") or (dataMatrix[iCol][iRow] == "null")):
                numNA += 1
                numNAbyRow[iRow] += 1
                if (maxNA < numNAbyRow[iRow]):
                    maxNA = numNAbyRow[iRow]
                if (haveDataTypes):
                    NAbyDataType[dataType] += 1
            else:
                notNA += 1
                if (haveDataTypes):
                    AVbyDataType[dataType] += 1

    print " %d x %d " % ((numCol - 1), (numRow))
    print " total number of NA values : ", numNA, notNA
    fracNA = float(numNA) / float(numNA + notNA)
    print " fraction of NA values : %f " % fracNA

    print " "
    print "         Summary : %4d x %6d   %5.3f   %s " % ((numCol - 1), numRow, fracNA, inFilename)
    print " "

    try:
        keyList = NAbyDataType.keys()
        keyList.sort()
        for aType in keyList:
            numNA = NAbyDataType[aType]
            numAV = AVbyDataType[aType]
            numTot = numNA + numAV
            fracNA = float(numNA) / float(numTot)
            appCol = int((1. - fracNA) * float(numCol - 1))
            print "         <%s>   %6.3f : approx %4d out of %4d    %12d    %12d    %12d " % \
                (aType, fracNA, appCol, (numCol - 1), numNA, numAV, numTot)
        print " "
        print " "
        print " "
    except:
        keyList = []
        doNothing = 1

    # check some basic mutation counts ...
    print " "
    print " checking mutation counts for TP53 and TTN ... "
    aType = "B:GNAB"
    if (aType in keyList):
        for iRow in range(numRow):
            featName = dataMatrix[0][iRow]
            if (featName.startswith("B:GNAB:TP53:") or featName.startswith("B:GNAB:TTN:")):
                if (featName.find("code_potential") > 0):
                    bitD = {}
                    print iRow, featName
                    print featName
                    for iCol in range(1, numCol):
                        curVal = dataMatrix[iCol][iRow]
                        if (curVal not in bitD):
                            bitD[curVal] = 1
                        else:
                            bitD[curVal] += 1
                    print bitD
                    print " "

    # check cardinality of categorical features ...
    print " "
    print " checking for high cardinality categorical features ... "
    highCard = 0
    maxCard = 0
    maxName = "NA"
    for iRow in range(numRow):
        featName = dataMatrix[0][iRow]
        if (featName.startswith("C:")):
            uVec = []
            for iCol in range(1, numCol):
                curVal = dataMatrix[iCol][iRow]
                if ((curVal == "NA") or (curVal == "na") or
                        (curVal == "null") or (curVal == NA_VALUE)):
                    doNothing = 1
                else:
                    if (curVal not in uVec):
                        uVec += [curVal]
            if ( maxCard < len(uVec) ): 
                maxCard = len(uVec)
                maxName = featName
            if (len(uVec) > 25):
                print " WARNING ... VERY high cardinality feature !!! ", featName, len(uVec), uVec
                print " "
                highCard = 1
    print " --> highest cardinality feature found: ", maxCard, maxName

    if ( 0 ):
        if (highCard):
            print " "
            print " "
            sys.exit(-1)

    # sys.exit(-1)
    # get information about data values for each data type ...
    print " "
    print " now trying to get some information about the actual data values ... "

    # nz_byDataType = {}	# number of zeros by data type
    # nv_byDataType = {}	# number of values by data type
    # min_byDataType = {}	# smallest non-zero (abs) value by data type
    # max_byDataType = {}	# largest non-zero (abs) value by data type

    nz_byDataType = {}
    nv_byDataType = {}
    min_byDataType = {}
    max_byDataType = {}

    for iRow in range(numRow):
        for iCol in range(1, numCol):

            dataType = dataMatrix[0][iRow][:6]

            if ((dataMatrix[iCol][iRow] == "NA") or (dataMatrix[iCol][iRow] == "na") or
                    (dataMatrix[iCol][iRow] == "null") or (dataMatrix[iCol][iRow] == NA_VALUE)):
                doNothing = 1

            else:

                if (dataType not in nz_byDataType.keys()):
                    nz_byDataType[dataType] = 0
                    nv_byDataType[dataType] = 0
                    min_byDataType[dataType] = 999990
                    max_byDataType[dataType] = -999990
                else:
                    nv_byDataType[dataType] += 1

                try:
                    fVal = float(dataMatrix[iCol][iRow])
                    if (abs(fVal) < 0.0000001):
                        nz_byDataType[dataType] += 1
                    else:
                        if (fVal < min_byDataType[dataType]):
                            min_byDataType[dataType] = fVal
                        if (fVal > max_byDataType[dataType]):
                            max_byDataType[dataType] = fVal
                except:
                    doNothing = 1

    for aType in nz_byDataType.keys():
        if (min_byDataType[aType] == 999990):
            print aType, nz_byDataType[aType], nv_byDataType[aType]
        else:
            print aType, nz_byDataType[aType], nv_byDataType[aType], \
                min_byDataType[aType], max_byDataType[aType]

    numNAhist = [0] * (maxNA + 1)
    for iRow in range(numRow):
        numNAhist[numNAbyRow[iRow]] += 1

    if (not noHist):
        fh = file(histFilename, 'w')
        if ( 0 ):
            fh.write("\n\n")
            fh.write("Histogram of NA counts by feature: \n\n")
            for ii in range(maxNA + 1):
                if (numNAhist[ii] > 0): fh.write(" %4d : %8d \n" % (ii, numNAhist[ii]))
            fh.write("\n\n")
        for iRow in range(numRow):
            fh.write("%4d  %s \n" % (numNAbyRow[iRow], dataMatrix[0][iRow]))
        ## fh.write("\n\n")
        fh.close()

    sys.exit(-1)

    for iCol in range(numCol):
        numNotNull = 0
        numS = len(dataMatrix[iCol])
        uniqueList = []
        for iS in range(numS):
            if (dataMatrix[iCol][iS] != "null"):
                if ((dataMatrix[iCol][iS] != "NA") and (dataMatrix[iCol][iS] != "na") and (dataMatrix[iCol][iS] != "null")):
                    numNotNull += 1
                    if (dataMatrix[iCol][iS] not in uniqueList):
                        uniqueList += [dataMatrix[iCol][iS]]
        print " %3d %32s %3d / %3d " % (iCol, hdrTokens[iCol], numNotNull, numS)
        uniqueList.sort()
        if (len(uniqueList) < 10):
            print len(uniqueList), uniqueList
        else:
            print len(uniqueList), uniqueList[:10]



# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
