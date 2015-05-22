# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import numpy
import sys

# these are my local ones
from env import gidgetConfigVars
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanUpName(aName):

    bName = ''

    aName = aName.upper()

    ## ii = aName.find(" - Homo sapiens (human)")
    ii = aName.find(" - HOMO SAPIENS (HUMAN)")
    if (ii >= 0):
        aName = aName[:ii]
    aName = aName.strip()

    ii = aName.find("(")
    while (ii >= 0):
        jj = aName.find(")", ii)
        aName = aName[:ii] + aName[jj + 1:]
        ii = aName.find("(")
    aName = aName.strip()

    ii = aName.find("<")
    while (ii >= 0):
        jj = aName.find(">", ii)
        aName = aName[:ii] + aName[jj + 1:]
        ii = aName.find("<")
    aName = aName.strip()

    for ii in range(len(aName)):
        if (aName[ii] == ','):
            continue
        elif (aName[ii] == '('):
            bName += '_'
        elif (aName[ii] == ')'):
            bName += '_'
        elif (aName[ii] == '-'):
            bName += '_'
        elif (aName[ii] == '/'):
            bName += '_'
        elif (aName[ii] == ';'):
            bName += '_'
        elif (aName[ii] == '&'):
            continue
        elif (aName[ii] == '#'):
            continue
        elif (aName[ii] == ' '):
            bName += '_'
        else:
            bName += aName[ii].upper()

    ii = bName.find("__")
    while (ii >= 0):
        print "             ", ii, bName
        bName = bName[:ii] + bName[ii + 1:]
        print "             ", bName
        ii = bName.find("__")

    return (bName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readPathways():

    fh = file(
        gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] + "/nci_pid/only_NCI_Nature_ver4.tab", 'r')

    pwDict = {}

    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()
        tokenList = aLine.split('\t')
        if (len(tokenList) != 3):
            continue
        if (tokenList[0] == "pathway"):
            continue

        longPathwayName = tokenList[0]
        shortPathwayName = tokenList[1]

        geneTokens = tokenList[2].strip()
        geneList = geneTokens.split(',')
        geneList.sort()

        if (len(geneList) > 0):
            while (geneList[0] == ''):
                geneList = geneList[1:]
                if (len(geneList) == 0):
                    continue

        if (len(geneList) == 0):
            continue

        pathwayName = cleanUpName(shortPathwayName)

        if (pathwayName not in pwDict.keys()):
            # print " adding pathway %s (%d) " % ( pathwayName, len(geneList) )
            pwDict[pathwayName] = geneList
        else:
            if (len(pwDict[pathwayName]) < len(geneList)):
                # print " substituting shorter list of genes for %s (%d) " % (
                # pathwayName, len(geneList) )
                pwDict[pathwayName] = geneList
            # else:
                # print " NOT substituing list for %s " % pathwayName

    fh.close()

    print " "
    print " have pathway dictionary with %d pathways " % len(pwDict)
    print "     --> now looking for duplicate pathways ... "
    pwList = pwDict.keys()
    pwList.sort()
    delList = []
    pairDict = {}

    for ii in range(len(pwList) - 1):
        iiName = pwList[ii]
        iiLen = len(pwDict[iiName])
        for jj in range(ii + 1, len(pwList)):
            jjName = pwList[jj]
            jjLen = len(pwDict[jjName])
            if (jjLen != iiLen):
                continue

            if (pwDict[iiName] == pwDict[jjName]):
                print "\n\n SAME !!! "
                print iiName, iiLen
                print pwDict[iiName]
                print jjName, jjLen
                print pwDict[jjName]

                iiSplit = iiName.split('__')
                jjSplit = jjName.split('__')

                if (iiSplit[1] <= jjSplit[1]):
                    pairNames = (iiSplit[1], jjSplit[1])
                else:
                    pairNames = (jjSplit[1], iiSplit[1])
                if (pairNames in pairDict.keys()):
                    pairDict[pairNames] += 1
                else:
                    pairDict[pairNames] = 1

                if (iiSplit[1] == jjSplit[1]):
                    if (len(iiName) <= len(jjName)):
                        delList += [jjName]
                    else:
                        delList += [iiName]

                else:

                    if (iiSplit[1] == "NCI-NATURE"):
                        delList += [jjName]
                    elif (jjSplit[1] == "NCI-NATURE"):
                        delList += [iiName]

                    elif (iiSplit[1] == "PID"):
                        delList += [jjName]
                    elif (jjSplit[1] == "PID"):
                        delList += [iiName]

                    elif (iiSplit[1] == "KEGG"):
                        delList += [jjName]
                    elif (jjSplit[1] == "KEGG"):
                        delList += [iiName]

                    elif (iiSplit[1] == "PWCOMMONS"):
                        delList += [jjName]
                    elif (jjSplit[1] == "PWCOMMONS"):
                        delList += [iiName]

                    elif (iiSplit[1] == "REACTOME"):
                        delList += [jjName]
                    elif (jjSplit[1] == "REACTOME"):
                        delList += [iiName]

                    elif (iiSplit[1] == "WIKIPATHWAYS"):
                        delList += [jjName]
                    elif (jjSplit[1] == "WIKIPATHWAYS"):
                        delList += [iiName]

                    elif (iiSplit[1] == "WIKIPW"):
                        delList += [jjName]
                    elif (jjSplit[1] == "WIKIPW"):
                        delList += [iiName]

                    elif (iiSplit[1] == "SMPDB"):
                        delList += [jjName]
                    elif (jjSplit[1] == "SMPDB"):
                        delList += [iiName]

                    elif (iiSplit[1] == "HUMANCYC"):
                        delList += [jjName]
                    elif (jjSplit[1] == "HUMANCYC"):
                        delList += [iiName]

                    else:
                        sys.exit(-1)

    for aName in delList:
        try:
            del pwDict[aName]
        except:
            doNothing = 1

    print " "
    print " returning pathway dictionary with %d pathways " % len(pwDict)
    print " "
    for aKey in pairDict.keys():
        print aKey, pairDict[aKey]
    print " "
    print " "

    return (pwDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def setFeatBits(rowLabels, featPrefix, doesContain, notContain):

    numSet = 0

    numRow = len(rowLabels)
    bitVec = numpy.zeros(numRow, dtype=numpy.bool)
    for iR in range(numRow):
        if (featPrefix != ""):
            if (not rowLabels[iR].startswith(featPrefix)):
                continue
        if (doesContain != ""):
            if (rowLabels[iR].find(doesContain) < 0):
                continue
        if (notContain != ""):
            if (rowLabels[iR].find(notContain) >= 0):
                continue
        bitVec[iR] = 1
        numSet += 1

    print featPrefix, doesContain, notContain, numRow, numSet
    if (numSet == 0):
        print " numSet=0 ... this is probably a problem ... "
        # sys.exit(-1)

    return (bitVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# B:GNAB:ADAM7:chr8:24298509:24384483:+:y_n_somatic y_n y_del
# --> B:GNAB:ADAM7:chr8:24298509:24384483:+:y_del_somatic


def makeNewFeatureName(curFeatName, oldString, newString):

    i1 = curFeatName.find(oldString)
    if (i1 < 0 or len(oldString) < 2):
        print " ERROR in makeNewFeatureName ???? ", curFeatName, oldString, newString

    i2 = i1 + len(oldString)
    newFeatName = curFeatName[:i1] + newString + curFeatName[i2:]
    # print curFeatName, oldString, newString, newFeatName

    return (newFeatName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def chooseCountThreshold(dataD):

    rowLabels = dataD['rowLabels']
    dMat = dataD['dataMatrix']

    numBits = 0
    for ii in range(len(rowLabels)):
        if (numBits > 0):
            continue
        if (rowLabels[ii].find("B:GNAB:TP53:") >= 0):
            for jj in range(len(dMat[ii])):
                if (dMat[ii][jj] == 0):
                    numBits += 1
                elif (dMat[ii][jj] == 1):
                    numBits += 1

    print " number of bits found for TP53 mutation feature: ", numBits
    countThreshold = int(numBits / 11) - 1
    return (countThreshold)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def pathwayGEXP(dataD, pathways={}):

    print " "
    print " ************************************************************* "
    print " ************************************************************* "
    print " "
    print " in pathwayGEXP ... "

    # check that the input feature matrix looks ok ...
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in pathwayGEXP ??? bad data ??? "
        return (dataD)

    if (len(pathways) == 0):
        print " no pathway information ??? "
        sys.exit(-1)

    print " "
    print " total number of pathways : ", len(pathways)
    print " "

    pathwayList = pathways.keys()
    pathwayList.sort()
    numPW = len(pathways)
    newNameVec = [0] * (numPW)
    newDataMat = [0] * (numPW)

    dMat = dataD['dataMatrix']

    kFeat = 0
    for aPathway in pathwayList:

        if (1):

            numON = 0
            newFeatName = "N:GEXP:" + aPathway + "::::"

            # first make sure we don't already have a feature with this name
            # ...
            stopNow = 0
            for iRow in range(numRow):
                if (newFeatName == rowLabels[iRow]):
                    stopNow = 1
            if (stopNow):
                continue

            print " tentative new feature #%d ... <%s> " % (kFeat, newFeatName)
            newNameVec[kFeat] = newFeatName
            newDataMat[kFeat] = numpy.zeros(numCol)
            # initialize to all NAs ...
            for iCol in range(numCol):
                newDataMat[kFeat][iCol] = NA_VALUE

            if (0):
                print " "
                print " "
                print aPathway, newFeatName
                print len(pathways[aPathway]), pathways[aPathway]

            for iR in range(numRow):

                # if ( iR%1000 == 0 ): print iR, numRow

                if (1):
                    gexpLabel = rowLabels[iR]
                    if (not gexpLabel.startswith("N:GEXP:")):
                        continue

                    try:
                        gexpTokens = gexpLabel.split(':')
                        gexpGene = gexpTokens[2].upper()
                    except:
                        print " FAILED to parse GEXP feature name ??? ", gexpLabel
                        continue

                    if (gexpGene in pathways[aPathway]):
                        for iCol in range(numCol):
                            if (dMat[iR][iCol] != "NA"):
                                if (dMat[iR][iCol] != NA_VALUE):
                                    if (newDataMat[kFeat][iCol] == NA_VALUE):
                                        newDataMat[kFeat][
                                            iCol] = dMat[iR][iCol]
                                    else:
                                        newDataMat[kFeat][
                                            iCol] += dMat[iR][iCol]

            if (1):
                kFeat += 1
                print " --> keeping this feature ... ", kFeat, newFeatName

            # else:
            # print " --> NOT keeping this feature ... ", newFeatName, numON,
            # min_numON

    numNewFeat = kFeat
    print " "
    print " --> number of new features : ", numNewFeat
    print len(newDataMat), len(newDataMat[0])

    # now we need to append these new features to the input data matrix
    newRowLabels = [0] * (numRow + numNewFeat)
    newMatrix = [0] * (numRow + numNewFeat)
    for iR in range(numRow):
        newRowLabels[iR] = rowLabels[iR]
        newMatrix[iR] = dMat[iR]
    for iR in range(numNewFeat):
        newRowLabels[iR + numRow] = newNameVec[iR]
        newMatrix[iR + numRow] = newDataMat[iR]

    dataD['rowLabels'] = newRowLabels
    dataD['dataMatrix'] = newMatrix

    print " "
    print " --> finished with pathwayGEXP ... "
    print " "

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
    print " Running : %s  %s  %s  " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print " "

    # read in the input feature matrix first, just in case there
    # actually isn't one yet available ...
    testD = tsvIO.readTSV(inFile)
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
    except:
        print " --> invalid / missing input feature matrix "
        sys.exit(-1)

    # and then pathway level mutation features
    if (1):
        pwDict = readPathways()
        newD = pathwayGEXP(testD, pwDict)
        testD = newD

    # and finally write it out ...
    tsvIO.writeTSV_dataMatrix(testD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
