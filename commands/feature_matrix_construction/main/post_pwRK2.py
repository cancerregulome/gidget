#!/usr/bin/env python

import argparse
import commands
import math
import os
import os.path
import sys
import time

import miscIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getNumFeat(featureMatrixFile):

    fh = file(featureMatrixFile)
    numLines = miscIO.num_lines(fh)
    numFeat = numLines - 1
    fh.close()

    return (numFeat)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getNumSamples(featureMatrixFile):

    fh = file(featureMatrixFile)
    numCols = miscIO.num_cols(fh, '\t')
    numSamples = numCols - 1
    fh.close()

    return (numSamples)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

BIG_DISTANCE = 500000000

def getGenomicDistance(aName, bName):

    aTokens = aName.split(':')

    if (len(aTokens) < 4):
        return (BIG_DISTANCE)

    if (aTokens[3] == ''):
        return (BIG_DISTANCE)

    bTokens = bName.split(':')
    if (bTokens[3] == ''):
        return (BIG_DISTANCE)

    if (aTokens[3] != bTokens[3]):
        return (BIG_DISTANCE)

    try:
        aStart = int(aTokens[4])
        bStart = int(bTokens[4])
    except:
        return (BIG_DISTANCE)

    if (aTokens[5] == ''):
        aStop = aStart
    else:
        aStop = int(aTokens[5])
    if (bTokens[5] == ''):
        bStop = bStart
    else:
        bStop = int(bTokens[5])

    iStart = min(aStart, bStart)
    if (iStart == aStart):
        jStart = bStart
        iStop = aStop
        jStop = bStop
    else:
        jStart = aStart
        iStop = bStop
        jStop = aStop

    if (jStop < iStop):
        return (0)
    elif (jStart < iStop):
        return (0)
    elif (jStart > iStop):
        return (jStart - iStop)
    else:
        # we really should not get here, but ...
        return (BIG_DISTANCE)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# define a feature "type" based on the first 6 characters, eg N:METH


def getFeatTypesCounts(tsvFile):

    featTypesCounts = {}
    fh = file(tsvFile)

    firstLine = 1
    for aLine in fh:
        if (firstLine):
            firstLine = 0
        else:
            curType = aLine[:6]
            if (curType not in featTypesCounts):
                featTypesCounts[curType] = 1
            else:
                featTypesCounts[curType] += 1

    fh.close()
    print " featTypesCounts : ", featTypesCounts

    return (featTypesCounts)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getBonfCorr(aType, bType, featTypesCounts):

    aCounts = featTypesCounts[aType]
    bCounts = featTypesCounts[bType]

    if (aType != bType):
        abCounts = aCounts * bCounts
    else:
        abCounts = aCounts * (aCounts - 1) / 2

    logB = math.log10(abCounts)
    return (logB)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# this function post-processed the outputs of Roger Kramer's pairwise code
#

