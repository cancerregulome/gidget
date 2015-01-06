# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# want to make sure that we don't add a feature like:
# B:SAMP:I(A,B|C)
# if   B:SAMP:I(B,A|C)
# already exists ...


def similarFeatureExists(newLabel, rowLabels):

    if (newLabel in rowLabels):
        return (1)

    newTokens = newLabel.split(':')
    if (newTokens[2].startswith("I(")):
        i1 = newTokens[2].find(",")
        i2 = newTokens[2].find("|", i1)
        i3 = newTokens[2].find(")", i2)
        if (i1 >= 0):
            labelA = newTokens[2][2:i1]
            labelB = newTokens[2][i1 + 1:i2]
            givenC = newTokens[2][i2 + 1:i3]
        else:
            labelA = newTokens[2][2:i2]
            labelB = "none"
            givenC = newTokens[2][i2 + 1:i3]
    else:
        print " we should not get here, no ??? "
        sys.exit(-1)

    for tstLabel in rowLabels:

        checkThis = 0
        if (tstLabel[:9] == newLabel[:9]):
            checkThis = 1
        if (newLabel[2:6] == "SAMP" and tstLabel[2:6] == "CLIN"):
            checkThis = 1
        if (newLabel[2:6] == "CLIN" and tstLabel[2:6] == "SAMP"):
            checkThis = 1

        if (checkThis):
            tstTokens = tstLabel.split(':')
            if (tstTokens[2].startswith("I(")):
                i1 = tstTokens[2].find(",")
                i2 = tstTokens[2].find("|", i1)
                i3 = tstTokens[3].find(")", i2)
            if (i1 >= 0):
                tstA = tstTokens[2][2:i1]
                tstB = tstTokens[2][i1 + 1:i2]
                tstC = tstTokens[2][i2 + 1:i3]
            else:
                tstA = tstTokens[2][2:i2]
                tstB = "none"
                tstC = tstTokens[2][i2 + 1:i3]

            if (givenC.lower() == tstC.lower()):
                if (labelA.lower() == tstA.lower() and labelB.lower() == tstB.lower()):
                    print newLabel, tstLabel
                    return (1)
                elif (labelA.lower() == tstB.lower() and labelB.lower() == tstA.lower()):
                    print newLabel, tstLabel
                    print " AHA !!! found one of these :-) "
                    # sys.exit(-1)
                    return (1)

    print " did not find any feature similar to ", newLabel
    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def checkColonCount(newLabel):

    numC = 0
    for ii in range(len(newLabel)):
        if (newLabel[ii] == ':'):
            numC += 1

    if (numC == 7):
        return (newLabel)
    elif (numC < 7):
        for ii in range(numC, 7):
            newLabel += ':'
        return (newLabel)
    elif (numC > 7):
        print " WARNING !!! improper feature label ??? ", newLabel, numC
        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addIndicators4oneFeat(aKey, rowLabels, tmpMatrix):

    print " "
    print " "
    print " *********************************************** "
    print " in addIndicators4oneFeat ... ", aKey

    numRow = len(tmpMatrix)
    numCol = len(tmpMatrix[0])

    jRow = -1
    for iRow in range(numRow):
        if (aKey == rowLabels[iRow]):
            jRow = iRow

    if (jRow < 0):
        print " failed to find specified feature "
        return (rowLabels, tmpMatrix)

    aKey = rowLabels[jRow]
    if (aKey.startswith("N:")):
        print " feature is numerical "
        return (rowLabels, tmpMatrix)

    if (aKey.startswith("B:GNAB:")):
        print " not producing indicator features for binary mutation features "
        return (rowLabels, tmpMatrix)

    tmpVec = tmpMatrix[jRow]
    print aKey, jRow, numCol
    uVec = []
    for iCol in range(numCol):
        curVal = tmpVec[iCol]
        if (curVal != "NA" and curVal != NA_VALUE):
            strVal = str(curVal)

            if ( 0 ):
                if (strVal not in uVec): uVec += [str(curVal)]
            else:
                uFound = 0
                for uVal in uVec:
                    if ( strVal.lower() == uVal.lower() ): uFound = 1
                if ( not uFound ): uVec += [str(curVal)]

    curV = tmpVec

    print "     uVec : ", uVec
    nCard = len(uVec)
    if (nCard < 2):
        return (rowLabels, tmpMatrix)
    if (nCard > 32):
        return (rowLabels, tmpMatrix)

    labelList = uVec
    labelList.sort()
    if (labelList == ['0', '1']):
        return (rowLabels, tmpMatrix)
    print "     labelList : ", labelList

    # sample aKey:
    # C:SAMP:Genome_Instability:::::TK_cat
    # 01234567
    # ^ i1
    # ^ len(aKey)

    # first we build the singleton indicator features ...
    print " "
    print " *** adding singleton indicator features *** "
    print " "
    for aLabel in labelList:
        print " "
        print " aLabel=<%s> " % (aLabel)
        print " --> building new label ... "
        try:
            if (aKey[1] == ":" and aKey[6] == ":"):
                # if we get to here, then we must have a feature that starts 
                # with something like C:GEXP:NOTCH2...
                i1 = aKey[7:].find(':')
                if (i1 < 0):
                    i1 = len(aKey)
                    i2 = len(aKey)
                else:
                    # if we get here, then a 3rd colon has been found
                    i1 = i1 + 7
                    i2 = aKey[(i1 + 1):].find(':')
                    if (i2 < 0):
                        i2 = len(aKey)
                    else:
                        # and if we get here, then a 4th colon has been found
                        # BUT I DON'T UNDERSTAND WHY THAT MATTERS ???
                        #### i2 = i2 + i1
                        i2 = i1 
                print aKey, i1, i2, len(aKey)
                print aKey[7:i1]
                print aKey[i2:]

                if (i2 > 0 and i2 < len(aKey)):
                    newLabel = "B:" + \
                        aKey[2:7] + \
                        "I(" + aLabel + "|" + aKey[7:i1] + ")" + aKey[i2:]
                else:
                    newLabel = "B:" + \
                        aKey[2:7] + \
                        "I(" + aLabel + "|" + aKey[7:i1] + ")" + ":::::"

                print " --> newLabel : <%s> " % newLabel

                if (newLabel.find("|):") > 0):
                    print " (a) BAILING !!!! ", newLabel
                    sys.exit(-1)

            else:
                print " should not get here ??? "
                sys.exit(-1)

        except:
            print " (b) BAILING !!! "
            print " ERROR in addIndicatorFeatures ??? ", aLabel, aKey
            sys.exit(-1)

        # make sure there are no blanks ...
        print " newLabel = <%s> " % newLabel
        newLabel = tsvIO.replaceBlanks(newLabel, "_")
        print " newLabel = <%s> " % newLabel

        # double-check that we have 7 colons ... otherwise add at end ...
        newLabel = checkColonCount(newLabel)

        if (similarFeatureExists(newLabel, rowLabels)):
            print " this indicator variable already exists so I will not make a new one ... ", newLabel
            continue

        tmpV = [0] * numCol
        numON = 0
        print "     ... looping over %d values ... " % (numCol)
        for iCol in range(numCol):
            if (curV[iCol] == "NA"):
                tmpV[iCol] = "NA"
            elif (curV[iCol] == NA_VALUE):
                tmpV[iCol] = "NA"
            elif (str(curV[iCol]).lower() == str(aLabel).lower()):
                tmpV[iCol] = 1
                numON += 1

        if (numON > (numCol / 300)):
            print " adding new feature : ", newLabel
            # print tmpV
            rowLabels += [newLabel]
            tmpMatrix += [tmpV]
        else:
            print " --> actually NOT adding this feature after all ... ", newLabel, numON, (numCol / 300)

    # if this was a binary feature, then pairwise indicators are not required
    if (nCard == 2):
        return (rowLabels, tmpMatrix)
    if (labelList == ['0', '1']):
        return (rowLabels, tmpMatrix)

    # and then we add the pairwise indicator features ...
    print " "
    print " *** adding pairwise indicator features *** "
    print labelList
    print " "
    for ak in range(len(labelList)):
        aLabel = str(labelList[ak])

        for bk in range(ak + 1, len(labelList)):
            bLabel = str(labelList[bk])

            print " aLabel=<%s>  bLabel=<%s> " % (aLabel, bLabel)
            print " --> building new label ... "

            try:
                if (aKey[1] == ":" and aKey[6] == ":"):
                    i1 = aKey[7:].find(':')
                    if (i1 < 0):
                        i1 = len(aKey)
                        i2 = len(aKey)
                    else:
                        i1 = i1 + 7
                        i2 = aKey[(i1 + 1):].find(':')
                        if (i2 < 0):
                            i2 = len(aKey)
                        else:
                            #### i2 = i2 + i1
                            i2 = i1 
                    print aKey, i1, i2
                    print aKey[7:i1]
                    print aKey[i2:]

                    if (i2 > 0 and i2 < len(aKey)):
                        newLabel = "B:" + \
                            aKey[2:7] + "I(" + aLabel + "," + bLabel + \
                            "|" + aKey[7:i1] + ")" + aKey[i2:]
                    else:
                        newLabel = "B:" + \
                            aKey[2:7] + \
                            "I(" + aLabel + "," + bLabel + \
                            "|" + aKey[7:i1] + ")" + ":::::"

                    print " --> newLabel : <%s> " % newLabel

                    if (newLabel.find("|):") > 0):
                        print " (c) BAILING !!!! ", newLabel
                        sys.exit(-1)
                else:
                    print " should not get here ??? "
                    sys.exit(-1)

            except:
                print " NOT continuing to add pairwise indicator features !!! ", aLabel, bLabel, aKey
                continue

            # make sure there are no blanks ...
            print " newLabel = <%s> " % newLabel
            newLabel = tsvIO.replaceBlanks(newLabel, "_")
            print " newLabel = <%s> " % newLabel

            # double-check that we have 7 colons ... otherwise add at end ...
            newLabel = checkColonCount(newLabel)

            if (similarFeatureExists(newLabel, rowLabels)):
                print " this indicator variable already exists so I will not make a new one ... ", newLabel
                continue

            tmpV = [0] * numCol
            numON = 0
            print "     ... looping over %d values ... " % (numCol)
            for kk in range(numCol):
                tmpV[kk] = "NA"
                if (curV[kk].lower() == aLabel.lower()):
                    tmpV[kk] = 1
                    numON += 1
                elif (curV[kk].lower() == bLabel.lower()):
                    tmpV[kk] = 0

            if (numON > (numCol / 300)):
                print " adding new feature : ", newLabel
                # print tmpV
                rowLabels += [newLabel]
                tmpMatrix += [tmpV]
            else:
                print " --> actually NOT adding this feature after all ... ", newLabel, numON, (numCol / 300)

    return (rowLabels, tmpMatrix)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function creates N binary indicator vectors based on a single nominal
