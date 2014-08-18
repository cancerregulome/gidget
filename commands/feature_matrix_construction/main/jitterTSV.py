# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import tsvIO

import random
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) != 3):
            print " Usage : %s <input file> <output file> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        inFile = sys.argv[1]
        outFile = sys.argv[2]

    print " "
    print " "
    print " **************** "
    print " in jitterTSV : "
    print " "
    print " ***************************************************************** "
    print " calling readTSV ... ", inFile
    inD = tsvIO.readTSV(inFile)
    tsvIO.lookAtDataD(inD)

    rowLabels = inD['rowLabels']
    colLabels = inD['colLabels']
    dataMatrix = inD['dataMatrix']

    numRow = len(rowLabels)
    numCol = len(colLabels)

    outD = {}
    outD['dataType'] = inD['dataType']
    outD['rowLabels'] = rowLabels
    outD['colLabels'] = colLabels

    numRow = len(rowLabels)
    numCol = len(colLabels)
    outMatrix = [0] * numRow
    for iRow in range(numRow):
        outMatrix[iRow] = [0] * numCol

    numDiff = 0

    dataTypeList = [(
        "N:GEXP:", "C:SAMP:gexpPlatform", 0.10, "RNASeq", 999999999),
        ("N:MIRN:", "C:SAMP:mirnPlatform",
         0.10, "RNASeq", 999999999),
        ("N:METH:", "C:SAMP:methPlatform", 0.10, "Methyl", 1)]

    # new as of 27jun13 :
    dataTypeList = [(
        "N:GEXP:", "C:SAMP:gexpPlatform", 0.01, "RNASeq", 999999999),
        ("N:MIRN:", "C:SAMP:mirnPlatform", 0.01, "RNASeq", 999999999)]

    iPlatFeatList = [0] * len(dataTypeList)

    # first we need to find the platform feature for each of the
    # data types to be 'jittered' ...
    for iTuple in range(len(dataTypeList)):
        aTuple = dataTypeList[iTuple]
        print " "
        print aTuple
        dataType = aTuple[0]
        platFeat = aTuple[1]
        maxJitter = aTuple[2]
        iPlatFeat = -1
        for iRow in range(numRow):
            featName = rowLabels[iRow]
            if (featName.upper().startswith(platFeat.upper())):
                iPlatFeat = iRow
                print "     --> have platform feature : ", iPlatFeat, featName, platFeat
        iPlatFeatList[iTuple] = iPlatFeat

    # now we loop over the features ...
    for iRow in range(numRow):

        featName = rowLabels[iRow]

        # pre-emptively, we just mirror the input row of data ...
        for iCol in range(numCol):
            outMatrix[iRow][iCol] = dataMatrix[iRow][iCol]

        # but then we check and see if this feature matches any of the ones
        # that we ~may~ want to 'jitter' ...

        for iTuple in range(len(dataTypeList)):
            aTuple = dataTypeList[iTuple]
            dataType = aTuple[0]
            if (featName.startswith(dataType)):
                iPlatFeat = iPlatFeatList[iTuple]
                if (iPlatFeat >= 0):
                    maxJitter = aTuple[2]
                    keyWord = aTuple[3]
                    maxCutoff = aTuple[4]

                    # print featName, aTuple

                    vDict = {}
                    maxR = 0
                    numV = 0
                    for iCol in range(numCol):
                        curVal = dataMatrix[iRow][iCol]
                        if (curVal != NA_VALUE):
                            numV += 1
                            if curVal in vDict:
                                vDict[curVal] += 1
                                if (vDict[curVal] > maxR):
                                    maxR = vDict[curVal]
                            else:
                                vDict[curVal] = 1

                    addJitter = 0
                    if (maxR > (numV / 10)):
                        print " recommend adding jitter ... "
                        print featName, aTuple
                        # print vDict
                        print maxR, min(vDict), max(vDict)
                        addJitter = 1

                    if (addJitter):
                        for iCol in range(numCol):
                            curVal = dataMatrix[iRow][iCol]
                            if (curVal == NA_VALUE):
                                outMatrix[iRow][iCol] = NA_VALUE
                            else:
                                try:
                                    if (dataMatrix[iPlatFeat][iCol].find(keyWord) > 0):
                                        newVal = curVal + \
                                            (maxJitter * 2 *
                                             (random.random() - 0.5))
                                        if (newVal < 0):
                                            newVal = abs(newVal)
                                        if (newVal > maxCutoff):
                                            newVal = maxCutoff - \
                                                (newVal - maxCutoff)
                                        outMatrix[iRow][iCol] = newVal
                                        numDiff += 1
                                    else:
                                        outMatrix[iRow][iCol] = curVal
                                except:
                                    print iPlatFeat, iCol, dataMatrix[iPlatFeat][iCol], keyWord
                                    sys.exit(-1)

    numTot = numRow * numCol
    print " "
    print " number of samples altered ..... %8d " % numDiff
    print " number of samples unchanged ... %8d " % (numTot - numDiff)
    print " fraction of samples altered ... %.2f " % (float(numDiff) / float(numTot))

    if (numDiff == 0):
        print " ERROR ??? jitterTSV did not affect ANY samples ??? is there a bug ??? "

    outD['dataMatrix'] = outMatrix

    print " "
    print " ready to write output file ... ", outFile
    tsvIO.writeTSV_dataMatrix(outD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
