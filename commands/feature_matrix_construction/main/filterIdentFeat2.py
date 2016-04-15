# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import miscMath
import miscMatrix
import miscTCGA
import plotMatrix
import tsvIO

import itertools
import numpy
import random
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function is specifically for choosing the 'best' feature from a group
# of GNAB features that all pertain to the same gene
#
# for example if 'nonsilent' and 'y_n' are identical, then we prefer 'nonsilent'
# or if 'dna_bin' and a specific 'dom_xxx_xxx' are the same, then we prefer the
# specific domain ...


def chooseMostSpecific(bestFeatureList):

    print "             in chooseMostSpecific ... "
    print "                 ", bestFeatureList[0]
    print "                 ", bestFeatureList[1]

    if (bestFeatureList[0].find("y_amp_") >= 0):
        return (bestFeatureList[1])
    if (bestFeatureList[1].find("y_amp_") >= 0):
        return (bestFeatureList[0])
    if (bestFeatureList[0].find("y_del_") >= 0):
        return (bestFeatureList[1])
    if (bestFeatureList[1].find("y_del_") >= 0):
        return (bestFeatureList[0])

    # we need to double-check that all of these features in fact
    # correspond to the same gene!!!
    geneList = []
    geneCounts = []
    for ii in range(len(bestFeatureList)):
        tokenList = bestFeatureList[ii].split(':')
        geneName = tokenList[2]
        if (geneName not in geneList):
            geneList += [geneName]
            geneCounts += [1]
        else:
            jj = geneList.index(geneName)
            geneCounts[jj] += 1
    if (len(geneList) > 1):
        return ('')

    # these are the mutation strings in order of decreasing specificity
    infixList = [
        ":ddG_", ":iarc_", ":tcga_", ":code_potential", ":mni_", ":mnf_",
        ":dom_", ":dna_bin", ":DNA_interface", ":missense", ":nonsilent", ":y_n"]
    NSorFS = ":ns_or_fs"
    ORstring = "_OR"

    featScores = [-1] * len(bestFeatureList)
    minScore = len(infixList)
    for ii in range(len(bestFeatureList)):
        aFeat = bestFeatureList[ii]
        fFlag = 0
        for aString in infixList:
            if (aFeat.find(aString) > 0):
                fFlag = 1
                featScores[ii] = infixList.index(aString)
                if (minScore > featScores[ii]):
                    minScore = featScores[ii]
        if (fFlag == 0):
            print " WARNING ??? never found the mutation string ??? ", aFeat
            return ( bestFeatureList[0] )
            sys.exit(-1)

    print bestFeatureList
    print featScores

    # count up how many "minScore" features we have ...
    numMin = 0
    for ii in range(len(bestFeatureList)):
        if (minScore == featScores[ii]):
            numMin += 1
    print numMin

    # find the first "minScore" feature ...
    for ii in range(len(bestFeatureList)):
        if (minScore == featScores[ii]):
            bestFeat = bestFeatureList[ii]
    if (numMin == 1):
        return (bestFeat)

    print bestFeat

    if (bestFeat.find(":dom_") > 0):
        # we must have multiple "dom" features, so now we want to
        # prioritize them by start position and by whether or not
        # they have the _ns_or_fs ending
        featScores = [999999] * len(bestFeatureList)
        minScore = 999999
        for ii in range(len(bestFeatureList)):
            aFeat = bestFeatureList[ii]
            if (aFeat.find(ORstring) >= 0):
                doNothing = 1
            elif (aFeat.find(":dom_") > 0):
                i1 = aFeat.find("_")
                i2 = aFeat.find("_", i1 + 1)
                i3 = aFeat.find("_", i2 + 1)
                print i1, i2, i3
                iPos = int(aFeat[i2 + 1:i3])
                print iPos
                if (aFeat.find(NSorFS) >= 0):
                    iPos -= 1
                featScores[ii] = iPos
                if (iPos < minScore):
                    minScore = iPos
        print featScores

        for ii in range(len(bestFeatureList)):
            if (featScores[ii] == minScore):
                bestFeat = bestFeatureList[ii]
                print " --> now returning : ", bestFeat
                return (bestFeat)

    # total hack, but ...
    if (len(bestFeatureList) == 2):
        if (bestFeatureList[0].endswith("_OR") and bestFeatureList[1].endswith("_germline")):
            return (bestFeatureList[1])
        if (bestFeatureList[1].endswith("_OR") and bestFeatureList[0].endswith("_germline")):
            return (bestFeatureList[0])
        if (bestFeatureList[0].endswith("_OR") and bestFeatureList[1].endswith("_somatic")):
            return (bestFeatureList[1])
        if (bestFeatureList[1].endswith("_OR") and bestFeatureList[0].endswith("_somatic")):
            return (bestFeatureList[0])

    if (0):
        print " need something more clever here "
        print bestFeatureList
    else:
        return ("")

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def constantVec(aVec):

    n = len(aVec)
    v = []
    for ii in range(n):
        if (aVec[ii] != NA_VALUE):
            if (aVec[ii] not in v):
                v += [aVec[ii]]
                if (len(v) > 1):
                    return (0)

    print "     in constantVec function ... ", v
    return (1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeIdenticalFeatures(inD, featType):

    print " in removeIdenticalFeatures ... <%s> " % featType

    rowLabels = inD['rowLabels']
    dataMatrix = inD['dataMatrix']

    nRowIn = len(dataMatrix)
    nColIn = len(dataMatrix[0])

    rmRowList = []

    iRow = 0
    while (iRow < nRowIn):

        print " "
        print " working on feature # %d " % iRow

        iFeatname = rowLabels[iRow]
        if (featType != "ANY"):
            if (iFeatname.find(featType) < 0):
                iRow += 1
                continue

        if (iFeatname.find(":ja_") > 0 ):
            iRow += 1
            continue

        curTokens = iFeatname.split(':')
        iGeneName = curTokens[2]

        jRow = iRow + 1
        done = 0

        # check to see if this feature is a ~constant~
        if (constantVec(dataMatrix[iRow])):
            rmRowList += [iRow]
            print "         --> adding constant iRow (%d) to rmRowList <%s> " % (iRow, iFeatname)
            done = 1

        while not done:

            if (jRow >= nRowIn):
                done = 1
                continue

            if (jRow in rmRowList):
                jRow += 1
                continue

            jFeatname = rowLabels[jRow]
            if (featType != "ANY"):
                if (jFeatname.find(featType) < 0):
                    jRow += 1
                    continue

            if (jFeatname.find(":ja_") > 0):
                jRow += 1
                continue

            curTokens = jFeatname.split(':')
            jGeneName = curTokens[2]

            ## HERE this makes things MUCH faster, but may not uncover
            ## all identical features ...
            if ( 1 ):
                if (jGeneName != iGeneName):
                    done = 1
                    continue

            identFeat = 1
            ## print "     --> comparing %d and %d  ( %s and %s ) " % (iRow, jRow, iFeatname, jFeatname)
            for iCol in range(nColIn):
                if (dataMatrix[iRow][iCol] != dataMatrix[jRow][iCol]):
                    identFeat = 0

            if (identFeat):
                print "     --> identical !!! %d and %d  ( %s and %s ) " % (iRow, jRow, iFeatname, jFeatname)
                newName = chooseMostSpecific([iFeatname, jFeatname])
                if (newName == iFeatname):
                    if (jRow not in rmRowList):
                        rmRowList += [jRow]
                        print "         --> adding jRow (%d) to rmRowList <%s> " % (jRow, jFeatname)
                elif (newName == jFeatname):
                    if (iRow not in rmRowList):
                        rmRowList += [iRow]
                        print "         --> adding iRow (%d) to rmRowList <%s> " % (iRow, iFeatname)
                    print "         --> skipping to next iRow "
                    done = 1
                    continue

            jRow += 1

        iRow += 1

    print len(rmRowList)
    # print rmRowList

    outD = tsvIO.filter_dataMatrix(inD, rmRowList, [])

    print " returning ... "
    return (outD)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) != 4):
            print " Usage : %s <input feature matrix> <output feature matrix> <featType> " % sys.argv[0]
            print "         to avoid filtering on featType, use ANY "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        inFile = sys.argv[1]
        outFile = sys.argv[2]
        featType = sys.argv[3]

    print " "
    print " "
    print " ******************** "
    print "  in filterIdentFeat  "
    print " ******************** "

    inD = tsvIO.readTSV(inFile)
    rowLabels = inD['rowLabels']
    numRow = len(rowLabels)

    outD = removeIdenticalFeatures(inD, featType)

    tsvIO.writeTSV_dataMatrix(outD, 0, 0, outFile)

    print " FINISHED "
    print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
