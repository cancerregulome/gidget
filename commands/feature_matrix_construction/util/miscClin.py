#!/usr/bin/env python

import numpy
import sys

import miscMath
import miscTCGA
import rand2x2

debugFlag = 0

#------------------------------------------------------------------------------


def buildHist(iVec):

    minI = 0
    maxI = max(iVec)
    numBins = maxI - minI + 1
    iHist = [0] * numBins
    for ii in range(len(iVec)):
        iHist[iVec[ii]] += 1

    return (iHist)

#------------------------------------------------------------------------------


def reMapIntegerVector(iVec):

    print " in reMapIntegerVector ... "
    print iVec
    maxI = max(iVec)

    iHist = buildHist(iVec)
    print iHist

    minHistCount = min(iHist)
    minVal = iHist.index(minHistCount)
    print minHistCount, minVal

    # if the least-used value is 0, then all other values are decremented
    if (minVal == 0):
        for ii in range(len(iVec)):
            if (iVec[ii] > 0):
                iVec[ii] -= 1
    # if the least-used value is the largest value, then it gets decremented
    elif (minVal == maxI):
        for ii in range(len(iVec)):
            if (iVec[ii] == maxI):
                iVec[ii] -= 1
    # if in between, then merge with smaller neighbor
    else:
        if (iHist[minVal - 1] <= iHist[minVal + 1]):
            for ii in range(len(iVec)):
                if (iVec[ii] >= minVal):
                    iVec[ii] -= 1
        else:
            for ii in range(len(iVec)):
                if (iVec[ii] > minVal):
                    iVec[ii] -= 1

    iHist = buildHist(iVec)
    print iHist

    return (iVec)

#------------------------------------------------------------------------------


def compressIntegerVector(iVec, skipZero=1):

    if (len(iVec) < 3):
        print " ERROR ??? empty input vector ??? "
        print iVec
        sys.exit(-1)

    # we want to make sure that the integer vectors are "compressed"
    # meaning that they don't skip any values (except perhaps 0)

    minI = min(iVec)
    if (minI > 0):
        # print " resetting minI to 0 from %d " % minI
        minI = 0

    maxI = max(iVec)
    numBins = maxI - minI + 1
    # print minI, maxI, numBins

    iHist = [0] * numBins

    nVal = len(iVec)
    for ii in range(nVal):
        try:
            iHist[iVec[ii]] += 1
        except:
            print " error in histogram ??? ", ii, iVec[ii]
            sys.exit(-1)

    # print " histogram : ", iHist

    iStart = 0
    if (skipZero):
        iStart = 1

    minHist = min(iHist[iStart:])
    # print " minHist : ", minHist

    # we only need to compress if one of the bins nas 0 counts ...
    if (minHist == 0):
        # print " need to compress discrete vector ", iHist
        mapVals = [0] * numBins
        kk = 1
        for jj in range(iStart, numBins):
            mapVals[jj] = kk
            if (iHist[jj] > 0):
                kk += 1
        # print " remapping vector : ", mapVals
        # print " old vec : ", iVec
        for ii in range(nVal):
            try:
                iVec[ii] = mapVals[iVec[ii]]
            except:
                print " ERROR mapping from %d to %d " % (iVec[ii], mapVals[iVec[ii]])
                sys.exit(-1)

        # print " new vec : ", iVec

    return (iVec)

#------------------------------------------------------------------------------

# this function discretizes a categorical vector -- NAs become 0s and all
# other values become integers > 0 ...


def discretize(keyVec, keyType, numBins=16, printFlag=0):

    nVal = len(keyVec)
    qFlag = 0

    if (keyType == "NOMINAL"):

        # for NOMINAL data, we just make a list of all the nominal
        # values and then make an integer vector where NAs become 0s
        # and all other values are replaced by their index+1

        catList = []
        for aVal in keyVec:
            if (aVal == "NA"):
                continue
            if (aVal not in catList):
                catList += [aVal]

        catList.sort()
        numVal = len(catList)

        iVec = [0] * nVal
        for ii in range(nVal):
            aVal = keyVec[ii]
            if (aVal == "NA"):
                continue
            iVec[ii] = catList.index(aVal) + 1

        if (printFlag):
            outLine = "mapping from NOMINAL to INTEGERS: "
            outLine += ' { "NA":0,'
            for ii in range(numVal):
                outLine += ' "%s":%d' % (catList[ii], ii + 1)
                if (ii < (numVal - 1)):
                    outLine += ","
                else:
                    outLine += ' }'
            print outLine

    elif (keyType == "NUMERIC"):

        # for NUMERIC data, we will bin them into numBins ( at most )

        valList = []

        tmpV = [0] * nVal
        kk = 0
        for ii in range(nVal):
            aVal = keyVec[ii]
            if (aVal != "NA"):
                if (aVal not in valList):
                    valList += [aVal]
                tmpV[kk] = aVal
                kk += 1
        tmpV = tmpV[:kk]
        tmpV.sort()

        notNAcount = kk

        valList.sort()

        # number of distinct values:
        numDiffVal = len(valList)
        # number of data points
        numNotNA = notNAcount

        # we want to make sure that the number of bins is no larger
        # than 1/qThresh the total number of data points
        # ( ie that there are at least qThresh points per bin )
        qThresh = 5
        if (numBins > (numNotNA / qThresh)):
            numBins = int((numNotNA / qThresh))

        # and also, if there are fewer distinct values, then we just
        # will not do any binning ...
        if (len(valList) < numBins):
            numBins = len(valList)
            qFlag = 0
        else:
            qFlag = 1

        iVec = [0] * nVal
        for ii in range(nVal):
            aVal = keyVec[ii]
            if (aVal == "NA"):
                continue
            if (qFlag):
                jj = tmpV.index(aVal)
                jBin = int(float(jj * numBins) / float(notNAcount)) + 1
            else:
                jBin = valList.index(aVal) + 1
            iVec[ii] = jBin

        numVal = numBins

    else:
        print " FATAL ERROR ??? ", keyType
        sys.exit(-1)

    # make sure ther are no "unused" or "missing" values ...
    iVec = compressIntegerVector(iVec)

    # print "     --> returning from discretize ", numVal, qFlag, iVec[:5], iVec[-5:]
    # print iVec

    if (debugFlag):
        if (qFlag):
            for ii in range(nVal):
                print ii, keyVec[ii], iVec[ii]

    return (iVec, numVal, qFlag)

#------------------------------------------------------------------------------
# this function removes the zeros (formerly NAs) from a pair of integer
# (discretized) vectors


def removeZeros(tmpI1, tmpI2):

    if (len(tmpI1) != len(tmpI2)):
        print " lengths differ ??? ", len(tmpI1), len(tmpI2)
        sys.exit(-1)

    newI1 = []
    newI2 = []

    na1 = 0
    na2 = 0

    for ii in range(len(tmpI1)):
        if (tmpI1[ii] == 0):
            na1 += 1
        if (tmpI2[ii] == 0):
            na2 += 1
        if (tmpI1[ii] != 0 and tmpI2[ii] != 0):
            newI1 += [tmpI1[ii] - 1]
            newI2 += [tmpI2[ii] - 1]

    if (debugFlag):
        print "     --> returning from removeZeros ", len(newI1), na1, len(newI2), na2
        if (len(newI1) == 0 or len(newI2) == 0):
            print "         ERROR ??? !!! "
            print len(tmpI1), len(tmpI2)
            print tmpI1
            print tmpI2
            sys.exit(-1)

    # if we don't have at least 5 points, bail ...
    if (len(newI1) < 5):
        return ([], [], na1, na2)

    newI1 = compressIntegerVector(newI1, 0)
    newI2 = compressIntegerVector(newI2, 0)

    return (newI1, newI2, na1, na2)

#------------------------------------------------------------------------------