# (categorical) variable of cardinality N -- the indicator vectors still
# contain strings ("I0" and "I1") so that we can tell that they are still not
# truly "numeric" vectors ...


def addIndicatorFeatures(tmpD):

    print " *********************************************** "
    print " in addIndicatorFeatures ... "

    try:
        rowLabels = tmpD['rowLabels']
        colLabels = tmpD['colLabels']
        tmpMatrix = tmpD['dataMatrix']
    except:
        print " invalid or empty data structure in addIndicatorFeatures ??? "
        return (tmpD)

    print " "
    print " previously existing indicator features ... "
    for aFeat in rowLabels:
        if (aFeat.find(":I(") >= 0):
            if (aFeat.find(",") < 0):
                print aFeat
    print " "
    print " "

    numRow = len(rowLabels)
    numCol = len(colLabels)

    for iRow in range(numRow):
        aFeature = rowLabels[iRow]

        if (aFeature.find("Gistic") >= 0):
            continue
        if (aFeature.find("batch_number") >= 0):
            continue
        if (aFeature.find("icd_o_3_histology") >= 0):
            continue
        if (aFeature.find("icd_o_3_site") >= 0):
            continue
        if (aFeature.find("icd_10") >= 0):
            continue
        if (aFeature.find("system_version") >= 0):
            continue
        if (aFeature.find(":GNAB:") >= 0):
            continue

        if (aFeature.startswith("N:")):
            doNothing = 1
        else:
            (rowLabels, tmpMatrix) = addIndicators4oneFeat(
                aFeature, rowLabels, tmpMatrix)

    tmpD['rowLabels'] = rowLabels
    tmpD['dataMatrix'] = tmpMatrix

    return (tmpD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print " Usage : %s <input TSV> <output TSV> " % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    tsvNameIn = sys.argv[1]
    tsvNameOut = sys.argv[2]

    print " "
    print " ****************************************************************** "
    print " reading input file <%s> " % tsvNameIn
    tmpD = tsvIO.readTSV(tsvNameIn)

    if (len(tmpD) == 0):
        print " in addIndicators ... no input data ... nothing to do here ... "
        sys.exit(-1)

    # automatically generate indicator features for categorical features
    tmpD = addIndicatorFeatures(tmpD)

    tsvIO.writeTSV_dataMatrix(tmpD, 0, 0, tsvNameOut)

    print " "
    print " "
    print " FINISHED "
    print " "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