if __name__ == "__main__":

    if (len(sys.argv) != 5):
        print " Usage : %s <scratch-dir> <tsv-File> <iOne> <BC_threshold> " % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    print " "
    print " in post_pwRK2b ... "
    print "     scratch directory: ", sys.argv[1]
    print "     tsv file: ", sys.argv[2]
    print "     iOne: ", sys.argv[3]
    print "     BC_threshold: ", sys.argv[4]
    print " "

    sDir = sys.argv[1]
    if (sDir[-1] != "/"):
        sDir += "/"

    tsvFile = sys.argv[2]

    iOne = int(sys.argv[3])
    useBC_threshold = float(sys.argv[4])
    if (useBC_threshold < 1.):
        logP_BC = -1. * math.log10(useBC_threshold)
        print " --> setting a threshold on Bonferroni-corrected p-values: ", useBC_threshold, logP_BC
    else:
        print " --> NOT setting a threshold on Bonferroni-corrected p-values "

    featTypesCounts = getFeatTypesCounts(tsvFile)
    numFeat = getNumFeat(tsvFile)
    numSamp = getNumSamples(tsvFile)

    print " "
    print " <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><> "
    print " "
    print " "
    print numFeat, numSamp
    print featTypesCounts

    ## new 04apr14 ... still having NFS latency problems ...
    time.sleep ( 30 )

    featTypesList = featTypesCounts.keys()
    featTypesList.sort()
    print featTypesList
    numFeatTypes = len(featTypesList)

    shortTypes = []
    for iF in range(numFeatTypes):
        curType = featTypesList[iF]
        sType = curType[0] + curType[2:]
        shortTypes += [sType]
    print shortTypes

    if (iOne == -1):
        subFh = [0] * numFeatTypes
        for iF in range(numFeatTypes):
            subFh[iF] = [0] * numFeatTypes
            for jF in range(iF, numFeatTypes):
                oFile = sDir + "post_proc_all." + \
                    shortTypes[iF] + "." + shortTypes[jF] + ".tmp"
                # print oFile
                subFh[iF][jF] = file(oFile, 'w')

    logFilename = sDir + "post_proc_all.log"
    print " opening output log file <%s> " % logFilename
    fhLog = file(logFilename, 'w')

    oFile = sDir + "post_proc_all.tsv"
    print " opening output file     <%s> " % oFile
    fhOut = file(oFile, 'w')

    print " "
    print " "

    numLinesOut = 0
    numDQ = 0

    if (iOne == -1):
        iFeat = 0
    else:
        iFeat = iOne

    iFirst = 1
    done = 0
    while not done:

        # we either just keep incrementing iFeat until we don't find any more
        # files ...
        inFile = sDir + "%d.pw" % iFeat
        try:
            print " opening input file <%s> " % inFile
            fhIn = file(inFile)
        except:
            print " --> FAILED to open input file <%s> " % inFile
            done = 1
            continue

        # or if we are definitely only processing one, we are done after one
        # loop
        if (iFeat == iOne):
            done = 1

        # test to see if we can read the file properly ...
        # BUT do this only if we're just reading a single file ...
        if (not iFirst):
            if (iFeat == iOne):
                seemsOK = 0
            else:
                seemsOK = 1
        else:
            seemsOK = 0

        sleepTime = 0
        while not seemsOK:
            if (sleepTime == 0):
                print " testing whether <%s> seems ok or not ... " % inFile
            aLine = fhIn.readline()
            if (len(aLine) > 2):
                print " seem to have something "
                print aLine
                seemsOK = 1
            else:
                if (sleepTime > 30):
                    if (iFeat == iOne):
                        print " BAILING ... nothing to post process here !!! "
                        sys.exit(-1)
                    else:
                        print " assuming that we can continue ... "
                        seemsOK = 1
                if (sleepTime == 0):
                    print " empty file ??? ", inFile
                time.sleep(1)
                sleepTime += 1
            fhIn.close()
            fhIn = file(inFile, 'r')

        iFirst = 0

        if (iFeat % 10000 == 0):
            print " feature # ", iFeat

        # NEW TEST 04apr14 ... read through the entire file to try and
        # check for truncation problems ...
        ## print " NEW TESTING FOR FILE COMPLETENESS !!! ", inFile
        fileGood = 0
        numRetry = 0
        while ( not fileGood ):
            fhIn.close()
            fhIn = file(inFile, 'r')
            bailFlag = 0
            numLines = 0
            keepReading = 1
            while ( keepReading ):
                aLine = fhIn.readline()
                numLines += 1
                aLine = aLine.strip()
                if ( len(aLine) == 0 ):
                    keepReading = 0
                    continue
                if ( aLine.startswith("#") ): continue
                tokenList = aLine.split('\t')
                if ( len(tokenList)>1 and len(tokenList)<10 ):
                    bailFlag = 1
                    print " BAILING ... RETRY !!! ", numLines, inFile, tokenList, numRetry
                    fhIn.close()
                    time.sleep ( 2 )
                    fhIn = file(inFile, 'r')
                    numLines = 0
                    numRetry += 1
                if ( numRetry > 3 ):
                    print " too many retries ... ", numLines, inFile, numRetry
                    keepReading = 0
                    fileGood = 1
                    bailFlag = 0
            if ( not bailFlag ):
                fileGood = 1
                ## print "         YAY ", numLines, inFile
                fhIn.close()
                fhIn = file(inFile, 'r')


        # print " beginning to loop over input lines ... "
        for aLine in fhIn:

            # print aLine
            if (aLine[0] == "#"):
                continue

            # each line should look something like this:
            # <featA> <featB> <??>  +0.753   186   +9.236   0   -0.000   0   -0.000   <*>
            # and note that the 4th column could say "nan"

            aLine = aLine.strip()
            tokenList = aLine.split('\t')

            # this should not happen and yet it does sometimes,
            # when a file has gotten truncated ...
            if ( len(tokenList) < 10 ): 
                print " "
                print " WARNING !!! truncated file ??? "
                print len(tokenList), tokenList
                print " "
                continue


            aFeat = tokenList[0]
            bFeat = tokenList[1]
            # print aFeat, bFeat
            # print tokenList

            aType = aFeat[0] + aFeat[2:6]
            bType = bFeat[0] + bFeat[2:6]
            # print aType, bType

            if (iOne == -1):
                iF = shortTypes.index(aType)
                jF = shortTypes.index(bType)
                # print iF, jF
                if (jF < iF):
                    kF = jF
                    jF = iF
                    iF = kF
                    # print iF, jF

            if (tokenList[3].find("nan") >= 0):
                rhoString = "NA"
            else:
                try:
                    rho = float(tokenList[3])
                    rhoString = "%.2f" % rho
                    rho = float(rhoString)
                except:
                    rhoString = "NA"

            try:
                num = int(tokenList[4])
                logP = float(tokenList[5])
                nA = int(tokenList[6])
                pA = float(tokenList[7])
                nB = int(tokenList[8])
                pB = float(tokenList[9])
            except:
                print " "
                print " WARNING !!! truncated file ??? "
                print len(tokenList), tokenList
                print " "
                continue

            # rules for disqualifying this ...
            dqFlag = 0

            abDist = getGenomicDistance(aFeat, bFeat)

            logBonf = getBonfCorr(aFeat[:6], bFeat[:6], featTypesCounts)
            blogP = logP - logBonf
            if (blogP < 0):
                blogP = 0.
            if (useBC_threshold < 1.):
                if (blogP < logP_BC):
                    dqFlag = 1

            if ( 0 ):
                if (num < 10): dqFlag = 1

            if (rhoString != "NA"):
                if ((logP > 299) and (abs(float(rhoString)) < 0.1)):
                    dqFlag = 1
            # added this on 12jun13 ...
            # --> made some modifications on 05sep13 ...
            if (rhoString != "NA"):
                if (abs(rho) >= 0.998 and not dqFlag):

                    # if the correlation is perfect (+/-1), then this is probably not
                    # an "interesting" pair -- specifically if it is a GNAB/GNAB pair
                    # or if it involves a CLIN or SAMP feature
                    # ~except~ if it is a mutation feature and the two genes are different
                    if (aType == "BGNAB" and bType == "BGNAB"):
                        aTokens = aFeat.split(':')
                        bTokens = bFeat.split(':')
                        if (aTokens[2] == bTokens[2]):
                            dqFlag = 1
                    elif (aType == "NGNAB" and bType == "NGNAB"):
                        aTokens = aFeat.split(':')
                        bTokens = bFeat.split(':')
                        if (aTokens[2] == bTokens[2]):
                            dqFlag = 1

                    if ( 0 ):
                        if ( not dqFlag ):
                            if (aType[1:] == "CLIN"):
                                dqFlag = 1
                            elif (bType[1:] == "CLIN"):
                                dqFlag = 1
                            elif (aType[1:] == "SAMP"):
                                dqFlag = 1
                            elif (bType[1:] == "SAMP"):
                                dqFlag = 1

            # do not write out if this line has been "disqualified" ...

            if (dqFlag):
                numDQ += 1
                fhLog.write(
                    " not writing out: %s\t%s\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\t%d\t%.1f\t%d\t%.1f\t%9d\n" %
                    (inFile, aFeat, bFeat, rhoString, num, logP, logBonf, blogP, nA, pA, nB, pB, abDist))

            else:

                outString = ""
                if (aFeat[2:] < bFeat[2:]):
                    outString += "%s\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\t%d\t%.1f\t%d\t%.1f\t%9d\n" % \
                        (aFeat, bFeat, rhoString, num, logP,
                         logBonf, blogP, nA, pA, nB, pB, abDist)
                else:
                    outString += "%s\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\t%d\t%.1f\t%d\t%.1f\t%9d\n" % \
                        (bFeat, aFeat, rhoString, num, logP,
                         logBonf, blogP, nB, pB, nA, pA, abDist)

                fhOut.write("%s" % outString)
                if (iOne == -1):
                    subFh[iF][jF].write("%s" % outString)
                numLinesOut += 1
                if (numLinesOut % 1000000 == 0):
                    print "     number of output pairs : ", numLinesOut

        fhIn.close()
        iFeat += 1

    print " "
    print " FINISHED ... ", iFeat, numLinesOut, numDQ
    print " "

    fhLog.write(" ")
    fhLog.write(" FINISHED ...  %d  %d  %d " % (iFeat, numLinesOut, numDQ))
    fhLog.write(" ")

    fhOut.close()
    fhLog.close()


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