def calcProbDist(iVec, iCard):

    numBins = iCard

    pX = [0.] * numBins
    for ix in range(len(iVec)):
        try:
            pX[iVec[ix]] += 1
        except:
            print " ERROR of some sort in calcProbDist ??? ", ix, iVec[ix], len(pX)
            print " was trying to set element %d in vector of length %d " % (iVec[ix], len(pX))
            print pX
            print ix
            print iVec
            sys.exit(-1)

    # check for zeros ???
    if (0):
        for ix in range(numBins):
            if (pX[ix] == 0):
                print " WARNING ... zero probability ... ", ix, pX
                # print pX
                # print iVec
                # sys.exit(-1)

    checkSum = 0.
    for ix in range(numBins):
        checkSum += pX[ix]

    if (abs(1. - checkSum) > 1.e-06):
        if (debugFlag):
            print "     normalizing pX ... ", checkSum
        for ix in range(numBins):
            try:
                pX[ix] /= checkSum
            except:
                print " error normalizing pX ?!? "
                print ix, checkSum
                print pX
                sys.exit(-1)

    if (debugFlag):
        print " P(X) : "
        aLine = ""
        for ix in range(numBins):
            aLine += " %9.6f " % pX[ix]
        print aLine

    return (pX)

#------------------------------------------------------------------------------


def calcProbDist2(iVec, iCard, jVec, jCard):

    if (len(iVec) != len(jVec)):
        print " in calcProbDist2 ... lengths do not match ... ", len(iVec), len(jVec)
        sys.exit(-1)

    pXY = [0] * iCard
    for ii in range(iCard):
        pXY[ii] = [0] * jCard

    for ii in range(len(iVec)):
        ix = iVec[ii]
        iy = jVec[ii]
        pXY[ix][iy] += 1

    checkSum = 0.
    for ix in range(iCard):
        for iy in range(jCard):
            checkSum += pXY[ix][iy]

    if (abs(1. - checkSum) > 1.e-06):
        if (debugFlag):
            print "     normalizing pXY ... ", checkSum
        for ix in range(iCard):
            for iy in range(jCard):
                pXY[ix][iy] /= checkSum

    if (debugFlag):
        print " P(X,Y) : "
        for ix in range(iCard):
            aLine = ""
            for iy in range(jCard):
                aLine += " %9.6f " % pXY[ix][iy]
            print aLine

    return (pXY)

#------------------------------------------------------------------------------


def calcProbDist3(iVec, iCard, jVec, jCard, kVec, kCard):

    if (len(iVec) != len(jVec)):
        print " in calcProbDist2 ... lengths do not match ... ", len(iVec), len(jVec)
        sys.exit(-1)
    if (len(iVec) != len(kVec)):
        print " in calcProbDist2 ... lengths do not match ... ", len(iVec), len(kVec)
        sys.exit(-1)

    iMin = min(iVec)
    iMax = max(iVec)

    if (iMin != min(jVec)):
        print " in calcProbDist2 ... min values do not match ... ", min(iVec), min(jVec)
        sys.exit(-1)
    if (iMax != max(jVec)):
        print " in calcProbDist2 ... max values do not match ... ", max(iVec), max(jVec)
        sys.exit(-1)
    if (iMin != min(kVec)):
        print " in calcProbDist2 ... min values do not match ... ", min(iVec), min(kVec)
        sys.exit(-1)
    if (iMax != max(kVec)):
        print " in calcProbDist2 ... max values do not match ... ", max(iVec), max(kVec)
        sys.exit(-1)

    pXYZ = [0] * iCard
    for ii in range(iCard):
        pXYZ[ii] = [0] * jCard
        for jj in range(jCard):
            pXYZ[ii][jj] = [0.] * kCard

    for ii in range(len(iVec)):
        ix = iVec[ii]
        iy = jVec[ii]
        iz = kVec[ii]
        pXYZ[ix][iy][iz] += 1

    checkSum = 0.
    for ix in range(iCard):
        for iy in range(jCard):
            for iz in range(kCard):
                checkSum += pXYZ[ix][iy][iz]

    if (abs(1. - checkSum) > 1.e-06):
        if (debugFlag):
            print "     normalizing pXYZ ... ", checkSum
        for ix in range(iCard):
            for iy in range(jCard):
                for iz in range(kCard):
                    pXYZ[ix][iy][iz] /= checkSum

    if (debugFlag):
        print " P(X,Y,Z) : "
        for ix in range(iCard):
            for iy in range(jCard):
                aLine = " ix=%2d  iy=%2d  :  " % (ix, iy)
                for iz in range(kCard):
                    aLine += " %9.6f " % pXYZ[ix][iy][iz]
                print aLine

    return (pXYZ)

#------------------------------------------------------------------------------


def calcEntropy(iVec, iCard):

    pX = calcProbDist(iVec, iCard)
    numBins = iCard

    H = 0.
    for ix in range(numBins):
        # if the probability is zero, then skip this bin ...
        if (pX[ix] < 1.e-24):
            continue
        H -= (pX[ix] * miscMath.log2(pX[ix]))

    maxH = -1. * miscMath.log2((1. / float(numBins)))

    return (H, maxH)

#------------------------------------------------------------------------------


def calcCondEntropy(xVec, xCard, yVec, yCard):

    pX = calcProbDist(xVec, xCard)
    pY = calcProbDist(yVec, yCard)

    # print " in calcCondEntropy : "
    # print len(pX), pX
    # print len(pY), pY

    pXY = calcProbDist2(xVec, xCard, yVec, yCard)

    HofXgivenY = 0.
    for ix in range(len(pX)):
        for iy in range(len(pY)):
            # if the joint probability is zero, then skip this [ix,iy] bin ...
            if (pXY[ix][iy] < 1.e-24):
                continue
            try:
                HofXgivenY -= pXY[ix][iy] * \
                    miscMath.log2(pXY[ix][iy] / pY[iy])
            except:
                print " ERROR in calcCondEntropy ... "
                print ix, iy, pX[ix], pY[iy], pXY[ix][iy]
                sys.exit(-1)

    return (HofXgivenY)

#------------------------------------------------------------------------------


def calcCondEntropy2(xVec, xCard, yVec, yCard, zVec, zCard):

    pX = calcProbDist(xVec, xCard)
    pY = calcProbDist(yVec, yCard)
    pZ = calcProbDist(zVec, zCard)

    pYZ = calcProbDist2(yVec, yCard, zVec, zCard)
    pXYZ = calcProbDist3(xVec, xCard, yVec, yCard, zVec, zCard)

    HofXgivenYZ = 0.
    for ix in range(len(pX)):
        for iy in range(len(pY)):
            for iz in range(len(pZ)):
                # if the joint probability is zero, then skip this [ix,iy,iz]
                # bin ...
                if (pXYZ[ix][iy][iz] < 1.e-24):
                    continue
                try:
                    HofXgivenYZ -= pXYZ[ix][iy][iz] * \
                        miscMath.log2(pXYZ[ix][iy][iz] / pYZ[iy][iz])
                except:
                    print " ERROR in calcCondEntropy2 ... "
                    print ix, iy, iz, pX[ix], pY[iy], pZ[iz], pYZ[iy][iz], pXYZ[ix][iy][iz]
                    sys.exit(-1)

    return (HofXgivenYZ)

#------------------------------------------------------------------------------


def check_barcodes(aDict):

    print " in miscClin.check_barcodes "

    allKeys = aDict.keys()
    allKeys.sort()
    aKey = allKeys[0]
    numClin = len(aDict[aKey])
    ## print numClin, len(allKeys)
    ## print aKey
    ## print allKeys

    for aKey in allKeys:
        if (aKey.lower().find("bcr_patient_barcode")>=0):
            for ii in range(numClin):
                barcode = aDict[aKey][ii]
                if (len(barcode) == 12):
                    aDict[aKey][ii] = miscTCGA.get_tumor_barcode(barcode)

    return (aDict)

