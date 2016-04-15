# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import numpy
import sys

# these are my local ones
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
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


def checkMethCnvr(dataD):

    print " "
    print " ************************************************************* "
    print " ************************************************************* "
    print " "
    print " in checkMethCnvr ... "

    # check that the input feature matrix looks ok ...
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in checkMethCnvr ??? bad data ??? "
        return (dataD)

    # next, we need to find all of the METH features and all of the CNVR
    # features
    print " --> assigning meth / cnvr flags ... "
    isMeth = setFeatBits(rowLabels, "N:METH:", "", "")
    isCnvr = setFeatBits(rowLabels, "N:CNVR:", "", "Gistic")

    # now we need to map each of the METH features to an appropriate CNVR feature
    # this is pretty SLOW ...
    # takes 30-60 sec to map 1000 METH features to one of ~6000 CNVR features
    mapVec = numpy.zeros(numRow, dtype=numpy.int)

    numMatch = 0
    numNoMatch = 0

    print " --> now setting up meth / cnvr mapping ... "
    for iR in range(numRow):

        if (iR % 1000 == 0):
            print iR, numRow, numMatch, numNoMatch

        # if this is a METH feature, find the matching CNVR ...
        if (isMeth[iR]):
            mapVec[iR] = -1
            methLabel = rowLabels[iR]
            methTokens = methLabel.split(':')
            methChrName = methTokens[3].upper()
            methPos = int(methTokens[4])

            # avoid X and Y chromosome genes ...
            if (methChrName.endswith("X")):
                continue
            if (methChrName.endswith("Y")):
                continue

            for jR in range(numRow):
                if (mapVec[iR] >= 0):
                    continue
                if (isCnvr[jR]):
                    cnvrLabel = rowLabels[jR]
                    cnvrTokens = cnvrLabel.split(':')
                    cnvrChrName = cnvrTokens[3].upper()
                    if (methChrName != cnvrChrName):
                        continue
                    cnvrStart = int(cnvrTokens[4])
                    if (methPos < cnvrStart):
                        continue
                    cnvrStop = int(cnvrTokens[5])
                    if (methPos > cnvrStop):
                        continue
                    # print " found match! ", methLabel, cnvrLabel, iR, jR
                    mapVec[iR] = jR
                    numMatch += 1

            if (mapVec[iR] == -1):
                # print " failed to find a match ??? ", methLabel
                numNoMatch += 1

    print numMatch, numNoMatch, numRow

    # now we need to actually loop over the data ...

    dMat = dataD['dataMatrix']
    cnvrThreshold = 2.

    print " --> now checking for deletions ... "
    numReset = 0

    sum0 = 0
    num0 = 0

    sumAmp = 0
    numAmp = 0

    sumDel = 0
    numDel = 0

    sumAll = 0
    numAll = 0

    for iR in range(numRow):

        if (iR % 1000 == 0):
            print iR, numRow, numReset
            if (numDel > 0):
                print "     deletions      ", numDel, float(sumDel) / float(numDel)
            if (num0 > 0):
                print "     neutral        ", num0,   float(sum0) / float(num0)
            if (numAmp > 0):
                print "     amplifications ", numAmp, float(sumAmp) / float(numAmp)
            if (numAll > 0):
                print "     all            ", numAll, float(sumAll) / float(numAll)

        # iR is the methylation feature row
        # jR is the corresponding cnvr feature row
        if (isMeth[iR]):
            jR = mapVec[iR]
            if (jR < 0):
                continue

            for iCol in range(numCol):
                if (dMat[iR][iCol] != NA_VALUE):
                    if (dMat[jR][iCol] != NA_VALUE):

                        numAll += 1
                        sumAll += dMat[iR][iCol]

                        # if this patient has a deletion, then reset the meth value to NA
                        # ( also, keep track of avg beta values in deletions, amplifications, and copy-number neutral regions )
                        try:
                            if (dMat[jR][iCol] <= -cnvrThreshold):
                                print "     resetting ", iR, jR, iCol, dMat[iR][iCol], dMat[jR][iCol]
                                numDel += 1
                                sumDel += dMat[iR][iCol]
                                dMat[iR][iCol] = NA_VALUE
                                numReset += 1
                            elif (abs(dMat[jR][iCol]) < 0.25):
                                num0 += 1
                                sum0 += dMat[iR][iCol]
                            elif (dMat[jR][iCol] >= cnvrThreshold):
                                numAmp += 1
                                sumAmp += dMat[iR][iCol]
                        except:
                            print " ERROR ??? ", iR, jR, rowLabels[iR], rowLabels[jR]
                            print dMat[iR][iCol], dMat[jR][iCol]
                            sys.exit(-1)

    print " "
    print " finished ... ", iR, numRow, numReset
    print " total # of samples reset: %d out of %d " % (numReset, numAll)
    if (numDel > 0):
        print "     deletions (reset)          ", numDel, float(sumDel) / float(numDel)
    if (num0 > 0):
        print "     neutral                    ", num0,   float(sum0) / float(num0)
    if (numAmp > 0):
        print "     amplifications (not reset) ", numAmp, float(sumAmp) / float(numAmp)
    if (numAll > 0):
        print "     all                        ", numAll, float(sumAll) / float(numAll)

    dataD['dataMatrix'] = dMat

    print " "
    print " --> finished with checkMethCnvr ... "
    print " "

    return (dataD)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 3):
            inFile = sys.argv[1]
            outFile = sys.argv[2]
            do_checkMethCnvr = 1
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

    # we want to "check" for "deleted" METH probes
    if (do_checkMethCnvr):
        newD = checkMethCnvr(testD)
        ## tsvIO.writeTSV_dataMatrix ( newD, 0, 0, outFile )
        testD = newD

    # and finally write it out ...
    tsvIO.writeTSV_dataMatrix(testD, 0, 0, outFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
