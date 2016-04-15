# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

import chrArms
import miscTCGA
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

global armLabels
armLabels = chrArms.arms_hg19.keys()
armLabels.sort()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getChrArmFromRowLabel ( oneRowLabel ):

    # example rowLabel : N:CNVR:PRDM16:chr1:3218000:3258999::
    tokenList = oneRowLabel.split(':')
    chrName = tokenList[3][3:]
    segStart = int(tokenList[4])
    segStop = int(tokenList[5])
    segLen = (segStop - segStart)
    chrP = chrName + "p"
    chrQ = chrName + "q"
    inP = 0
    inQ = 0
    iA = -1

    midSeg = (segStart + segStop) / 2

    if (0):
        print " "
        print " "
        print oneRowLabel
        print segStart, segStop, segLen, midSeg
        print chrP
        print chrQ
        print chrArms.arms_hg19[chrP]
        print chrArms.arms_hg19[chrQ]

    try:
        # print " comparing %d to %d " % ( segStop, chrArms.arms_hg19[chrP][1]
        # )
        if (segStop <= chrArms.arms_hg19[chrP][1]):
            inP = 1
            iA = armLabels.index(chrP)
            # print " --> got iA=%d " % iA
    except:
        doNothing = 1

    try:
        # print " comparing %d to %d " % ( segStart, chrArms.arms_hg19[chrQ][1]
        # )
        if (segStart >= chrArms.arms_hg19[chrQ][0]):
            inQ = 1
            iA = armLabels.index(chrQ)
            # print " --> got iA=%d " % iA
    except:
        doNothing = 1

    if (iA < 0):
        try:
            # print " comparing %d to %d " % ( midSeg,
            # chrArms.arms_hg19[chrP][1] )
            if (midSeg <= chrArms.arms_hg19[chrP][1]):
                inP = 1
                iA = armLabels.index(chrP)
                # print " --> got iA=%d " % iA
        except:
            doNothing = 1
        try:
            # print " comparing %d to %d " % ( midSeg,
            # chrArms.arms_hg19[chrQ][1] )
            if (midSeg >= chrArms.arms_hg19[chrQ][0]):
                inQ = 1
                iA = armLabels.index(chrQ)
                # print " --> got iA=%d " % iA
        except:
            doNothing = 1

    if (iA < 0):
        print " still nothing ??? "
        print oneRowLabel
        print segStart, segStop, segLen, midSeg
        print chrP, chrQ
        print chrArms.arms_hg19[chrP]
        print chrArms.arms_hg19[chrQ]
        sys.exit(-1)

    return (iA, segLen)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def addCINfeature(dataD, fType):

    print " "
    print " in addCINfeature ... "

    # the feature matrix has thousands of features x hundreds of patients
    rowLabels = dataD['rowLabels']
    colLabels = dataD['colLabels']
    numRow = len(rowLabels)
    numCol = len(colLabels)
    dataMatrix = dataD['dataMatrix']
    print " %d rows x %d columns " % (numRow, numCol)
    # print rowLabels[:5]
    # print rowLabels[-5:]

    # the custom features are assumed to be derived in some way
    # from existing features ...
    exFNames = [fType]
    numExF = len(exFNames)
    numExF2 = [0] * numExF
    exFRows = [-1] * numExF

    print " looking through labels for ", exFNames

    for iRow in range(numRow):
        # BUT ... we will exclude X or Y chromosome features entirely
        if (rowLabels[iRow].find("chrX") >= 0):
            continue
        if (rowLabels[iRow].find("chrY") >= 0):
            continue

        # AND we will also exclude the Gistic features ...
        if (rowLabels[iRow].find("Gistic") >= 0):
            continue

        for iEx in range(numExF):
            if (exFNames[iEx] in rowLabels[iRow]):
                # print iRow, rowLabels[iRow], iEx, exFNames[iEx]
                if (numExF2[iEx] == 0):
                    exFRows[iEx] = [iRow]
                    numExF2[iEx] = 1
                else:
                    exFRows[iEx] += [iRow]
                    numExF2[iEx] += 1
                    # print " already found a match ??? ", exFNames[iEx], rowLabels[exFRows[iEx]]
                    # sys.exit(-1)

    if (min(numExF2) == 0):
        print " WARNING !!! failed to find one of the existing features ??? ", numExF2, exFNames
        print " --> no additional features will be added "
        return (dataD)

    ## the output below should look something like this ...
    ##  A  ['N:CNVR:']
    ##  B  [3636, 3637, 3638, 3639, 3640] [6517, 6518, 6519, 6520, 6521]
    ##  C  [2886]
    print " "
    print " feature names and rows: "
    print " A ", exFNames
    print " B ", exFRows[0][:5], exFRows[0][-5:]
    print " C ", numExF2
    print " "

    # for stad.seq.test.TP.tsv, it finds 3008 CNVR features ...

    # first we want to compute arm-level values for each sample
    numArms = len(chrArms.arms_hg19)

    # now we have armLabels, eg '20q'
    # as well as coordinates, eg (27500000, 63025520)
    print numArms, armLabels[:5]
    print chrArms.arms_hg19[armLabels[0]]

    # we need a matrix to keep track of sample-specific arm-level stats
    print numArms, numCol
    s1Mat = [0] * numArms
    s2Mat = [0] * numArms
    for iA in range(numArms):
        s1Mat[iA] = [0] * numCol
        s2Mat[iA] = [0] * numCol

    # first let's loop over all of the features and accumulate arm-level stats ...
    # outer loop is over CNVR features ...
    print " --> looping over %d features " % (len(exFRows[0]))
    for iF in range(len(exFRows[0])):

        ## figure out the chromosome arm and segment length
        iRow = exFRows[0][iF]
        (iA, segLen) = getChrArmFromRowLabel(rowLabels[iRow])

        if (iF % 100 == 0):
            print iF, iRow, rowLabels[iRow], segLen, iA, armLabels[iA]

        # inner loop is over samples ...
        for iC in range(numCol):
            if (dataMatrix[iRow][iC] == NA_VALUE):
                continue
            # print " qqqq  %6d %6d %11.2f " % ( iRow, iC, dataMatrix[iRow][iC]
            # )
            ## keep track of: a) copy-number value x segLen
            ##                b) segLen
            s1Mat[iA][iC] += (dataMatrix[iRow][iC] * segLen)
            s2Mat[iA][iC] += (segLen)

    print " "
    print " "
    print " "

    # now we can compute a weighted average for each arm (for each sample) ...
    maxPos = [-1] * numArms
    maxNeg = [1] * numArms
    for iA in range(numArms):
        for iC in range(numCol):
            if (s2Mat[iA][iC] > 0):
                s1Mat[iA][iC] /= s2Mat[iA][iC]
                if (s1Mat[iA][iC] > maxPos[iA]): maxPos[iA] = s1Mat[iA][iC]
                if (s1Mat[iA][iC] < maxNeg[iA]): maxNeg[iA] = s1Mat[iA][iC]
            else:
                s1Mat[iA][iC] = NA_VALUE
        if (maxPos[iA] > maxNeg[iA]):
            print " range of values for each arm : ", iA, armLabels[iA], maxNeg[iA], maxPos[iA]

    print " "
    print " "
    print " "

    # and based on these we compute an arm-level CIN feature for
    # each sample ...

    numNewFeat = 6
    newNames = [''] * numNewFeat
    newNames[0] = "N:SAMP:CIN_arm_del:::::"
    newNames[1] = "N:SAMP:CIN_arm_amp:::::"
    newNames[2] = "N:SAMP:CIN_arm_tot:::::"
    newNames[3] = "N:SAMP:CIN_foc_del:::::"
    newNames[4] = "N:SAMP:CIN_foc_amp:::::"
    newNames[5] = "N:SAMP:CIN_foc_tot:::::"

    ## we are creating 6 new features, for each one allocate
    ## a vector of NA's ...
    newVecs = [0] * numNewFeat
    for iNew in range(numNewFeat):
        newVecs[iNew] = [NA_VALUE] * numCol

    # for the arm-level stuff, we are using a threshold of 
    # essentially ZERO ...
    dThresh = 0.0001

    # outer loop is over samples ...
    for iC in range(numCol):

        # inner loop is over chromosome arms ...
        # the overall value is going to be a summed metric over all 
        # chromosome arms ...
        for iA in range(numArms):
            if (s1Mat[iA][iC] == NA_VALUE): continue

            ## deletions ...
            if (s1Mat[iA][iC] < -dThresh):
                if (newVecs[0][iC] == NA_VALUE): newVecs[0][iC] = 0
                newVecs[0][iC] += abs(s1Mat[iA][iC])

            ## amplifications ...
            elif (s1Mat[iA][iC] > dThresh):
                if (newVecs[1][iC] == NA_VALUE): newVecs[1][iC] = 0
                newVecs[1][iC] += abs(s1Mat[iA][iC])

        ## now we are going to sum the aggregated amplification and the
        ## aggregated deletion metrics ...
        if (newVecs[0][iC] != NA_VALUE): 
            newVecs[2][iC] = newVecs[0][iC]
        if (newVecs[1][iC] != NA_VALUE):
            if (newVecs[2][iC] == NA_VALUE): 
                newVecs[2][iC] = newVecs[1][iC]
            else:
                newVecs[2][iC] += newVecs[1][iC]


    ## now we are going to set a more significant threshold for
    ## looking at focal amplifications and deletions ...
    tmpVec = [0] * numCol
    dThresh = 0.7

    # now we loop over all of the features and accumulate focal statistics
    print " now for focal stats ... "

    for iF in range(len(exFRows[0])):
        iRow = exFRows[0][iF]
        (iA, segLen) = getChrArmFromRowLabel(rowLabels[iRow])

        for iC in range(numCol):
            dVal = dataMatrix[iRow][iC]
            if (dVal == NA_VALUE): continue

            if (newVecs[3][iC] == NA_VALUE): newVecs[3][iC] = 0
            if (newVecs[4][iC] == NA_VALUE): newVecs[4][iC] = 0
            if (newVecs[5][iC] == NA_VALUE): newVecs[5][iC] = 0

            # subtract the arm-level average ...
            dVal -= s1Mat[iA][iC]

            # if the segment copy-number exceeds the threshold,
            # then add this segment length ...
            if (dVal <= -dThresh):
                newVecs[3][iC] += (segLen)
                newVecs[5][iC] += (segLen)
            elif (dVal >= dThresh):
                newVecs[4][iC] += (segLen)
                newVecs[5][iC] += (segLen)
            tmpVec[iC] += segLen

    print " "
    print " "
    print " "

    print " "
    print " normalize by total segment length : "

    # and then normalize by the total segment length
    # (the values are very small, so multiplying by 10000 ...)
    for iC in range(numCol):
        if (tmpVec[iC] > 0):
            tmpVec[iC] = float(tmpVec[iC]) / 10000.
            newVecs[3][iC] /= float(tmpVec[iC])
            newVecs[4][iC] /= float(tmpVec[iC])
            newVecs[5][iC] /= float(tmpVec[iC])

    print " "
    print " "
    print " "

    for iC in range(numCol):
        print " %4d \t %g \t %g \t %g \t %g \t %g \t %g " % \
            (iC, newVecs[0][iC], newVecs[1][iC], newVecs[2][iC],
             newVecs[3][iC], newVecs[4][iC], newVecs[5][iC])

    # now we have the new data ...
    print " "
    print " adding these new features: ", newNames
    print " "
    newRowLabels = rowLabels + newNames
    print len(rowLabels), len(newRowLabels)

    newMatrix = dataMatrix + newVecs
    print len(dataMatrix), len(newMatrix)

    newD = {}
    newD['rowLabels'] = newRowLabels
    newD['colLabels'] = colLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = newMatrix

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

    # add new custom features ...
    dataD = addCINfeature(dataD, "N:CNVR:")

    # and write the matrix back out
    tsvIO.writeTSV_dataMatrix(dataD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