#------------------------------------------------------------------------------


def lookAtClinDict(allClinDict):

    print " "
    print " taking a look at clinical data dictionary : "

    allKeys = allClinDict.keys()
    if (len(allKeys) < 1):
        return

    allKeys.sort()
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    # if the data consists of strings, then force everything to lower case
    # to try to have things be consistent ...
    for ii in range(len(allKeys)):
        aKey = allKeys[ii]
        allStr = 1
        allNum = 1
        if (len(allClinDict[aKey]) == 0):
            continue
        for kk in range(numClin):
            if (allClinDict[aKey][kk] != "NA"):
                try:
                    testF = float(allClinDict[aKey][kk])
                    allStr = 0
                except:
                    allNum = 0
        print " Key <%s> %d %d " % (aKey, allStr, allNum)

    # continue ...

    naCounts = [0] * len(allKeys)
    otherCounts = [0] * len(allKeys)
    for ii in range(len(allKeys)):
        aKey = allKeys[ii]
        numNA = 0

        if (0):
            if (len(allClinDict[aKey]) != numClin):
                print " ERROR ??? ", aKey, len(allClinDict[aKey]), numClin
                sys.exit(-1)
        if (1):
            if (len(allClinDict[aKey]) != numClin):
                naCounts[ii] = -1
                otherCounts[ii] = {}
                continue

        for kk in range(numClin):
            if (allClinDict[aKey][kk] == "NA"):
                numNA += 1
        naCounts[ii] = numNA
        tmpKey = aKey
        if (len(tmpKey) > 50):
            tmpKey = tmpKey[:47]
            tmpKey += "..."
        outLine = ("%3d %50s %5d/%5d" % (ii, tmpKey, numNA, numClin))
        otherValues = []
        otherCounts[ii] = {}
        for kk in range(numClin):
            zValue = allClinDict[aKey][kk]
            if (zValue != "NA"):
                if (zValue not in otherValues):
                    otherValues += [zValue]
                    otherCounts[ii][zValue] = 0
                otherCounts[ii][zValue] += 1
        otherValues.sort()
        if (len(otherValues) < 5):
            ## outLine += "        "
            ## outLine += str ( otherValues )
            outLine += "    "
            outLine += str(otherCounts[ii])
        else:
            outLine += "    "
            outLine += str(otherValues[:3])
            outLine += " ... "
            outLine += str(otherValues[-3:])
        print outLine

    return (naCounts, otherCounts)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkDiscVec(iVec):

    # print " in checkDiscVec "
    minI = min(iVec)
    maxI = max(iVec)

    nUse = 0

    for ii in range(minI, maxI + 1):
        try:
            jj = iVec.index(ii)
        except:
            nUse += 1
            print " WARNING in checkDiscVec ... unused value %d " % ii
            print iVec

    return (nUse)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def filterClinDict(allClinDict,
                   categorical_naFracThresh=0.75,
                   numerical_naFracThresh=0.75,
                   classSize_minFracThresh=0.03,
                   classSize_maxFracThresh=0.97):

    print " "
    print " "
    print " in filterClinDict ... ", categorical_naFracThresh, numerical_naFracThresh, classSize_minFracThresh
    print " "

    allKeys = allClinDict.keys()
    allKeys.sort()
    numKeys = len(allKeys)
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    keepFlags = [0] * numKeys
    keyTypes = [0] * numKeys
    nCounts = [0] * numKeys
    naCounts = [0] * numKeys
    cardCounts = [0] * numKeys
    labelLists = [0] * numKeys
    labelCounts = [0] * numKeys

    allNAfrac = []

    numToss = 0
    for ii in range(numKeys):
        aKey = allKeys[ii]
        tossString = " "

        if (aKey.lower().find("bcr_patient_barcode")>=0):
            keepFlags[ii] = 1
            continue

        # a few HACKs ;-)
        if (aKey == "bcr"):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey == "V1"):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("barcode") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("_dcc_") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("batch") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey == "CDE.DxAge"):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("totaldose") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("administration") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("drugname") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("patient.drugs.drug-") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("patient.surgeries.surgery-") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("therapyclass") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("missingctxCde") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        if (aKey.find("radiationtype") >= 0):
            print " HACK : tossing this key <%s> " % aKey
            continue
        ## if (aKey.find("diagnosismethod") >= 0):
        ##     print " HACK : tossing this key <%s> " % aKey
        ##     continue
        ## if (aKey.find("diagnosis_method") >= 0):
        ##     print " HACK : tossing this key <%s> " % aKey
        ##     continue

        tmpKey = aKey
        if (len(tmpKey) > 50):
            tmpKey = tmpKey[:47]
            tmpKey += "..."
        numNA = naCounts[ii]
        outLine = ("%3d %50s %5d" % (ii, tmpKey, numNA))
        outLine += "    "

        # keyType is either NUMERIC or NOMINAL (arff terms)
        # nCount is the total # of clinical samples in the dictionary
        # nNA is the number of clinical samples with NA values
        # nCard is the # of classes (cardinality) for NOMINAL data
        # labelLists is the list of class labels for NOMINAL data (for NUMERIC data, it is a list of all possible values)
        # labelCounts is the number of counts associated with each label in
        # labelLists (for NUMERIC data it is [])
        (keyTypes[ii], nCounts[ii], naCounts[ii], cardCounts[ii],
         labelLists[ii], labelCounts[ii]) = lookAtKey(allClinDict[aKey])

        naFrac = float(naCounts[ii]) / float(nCounts[ii])
        allNAfrac += [naFrac]

        # we test the NA fraction, as well as the min/max class sizes for
        # NOMINAL data ...

        if (keyTypes[ii] == "NOMINAL"):
            if (naFrac <= categorical_naFracThresh):
                keepFlags[ii] = 1
            else:
                tossString += " naFrac = %.3f > %.3f " % (naFrac,
                                                          categorical_naFracThresh)
            minClassSize = min(labelCounts[ii])
            maxClassSize = max(labelCounts[ii])
            minFrac = float(minClassSize) / float(nCounts[ii] - naCounts[ii])
            maxFrac = float(maxClassSize) / float(nCounts[ii] - naCounts[ii])
            if (minFrac < classSize_minFracThresh):
                keepFlags[ii] = 0
                tossString += " minFrac = %.3f < %.3f " % (minFrac,
                                                           classSize_minFracThresh)

        if (keyTypes[ii] == "NUMERIC"):
            if (naFrac <= numerical_naFracThresh):
                keepFlags[ii] = 1
            else:
                tossString += " naFrac = %.3f > %.3f " % (naFrac,
                                                          numerical_naFracThresh)
            # if ( keepFlags[ii] ):
            # print " DEFAULT IS TO KEEP ... MAYBE NOT ??? look at entropy ???
            # "

        if (1):
            print outLine
            print keyTypes[ii], nCounts[ii], naCounts[ii], cardCounts[ii], labelLists[ii], labelCounts[ii]
            print " NA fraction : ", naFrac, categorical_naFracThresh
            if (keyTypes[ii] == "NOMINAL"):
                print " range of class sizes : ", minClassSize, maxClassSize, len(labelCounts[ii])
                print " range of class sizes as fractions : ", minFrac, maxFrac

        if (not keepFlags[ii]):
            print " NOT KEEPING THIS FEATURE ... ", tmpKey, tossString
            numToss += 1

        print "\n\n"

    print "\n\n"
    print " --> %d features being tossed due to counts, NAs, etc " % numToss

    # are there any remaining fields which are (nearly?) identical?
    allKeys = allClinDict.keys()
    allKeys.sort()
    numKeys = len(allKeys)

    if (1):
        print " "
        print " LOOP over all %d keys ... computing entropy to see if any can/should be removed ... " % numKeys
        print " "

        for ii in range(numKeys):
            # if ( keyTypes[ii] == "NUMERIC" ): continue
            if (not keepFlags[ii]):
                continue
            aKey = allKeys[ii]
            if (aKey.lower().find("bcr_patient_barcode")>=0):
                continue

            print " "
            print "     ******************************* "
            print "     in entropy computation loop ... ", ii, numKeys

            for jj in range(ii + 1, numKeys):
                # if ( keyTypes[jj] == "NUMERIC" ): continue
                if (not keepFlags[jj]):
                    continue
                bKey = allKeys[jj]
                if (bKey.lower().find("bcr_patient_barcode")>=0):
                    continue

                # print " (a) COMPARING : ", ii, numKeys, aKey, bKey
                # print keyTypes[ii], labelLists[ii], labelCounts[ii]
                # print keyTypes[jj], labelLists[jj], labelCounts[jj]

                (tmpI1, card1, qFlag1) = discretize(
                    allClinDict[aKey], keyTypes[ii])
                (tmpI2, card2, qFlag2) = discretize(
                    allClinDict[bKey], keyTypes[jj])

                # to be identical, we assume they must have the same cardinality ...
                # if ( card1 != card2 ): continue

                # we don't want to compare NAs ...
                # ( note that this function also then shifts all values down
                # by 1 so that the value 0 is now used for non-missing values )
                (tmpI1, tmpI2, na1, na2) = removeZeros(tmpI1, tmpI2)

                if (len(tmpI1) == 0 or len(tmpI2) == 0):
                    continue
                if (max(tmpI1) == 0 or max(tmpI2) == 0):
                    continue

                # check the two vectors ... there shouldn't be any unused
                # values ...
                nUse1 = checkDiscVec(tmpI1)
                nUse2 = checkDiscVec(tmpI2)
                if ((nUse1 + nUse2) > 0):
                    print " (a) empty bins after discretization ??? error !!! ??? "
                    if (nUse1 > 0):
                        print " tmpI1 : ", tmpI1
                    if (nUse2 > 0):
                        print " tmpI2 : ", tmpI2
                    sys.exit(-1)

                if (len(tmpI1) == 0 or len(tmpI2) == 0):
                    continue
                if (max(tmpI1) == 0 or max(tmpI2) == 0):
                    continue
                # print " B "
                # print tmpI1
                # print tmpI2

                # compute entropy, conditional entropy ...
                (HofX, maxHX) = calcEntropy(tmpI1, card1)
                (HofY, maxHY) = calcEntropy(tmpI2, card2)
                # print aKey, bKey, HofX, maxHX, HofY, maxHY
                HofXgivenY = calcCondEntropy(tmpI1, card1, tmpI2, card2)
                xyMI = HofX - HofXgivenY
                HofYgivenX = HofY - xyMI

                if (xyMI > (HofX) / 2.):
                    print " "
                    print " significant mutual information between <%s> and <%s> (%d) " % (aKey, bKey, len(tmpI1))
                    print " ENTROPY : H(X)=%4.2f  H(Y)=%4.2f  H(X|Y)=%4.2f  MI(X;Y)=%4.2f <%s> <%s> " % (HofX, HofY, HofXgivenY, xyMI, aKey, bKey)
                # print " "
                # sys.exit(-1)

                if (HofX > 0.05):
                    if (abs(HofX - HofY) < 0.01):
                        if (HofXgivenY < 0.01):
                            if (na1 == na2):
                                print " --> removing %s because %s has the same information (%f,%f,%f) (%d,%d) " % (bKey, aKey, HofX, HofXgivenY, xyMI, na2, na1)
                                keepFlags[jj] = 0
                            else:
                                print " --> would have removed %s because %s has the same information, but the number of NAs is not the same (%f,%f,%f) (%d,%d) " % \
                                    (bKey, aKey, HofX,
                                     HofXgivenY, xyMI, na2, na1)
                                # check to see if they are identical when not
                                # NA ... ??? HERE
                                allSame = 1
                                for oo in range(len(allClinDict[aKey])):
                                    if (allClinDict[aKey][oo] != "NA"):
                                        if (allClinDict[bKey][oo] != "NA"):
                                            if (allClinDict[aKey][oo] != allClinDict[bKey][oo]):
                                                allSame = 0
                                if (allSame):
                                    if (na1 > na2):
                                        print " --> removing %s because %s has the same information (%f,%f,%f) (%d,%d) " % (aKey, bKey, HofX, HofXgivenY, xyMI, na1, na2)
                                        keepFlags[ii] = 0
                                    else:
                                        print " --> removing %s because %s has the same information (%f,%f,%f) (%d,%d) " % (bKey, aKey, HofX, HofXgivenY, xyMI, na2, na1)
                                        keepFlags[jj] = 0

    # now we remove all of the features that we decided not to keep ...
    print " "
    print " now removing selected keys based on entropy calculations and other information ... "
    numDel = 0
    for ii in range(numKeys):
        aKey = allKeys[ii]
        if (not keepFlags[ii]):
            # HACK !!!
            if (aKey.find("MSI") > 0):
                numDel += 0
            else:
                print " deleting key <%s> " % aKey
                del allClinDict[aKey]
                numDel += 1

    allKeys = allClinDict.keys()
    allKeys.sort()
    numKeys = len(allKeys)
    if (numDel > 0):
        print " --> number of keys deleted due to entropy calculations : ", numDel
        print " --> final number of keys : ", numKeys

    print "\n DONE \n"
    # sys.exit(-1)

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def nospace(aString):
    bString = ''
    for ii in range(len(aString)):
        if (aString[ii] == ' '):
            bString += '_'
        else:
            bString += aString[ii]
    return (bString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def chooseWeakestLink(ii, jj, kk, pmiMatrix):

    # ii index refers to node A
    # jj index refers to node B
    # kk index refers to node C
    miAB = pmiMatrix[ii][jj]
    miBC = pmiMatrix[jj][kk]
    miAC = pmiMatrix[ii][kk]

    if (miAB < min(miBC, miAC)):
        return (ii, jj)
    if (miBC < min(miAB, miAC)):
        return (jj, kk)
    if (miAC < min(miAB, miBC)):
        return (ii, kk)

    print " not removing any edge !!! ", ii, jj, kk

    return (-1, -1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def sketchyDist(tmpI):

    minI = min(tmpI)
    maxI = max(tmpI)
    numBins = maxI - minI + 1

    tmpJ = [0] * numBins
    sumJ = 0
    for ii in range(len(tmpI)):
        jj = tmpI[ii] - minI
        # print " ii=%3d jj=%3d " % ( ii, jj )
        tmpJ[jj] += 1
        sumJ += 1

    # print " tmpJ before sorting : "
    # print tmpJ
    tmpJ.sort()

    # set a minimum threshold on the # of samples in the smallest bin ...
    minCount = (sumJ / len(tmpJ)) / 17
    if (tmpJ[0] < minCount):
        # print " looks sketchy ... minCount=%d  sumJ=%d  len(tmpJ)=%d  minI=%d  maxI=%d  numBins=%d " % \
        ##	( minCount, sumJ, len(tmpJ), minI, maxI, numBins )
        # print tmpJ
        # print tmpI
        return (1)
    else:
        return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def computeRhos(tmpA, typeA, tmpB, typeB):

    numNotNA = 0
    for ii in range(len(tmpA)):
        if (tmpA[ii] != "NA"):
            if (tmpB[ii] != "NA"):
                numNotNA += 1

    print " in computeRhos ... ", typeA, typeB

    # print typeA, typeB
    # print tmpA
    # print tmpB
    # print ' numNotNA : ', numNotNA, len(tmpA), len(tmpB)

    if (typeA == "NOMINAL"):
        aList = []
        for ii in range(len(tmpA)):
            if (tmpA[ii] != "NA"):
                if (tmpB[ii] != "NA"):
                    if (tmpA[ii] not in aList):
                        aList += [tmpA[ii]]
        aList.sort()
        # print ' aList : ', aList

    if (typeB == "NOMINAL"):
        bList = []
        for ii in range(len(tmpA)):
            if (tmpA[ii] != "NA"):
                if (tmpB[ii] != "NA"):
                    # print ii, tmpB[ii], bList
                    if (tmpB[ii] not in bList):
                        bList += [tmpB[ii]]
        bList.sort()
        # print ' bList : ', bList

    tmpV1 = numpy.zeros(numNotNA)
    tmpV2 = numpy.zeros(numNotNA)
    kk = 0
    for ii in range(len(tmpA)):
        if (tmpA[ii] != "NA"):
            if (tmpB[ii] != "NA"):
                if (typeA == "NOMINAL"):
                    tmpV1[kk] = aList.index(tmpA[ii])
                else:
                    tmpV1[kk] = tmpA[ii]
                if (typeB == "NOMINAL"):
                    tmpV2[kk] = bList.index(tmpB[ii])
                else:
                    tmpV2[kk] = tmpB[ii]
                kk += 1

    print " computing correlations ... ", len(tmpV1)
    print tmpV1[:5], tmpV1[-5:]
    print tmpV2[:5], tmpV2[-5:]
    rhoP = miscMath.PearsonCorr(tmpV1, tmpV2)
    rhoS = miscMath.SpearmanCorr(tmpV1, tmpV2)
    print " --> rhoP=%f   rhoS=%f " % (rhoP, rhoS)

    # print tmpV1
    # print tmpV2
    # print rhoP, rhoS

    return (rhoP, rhoS)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def pairwiseMI(allClinDict, outFilename=''):

    print " "
    print " "
    print " in pairwiseMI ... "
    print " "

    allKeys = allClinDict.keys()
    allKeys.sort()
    numKeys = len(allKeys)
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    keyTypes = [0] * numKeys
    nCounts = [0] * numKeys
    naCounts = [0] * numKeys
    cardCounts = [0] * numKeys
    labelLists = [0] * numKeys
    labelCounts = [0] * numKeys

    # first we just need some information about each key ...
    for ii in range(numKeys):
        aKey = allKeys[ii]
        if (aKey.lower().find("bcr_patient_barcode")>=0):
            continue
        # keyType is either NUMERIC or NOMINAL (arff terms)
        # nCount is the total # of clinical samples in the dictionary
        # nNA is the number of clinical samples with NA values
        # nCard is the # of classes (cardinality) for NOMINAL data
        # labelLists is the list of class labels for NOMINAL data (for NUMERIC data, it is a list of all possible values)
        # labelCounts is the number of counts associated with each label in
        # labelLists (for NUMERIC data it is [])
        (keyTypes[ii], nCounts[ii], naCounts[ii], cardCounts[ii],
         labelLists[ii], labelCounts[ii]) = lookAtKey(allClinDict[aKey])

        # take a look at how nominal features will be discretized ...
        print " "
        print aKey, keyTypes[ii]
        if (keyTypes[ii] == "NOMINAL"):
            (tmpI1, card1, qFlag1) = discretize(
                allClinDict[aKey], keyTypes[ii], 16, 1)

    # sys.exit(-1)

    if (outFilename == ''):
        writeFlag = 0
    else:
        fh = file(outFilename, 'w')
        writeFlag = 1

    print " "
    print " building an MI network over %d keys " % (numKeys - 1)
    print " "

    pmiMatrix = [0] * numKeys
    for ii in range(numKeys):
        pmiMatrix[ii] = [0] * numKeys

    for ii in range(numKeys):
        aKey = allKeys[ii]
        if (aKey.lower().find("bcr_patient_barcode")>=0):
            continue

        print " "
        print " ----------------------------------------------------------------- "
        print " LOOP #1 over %d keys ... %d <%s> " % (numKeys, ii, aKey)

        # HACK !!!
        # if ( aKey != "age_at_initial_pathologic_diagnosis" ): continue
        # if ( aKey != "CIN_bit" ): continue
        # if ( aKey.find("MSI") < 0 ): continue
        # if ( aKey.find("CNVR") > 0 ): continue
        # if ( aKey.find("SAMP")<0 and aKey.find("CLIN")<0 ): continue

        # HACK
        # if ( aKey < "N:CNVR:14q32.32_GisticROI_d:chr14:102454171:102471808:"
        # ): continue

        for jj in range(ii + 1, numKeys):
            bKey = allKeys[jj]
            if (bKey.lower().find("bcr_patient_barcode")>=0):
                continue

            print " "
            print " LOOP #2 over %d keys ... %d <%s> " % (numKeys, jj, bKey)

            # HACK !!!
            # if ( bKey != "age_at_initial_pathologic_diagnosis" ): continue
            # if ( aKey!="tumor_stage"  and  bKey!="tumor_stage" ): continue
            # if ( bKey.find("MSI") < 0 ): continue
            # if ( bKey.find("SAMP")<0 and bKey.find("CLIN")<0 ): continue
            # if ( bKey.find("CNVR") > 0 ): continue
            # if ( aKey.find("CIN")<0 and bKey.find("CIN")<0 ): continue

            # don't bother comparing indicator variables with the
            # source categorical variable ...
            if (0):
                aTest = "|" + aKey + ")"
                if (bKey.find(aTest) >= 0):
                    continue
                bTest = "|" + bKey + ")"
                if (aKey.find(bTest) >= 0):
                    continue

            # don't bother with the very high cardinality clusterings ...
            if (0):
                if (aKey.find("_K5") > 0):
                    continue
                if (aKey.find("_K6") > 0):
                    continue
                if (aKey.find("_K7") > 0):
                    continue
                if (aKey.find("_K8") > 0):
                    continue
                if (bKey.find("_K5") > 0):
                    continue
                if (bKey.find("_K6") > 0):
                    continue
                if (bKey.find("_K7") > 0):
                    continue
                if (bKey.find("_K8") > 0):
                    continue

            print " "
            print " "
            print " (b) COMPARING : ", aKey, bKey

            # try to decide if these two are essentially the same anyway ...
            skipComp = 0

            if (1):
                if (not aKey.lower().startswith("amp_")):
                    if (not aKey.lower().startswith("del_")):
                        if ((aKey.lower().find('_')) > 0):
                            if ((bKey.find('_')) > 0):
                                ia = aKey.find('_')
                                ib = bKey.find('_')
                                if (aKey[:ia].lower() == bKey[:ib].lower()):
                                    skipComp = 1

            if (1):
                if (aKey.lower().startswith("amp_")):
                    if (bKey.lower().startswith("amp_")):
                        skipComp = 1
                if (aKey.lower().startswith("del_")):
                    if (bKey.lower().startswith("del_")):
                        skipComp = 1

            if (1):
                if (aKey.lower().startswith("i(")):
                    aTokens = aKey.split('|')
                    aPart = aTokens[1][:-1]
                else:
                    aPart = aKey
                if (bKey.lower().startswith("i(")):
                    bTokens = bKey.split('|')
                    bPart = bTokens[1][:-1]
                else:
                    bPart = bKey
                if (aPart.lower() == bPart.lower()):
                    skipComp = 1

            if (skipComp):
                print " skipping further analysis of this pair they seem to be too similar ... ", aKey, bKey
                continue

            # print keyTypes[ii], labelLists[ii], labelCounts[ii]
            # print keyTypes[jj], labelLists[jj], labelCounts[jj]

            (tmpI1, card1, qFlag1) = discretize(
                allClinDict[aKey], keyTypes[ii])
            (tmpI2, card2, qFlag2) = discretize(
                allClinDict[bKey], keyTypes[jj])

            (rhoP, rhoS) = computeRhos(
                allClinDict[aKey], keyTypes[ii], allClinDict[bKey], keyTypes[jj])

            # we don't want to compare NAs ...
            (tmpI1, tmpI2, na1, na2) = removeZeros(tmpI1, tmpI2)

            if (len(tmpI1) == 0 or len(tmpI2) == 0):
                continue
            if (max(tmpI1) == 0 or max(tmpI2) == 0):
                continue
            # print " A "
            # print tmpI1
            # print tmpI2

            # check the two vectors ... there shouldn't be any unused values
            # ...
            nUse1 = checkDiscVec(tmpI1)
            nUse2 = checkDiscVec(tmpI2)
            if ((nUse1 + nUse2) > 0):
                print " (b) empty bins after discretization ??? error !!! ??? "
                if (nUse1 > 0):
                    print " tmpI1 : ", tmpI1
                if (nUse2 > 0):
                    print " tmpI2 : ", tmpI2
                sys.exit(-1)

            # check if the distributions seem too skewed ...
            if (sketchyDist(tmpI1) or sketchyDist(tmpI2)):
                print " potentially sketchy data ... we may want to skip further comparison of this pair ... "
                print keyTypes[ii], labelLists[ii], labelCounts[ii]
                print keyTypes[jj], labelLists[jj], labelCounts[jj]

                if (sketchyDist(tmpI1) and keyTypes[ii] == "NUMERIC"):
                    while (sketchyDist(tmpI1) and (len(tmpI1) > 2)):
                        tmpI1 = reMapIntegerVector(tmpI1)

                if (sketchyDist(tmpI2) and keyTypes[jj] == "NUMERIC"):
                    while (sketchyDist(tmpI2) and (len(tmpI2) > 2)):
                        tmpI2 = reMapIntegerVector(tmpI2)

                if (sketchyDist(tmpI1) or sketchyDist(tmpI2)):
                    print " skipping further analysis of this pair the data seems a bit sketchy ... "
                    print sketchyDist(tmpI1), keyTypes[ii], labelLists[ii], labelCounts[ii]
                    print sketchyDist(tmpI2), keyTypes[jj], labelLists[jj], labelCounts[jj]
                    # sys.exit(-1)
                    continue

            # compute entropy, conditional entropy ...
            (HofX, maxHX) = calcEntropy(tmpI1, card1)
            (HofY, maxHY) = calcEntropy(tmpI2, card2)
            HofXgivenY = calcCondEntropy(tmpI1, card1, tmpI2, card2)
            xyMI = HofX - HofXgivenY
            HofYgivenX = HofY - xyMI

            # if one of the variables (or both) was discretized, then maybe we should
            # try a few different levels of discretization to see if it affects
            # the MI ???
            if (1):
                if ((qFlag1 + qFlag2) > 0):

                    if (aKey.lower().startswith("i(") and bKey.lower().startswith("i(")):
                        aTokens = aKey.split('|')
                        bTokens = bKey.split('|')
                        if (aTokens[1] == bTokens[1]):
                            print " it does not make sense to compute a p-value for these ... "
                            continue

                    best_MI = 0.
                    tryN = [2, 4, 8, 12, 16, 24, 32,
                            48, 64, 96, 128, 192, 256]
                    tryN = [2, 3, 5, 7, 11, 15, 25, 31, 41, 51, 61]
                    tryN = [2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
                    try1 = [-1]
                    try2 = [-1]
                    if (qFlag1):
                        try1 = tryN
                    if (qFlag2):
                        try2 = tryN

                    stop1 = 0
                    stop2 = 0

                    for i1 in try1:
                        for i2 in try2:

                            if (i1 > 0):
                                if (len(allClinDict[aKey]) < i1):
                                    continue

                            if (i2 > 0):
                                if (len(allClinDict[bKey]) < i2):
                                    continue

                            # these flags get set if we should give up on trying higher
                            # values of i1 or i2 ...
                            if (stop1):
                                continue
                            if (stop2):
                                continue

                            # print " trying different numbers of bins ... ",
                            # i1, card1, i2, card2

                            if (i1 > 0):
                                (a_tmpI1, a_card1, a_qFlag1) = discretize(
                                    allClinDict[aKey], keyTypes[ii], i1)
                            else:
                                (a_tmpI1, a_card1, a_qFlag1) = discretize(
                                    allClinDict[aKey], keyTypes[ii])
                            if (i2 > 0):
                                (a_tmpI2, a_card2, a_qFlag2) = discretize(
                                    allClinDict[bKey], keyTypes[jj], i2)
                            else:
                                (a_tmpI2, a_card2, a_qFlag2) = discretize(
                                    allClinDict[bKey], keyTypes[jj])
                            (a_tmpI1, a_tmpI2, a_na1,
                             a_na2) = removeZeros(a_tmpI1, a_tmpI2)

                            # if the discretization results in any unused bins, then
                            # we assume that that is too many levels of
                            # discretization ...
                            stop1 = 0
                            stop2 = 0
                            if (checkDiscVec(a_tmpI1) > 0):
                                stop1 = 1
                                continue
                            if (checkDiscVec(a_tmpI2) > 0):
                                stop2 = 1
                                continue

                            (a_HofX, a_maxHX) = calcEntropy(
                                a_tmpI1, a_card1)
                            (a_HofY, a_maxHY) = calcEntropy(
                                a_tmpI2, a_card2)
                            a_HofXgivenY = calcCondEntropy(
                                a_tmpI1, a_card1, a_tmpI2, a_card2)
                            a_xyMI = a_HofX - a_HofXgivenY
                            a_HofYgivenX = a_HofY - a_xyMI

                            # print "     --> ", a_xyMI
                            if (best_MI < a_xyMI):
                                best_MI = a_xyMI

                                # note that if discretize() changes the number of bins, it will return
                                # the actual value used in the "card" field ...
                                if (i1 > 0):
                                    keep1 = a_card1
                                else:
                                    keep1 = i1

                                if (i2 > 0):
                                    keep2 = a_card2
                                else:
                                    keep2 = i2

                                ## keep1 = i1
                                ## keep2 = i2
                                # print "         --> best so far ", i1, i2,
                                # best_MI

                                tmpI1 = a_tmpI1
                                tmpI2 = a_tmpI2

                                HofX = a_HofX
                                maxHX = a_maxHX
                                HofY = a_HofY
                                maxHY = a_maxHY
                                HofXgivenY = a_HofXgivenY
                                xyMI = a_xyMI
                                HofYgivenX = HofY - xyMI

                    print "     --> last best quantization combination : %4d %4d %6.3f " % (keep1, keep2, best_MI)
                    # sys.exit(-1)

            # here we could try to compute significance for the MI and rho values ...
            # ( although for now we will do this only for 2x2 comparisons )
            if (card1 == 2 and card2 == 2):
                n00 = 0
                n01 = 0
                n10 = 0
                n11 = 0
                for kk in range(len(tmpI1)):
                    if (tmpI1[kk] == 0):
                        if (tmpI2[kk] == 0):
                            n00 += 1
                        else:
                            n01 += 1
                    else:
                        if (tmpI2[kk] == 0):
                            n10 += 1
                        else:
                            n11 += 1
                print " CALLING RAND2X2 ... ", n00, n01, n10, n11, xyMI, rhoP
                (p_MI, p_rho) = rand2x2.getSignif(n00,
                                                  n01, n10, n11, xyMI, rhoP, 100)
                print p_MI, p_rho

                if ((p_MI + p_rho) < 0.05):
                    print "     --> REFINING ... "
                    (p_MI, p_rho) = rand2x2.getSignif(n00,
                                                      n01, n10, n11, xyMI, rhoP, 1000)
                    print p_MI, p_rho

                if ((p_MI + p_rho) < 0.005):
                    print "         --> REFINING "
                    (p_MI, p_rho) = rand2x2.getSignif(n00,
                                                      n01, n10, n11, xyMI, rhoP, 10000)
                    print p_MI, p_rho

                if ((p_MI + p_rho) < -0.0005):
                    print "         --> REFINING "
                    (p_MI, p_rho) = rand2x2.getSignif(n00,
                                                      n01, n10, n11, xyMI, rhoP, 100000)
                    print p_MI, p_rho

            else:

                if (0):
                    print " not trying to compute significance ... "
                    p_MI = -1
                    p_rho = -1
                else:
                    print " CALLING PERMUTATIONTEST ... ", len(tmpI1), xyMI, rhoP
                    (p_MI, p_rho) = rand2x2.permutationTest(
                        tmpI1, tmpI2, xyMI, rhoP, 100)

                if ((p_MI + p_rho) < 0.05):
                    print "     --> REFINING ... "
                    (p_MI, p_rho) = rand2x2.permutationTest(
                        tmpI1, tmpI2, xyMI, rhoP, 1000)
                    print p_MI, p_rho

                if ((p_MI + p_rho) < 0.005):
                    print "         --> REFINING "
                    (p_MI, p_rho) = rand2x2.permutationTest(
                        tmpI1, tmpI2, xyMI, rhoP, 10000)
                    print p_MI, p_rho

                if ((p_MI + p_rho) < -0.0005):
                    print "         --> REFINING "
                    (p_MI, p_rho) = rand2x2.permutationTest(
                        tmpI1, tmpI2, xyMI, rhoP, 100000)
                    print p_MI, p_rho

            if (xyMI > 0.0):
                miFrac = xyMI / min(HofX, HofY)
                print " %4.2f  ENTROPY : H(X)=%4.2f (%4.2f)  H(Y)=%4.2f (%4.2f)  H(X|Y)=%4.2f (%4.2f)  MI(X;Y)=%4.2f (%4.2f)  <%s> <%s> " % \
                    (miFrac, HofX, maxHX, HofY, maxHY, HofXgivenY,
                     HofX, xyMI, min(HofX, HofY), aKey, bKey)
                if (writeFlag):
                    if (HofX <= HofY):
                        fh.write(
                            "%6.3f\t%d\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%8.5f\t%8.5f\t%8.5f\t%s\t%s\n" %
                            (xyMI / HofX, len(tmpI1), HofX, HofXgivenY, xyMI, rhoP, rhoS, p_MI, p_rho, max(p_MI, p_rho), nospace(aKey), nospace(bKey)))
                    else:
                        fh.write(
                            "%6.3f\t%d\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%8.5f\t%8.5f\t%8.5f\t%s\t%s\n" %
                            (xyMI / HofY, len(tmpI1), HofY, HofYgivenX, xyMI, rhoP, rhoS, p_MI, p_rho, max(p_MI, p_rho), nospace(bKey), nospace(aKey)))

                ## if ( miFrac > 0.8 ): sys.exit(-1)

            # the MI matrix is symmetrical
            pmiMatrix[ii][jj] = xyMI
            pmiMatrix[jj][ii] = xyMI

            # print " "
            # sys.exit(-1)

    if (writeFlag):
        fh.close()

    # now we go through and filter the pmiMatrix using the data-processing
    # inequality as Aracne does ...
    rmEdges = [0] * numKeys
    for ii in range(numKeys):
        rmEdges[ii] = [0] * numKeys

    numTst = 0
    numRM = 0
    for ii in range(numKeys):
        for jj in range(numKeys):
            if (pmiMatrix[ii][jj] == 0.0):
                continue
            for kk in range(numKeys):
                if (pmiMatrix[ii][kk] == 0.0):
                    continue
                if (pmiMatrix[jj][kk] == 0.0):
                    continue
                (k1, k2) = chooseWeakestLink(ii, jj, kk, pmiMatrix)
                numTst = numTst + 3
                if (k1 >= 0 and k2 >= 0):
                    rmEdges[k1][k2] = 1
                    numRM += 1
    print " --> chose %d edges for removal out of %d " % (numRM, numTst)

    for ii in range(numKeys):
        for jj in range(numKeys):
            if (rmEdges[ii][jj]):
                pmiMatrix[ii][jj] = 0.0

    # are there any nodes that have no edges anywhere ???
    for ii in range(numKeys):
        aKey = allKeys[ii]
        allZero = 1
        for jj in range(numKeys):
            if (pmiMatrix[ii][jj] > 0.0):
                allZero = 0
        if (allZero):
            print " node %s is all alone " % aKey

    if (writeFlag):
        dpiOut = outFilename + ".dpi"
        fh = file(dpiOut, 'w')
        for ii in range(numKeys):
            aKey = allKeys[ii]
            for jj in range(ii + 1, numKeys):
                bKey = allKeys[jj]
                abMI = pmiMatrix[ii][jj]
                if (pmiMatrix[ii][jj] > 0.0):
                    fh.write("%6.3f\t%s\t%s\n" %
                             (abMI, nospace(aKey), nospace(bKey)))
        fh.close()


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def removeDuplicateKeys(allClinDict):

    allKeys = allClinDict.keys()
    allKeys.sort()
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    print " "
    print " now looking for duplicate keys : "
    removeFlags = [0] * len(allKeys)
    for ii in range(len(allKeys)):
        aKey = allKeys[ii]
        aTokens = aKey.split(':')
        if (len(aTokens) > 1):
            rPartA = aTokens[-1]
        else:
            rPartA = aTokens[0]
        for jj in range(ii + 1, len(allKeys)):
            bKey = allKeys[jj]
            bTokens = bKey.split(':')
            if (len(bTokens) > 1):
                rPartB = bTokens[-1]
            else:
                rPartB = bTokens[0]

            if (rPartA.lower() == rPartB.lower()):
                print " SIMILAR (will combine) : ", ii, aKey, jj, bKey
                # so now we want to collapse the data and eliminate the
                # redundant key ...
                removeFlags[jj] = 1
                for kk in range(numClin):
                    if (allClinDict[aKey][kk] != "NA" and allClinDict[bKey][kk] != "NA"):
                        if (allClinDict[aKey][kk] != allClinDict[bKey][kk]):
                            print "     both non-NA ??? %5d  %30s  %30s " % (kk, allClinDict[aKey][kk], allClinDict[bKey][kk])
                    if (allClinDict[aKey][kk] == "NA"):
                        if (allClinDict[bKey][kk] != "NA"):
                            allClinDict[aKey][kk] = allClinDict[bKey][kk]

    print " "
    print " original number of keys : ", len(allKeys)
    for jj in range(len(allKeys)):
        if (removeFlags[jj]):
            bKey = allKeys[jj]
            print " --> deleting key ", bKey
            del allClinDict[bKey]

    allKeys = allClinDict.keys()
    allKeys.sort()
    print " new number of keys : ", len(allKeys)

    # now shorten the keys if we can ...
    print " "
    print " abbreviation keys : "
    for jj in range(len(allKeys)):
        bKey = allKeys[jj]
        bTokens = bKey.split(':')
        if (len(bTokens) > 1):
            rPartB = bTokens[-1]
            if (rPartB not in allKeys):
                allClinDict[rPartB] = allClinDict[bKey]
                print " --> abbreviating %s to %s " % (bKey, rPartB)
                del allClinDict[bKey]
                if (len(allClinDict[rPartB]) != numClin):
                    print " OOPS !!! need to copy deep "
                    sys.exit(-1)
            else:
                print " --> CANNOT abbreviate %s to %s " % (bKey, rPartB)

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeConstantKeys(allClinDict):

    print " in removeConstantKeys ... "

    allKeys = allClinDict.keys()
    allKeys.sort()
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    # any feature name which at least partially matches any of these
    # "magic" strings should NOT be removed!
    magicStrings = [
        "disease_code", "gender", "days_to_initial", "days_to_death", "icd_",
        "sampleType", "tumor_type", "cnvr_lvl3_qc", "pretreatment_history",
        "year_of_dcc_upload", "tumor_tissue_site", "histolog", "diagnosis", 
        "country", "_data", "batch_number" ]

    print " "
    print " now looking for constant (single-value) keys : "

    removeFlags = [0] * len(allKeys)
    for ii in range(len(allKeys)):
        aKey = allKeys[ii]

        doNotRemove = 0
        for aString in magicStrings:
            if (aKey.find(aString) >= 0):
                doNotRemove = 1
        if (doNotRemove):
            continue

        otherValues = []
        for kk in range(numClin):
            zValue = allClinDict[aKey][kk]
            if (zValue != "NA"):
                if (zValue not in otherValues):
                    otherValues += [zValue]
        if (len(otherValues) == 1):
            print "         removing key %s : only non-NA value is %s " % (aKey, otherValues[0])
            removeFlags[ii] = 1
        elif (len(otherValues) == 0):
            print "         removing key %s : only NA values !!! " % aKey
            removeFlags[ii] = 1

    print " "
    print " original number of keys : ", len(allKeys)
    numDel = 0
    for jj in range(len(allKeys)):
        if (removeFlags[jj]):
            bKey = allKeys[jj]
            print " --> deleting key ", bKey
            del allClinDict[bKey]
            numDel += 1

    allKeys = allClinDict.keys()
    allKeys.sort()

    if (numDel > 0):
        print " deleted %d keys " % numDel
        print " new number of keys : ", len(allKeys)
        # sys.exit(-1)
    else:
        print " no constant keys found or removed "

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeUninformativeKeys(allClinDict):

    # these strings should be removed no matter what ...
    magicDeleteStrings = [
        "detection_method", "tissue_source_site", "lab_proc", "_dcc_",
        "procedure_name", "ospective_collection",
        "_involvement_site", "_reason", "_family_member_", "patient_id"]

    # and these strings should NOT be removed ...
    # (removed HPV_type_var on 9/29)
    magicKeepStrings = [
        "bcr_patient_barcode", "disease_code",
        "iCluster_Adeno_k2", "nte_site", "batch_number",
        "initial_pathologic_diagnosis_method",
        "init_pathology_dx_method_other" ]

    print " in removeUninformativeKeys ... "

    allKeys = allClinDict.keys()
    allKeys.sort()
    aKey = allKeys[0]
    numClin = len(allClinDict[aKey])

    print " "
    print " now looking for uninformative keys : "
    removeFlags = [0] * len(allKeys)

    for ii in range(len(allKeys)):
        aKey = allKeys[ii]

        # if this is one of the magicKeepStrings, then skip over ...
        doSkip = 0
        for aString in magicKeepStrings:
            if ( aKey.lower().find(aString.lower()) >= 0 ): 
                print " skipping looking at this string : <%s> " % aKey
                doSkip = 1
        if ( doSkip ): continue
        
        otherValues = []
        numNA = 0
        allNumbers = 1
        for kk in range(numClin):
            zValue = allClinDict[aKey][kk]
            if (zValue != "NA"):
                if (zValue not in otherValues):
                    otherValues += [zValue]
                try:
                    zFloat = float(zValue)
                except:
                    allNumbers = 0
            else:
                numNA += 1

        print " looking at key %s ... allNumbers=%d ... |card|=%d " % (aKey, allNumbers, len(otherValues)), otherValues[:10]
        if (not allNumbers):
            if ((len(otherValues) + numNA) > int(0.90 * numClin)):
                print "        (a) removing key %s : numNA=%d  len(otherValues)=%d  numClin=%d " % (aKey, numNA, len(otherValues), numClin)
                print "                                    ", otherValues[:3], otherValues[-3:]
                print otherValues
                removeFlags[ii] = 1
            # 01feb13 : if a categorical feature has more than 20 categories,
            # drop it!
            if (len(otherValues) > 20):
                print "        (b) removing key %s : numNA=%d  len(otherValues)=%d  numClin=%d " % (aKey, numNA, len(otherValues), numClin)
                print "                                    ", otherValues[:3], otherValues[-3:]
                print otherValues
                removeFlags[ii] = 1

        # make sure that any string that looks like one of the magicDeleteStrings
        # gets removed ...
        for aString in magicDeleteStrings:
            if (not removeFlags[ii]):
                if ( aKey.lower().find(aString.lower()) >= 0 ):
                    print "        removing key %s " % aKey
                    removeFlags[ii] = 1

    print " "
    print " original number of keys : ", len(allKeys)
    numDel = 0
    for jj in range(len(allKeys)):
        if (removeFlags[jj]):
            bKey = allKeys[jj]
            print " --> deleting key ", bKey
            del allClinDict[bKey]
            numDel += 1

    allKeys = allClinDict.keys()
    allKeys.sort()

    if (numDel > 0):
        print " deleted %d keys " % numDel
        print " new number of keys : ", len(allKeys)
        # sys.exit(-1)
    else:
        print " no constant keys found or removed "

    return (allClinDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getBestKeyOrder(allClinDict, naCounts):

    allKeys = allClinDict.keys()
    allKeys.sort()

    bestKeyOrder = []
    minNA = min(naCounts)
    maxNA = max(naCounts)
    # print " minNA=%d  maxNA=%d " % ( minNA, maxNA )

    # we want to start with 'bcr_patient_barcode'
    if ( 'bcr_patient_barcode' in allKeys ):
        bestKeyOrder += ['bcr_patient_barcode']
    elif ( 'C:CLIN:bcr_patient_barcode:::::' in allKeys ):
        bestKeyOrder += ['C:CLIN:bcr_patient_barcode:::::']
    else:
        # but what if it is not in the clinical dictionary ??? !!!
        print " ERROR ??? bcr_patient_barcode is not one of the keys ??? " 
        for aKey in allKeys:
            if ( aKey.find("bcr_patient") >= 0 ):
                print aKey
        sys.exit(-1)

    for n in range(minNA, maxNA + 1):
        for ii in range(len(allKeys)):
            aKey = allKeys[ii]
            if (aKey.lower().find("bcr_patient_barcode")>=0):
                continue
            if (naCounts[ii] == n):
                bestKeyOrder += [aKey]
    print " "
    print " "
    print " bestKeyOrder : ", len(bestKeyOrder)
    print bestKeyOrder

    return (bestKeyOrder)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtKey(clinVec):

    # print " "
    # print clinVec[:5], ' ... ', clinVec[-5:]

    labelList = []
    labelDict = {}

    allNumeric = 1
    nCount = 0
    nNA = 0

    for aVal in clinVec:

        nCount += 1

        bVal = str(aVal)

        if (bVal == "NA"):
            nNA += 1
        elif (bVal == "NAN"):
            nNA += 1
        else:
            try:
                xVal = float(aVal)
                if (xVal not in labelList):
                    labelList += [xVal]
                    labelDict[xVal] = 0
                labelDict[xVal] += 1
            except:
                allNumeric = 0
                if (aVal not in labelList):
                    labelList += [aVal]
                    labelDict[aVal] = 0
                labelDict[aVal] += 1

    # check that there is something ???
    if ( (nCount-nNA) == 0 ):
        keyType = 'NA'
        return (keyType, nCount, nNA, 0, [], [])

    nCard = len(labelList)
    # print allNumeric, nCount, nNA, nCard

    # if nCount = (nNA + nCard), then there is a different value
    # for each of the examples and this cannot be informative unless
    # the values are numeric ... so we should probably remove it from
    # the data ...
    if (allNumeric):
        keyType = 'NUMERIC'
        nCard = 1
    else:
        keyType = 'NOMINAL'

    labelCounts = []
    if (keyType == 'NOMINAL'):
        labelList.sort()
        labelCounts = [0] * len(labelList)
        for ii in range(len(labelList)):
            labelCounts[ii] = labelDict[labelList[ii]]

    return (keyType, nCount, nNA, nCard, labelList, labelCounts)

#------------------------------------------------------------------------------
