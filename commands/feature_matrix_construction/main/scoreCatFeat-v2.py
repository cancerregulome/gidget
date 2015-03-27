
import argparse
import commands
import getpass
import itertools
import numpy
import os
import os.path
import sys
import time

from  env import gidgetConfigVars

import miscIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

debugFlag = 0

# order returns the order of each element in x as a list


def order(x):
    if (debugFlag):
        print " in FUNC order() ... "
    L = len(x)
    rangeL = range(L)
    z = itertools.izip(x, rangeL)
    z = itertools.izip(z, rangeL)    # avoid problems with duplicates
    D = sorted(z)
    return [d[1] for d in D]

# rank returns the rankings of the elements in x as a list


def rank(x):
    if (debugFlag):
        print " in FUNC rank() ... "
    L = len(x)
    ordering = order(x)
    ranks = [0] * L
    for i in range(L):
        ranks[ordering[i]] = i
    return ranks

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# new 28-jan-2013 from
# http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python


def rank_simple(vector):
    return sorted(range(len(vector)), key=vector.__getitem__)


def rankdata(a):
    n = len(a)
    ivec = rank_simple(a)
    svec = [a[rank] for rank in ivec]
    sumranks = 0
    dupcount = 0
    newarray = [0] * n
    for i in xrange(n):
        sumranks += i
        dupcount += 1
        if i == n - 1 or svec[i] != svec[i + 1]:
            averank = sumranks / float(dupcount) + 1
            for j in xrange(i - dupcount + 1, i + 1):
                newarray[ivec[j]] = averank
            sumranks = 0
            dupcount = 0

    print " returning from rankdata ... ", min(newarray), max(newarray)

    return newarray

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def countSamples(tokenList):

    numSamp = 0
    for aTok in tokenList:
        if (aTok != "NA"):
            numSamp += 1

    return (numSamp)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getClinSampFeat(featureMatrixFile, min_samples):

    fh = file(featureMatrixFile)

    indexList = []
    featList = []
    typeList = [ ":CLIN:", ":SAMP:" ]
    ## typeList = [ ":GNAB:" ]
    ## typeList = [ ":CLIN:", ":SAMP:", ":GNAB:", ":GEXP:", ":METH:", ":CNVR:", ":MIRN:", ":RPPA:" ]

    lineNo = 0
    for aLine in fh:
        aLine = aLine.strip()
        if (lineNo > 0):
            tokenList = aLine.split('\t')
            featName = tokenList[0]

            found = 0
            for aType in typeList:
                if ( not found ):
                    if ( featName.find(aType) > 0 ):
                        found = 1
                        numSamp = countSamples(tokenList)
                        if ( numSamp >= min_samples ):
                            indexList += [lineNo - 1]
                            featList += [featName]
                        else:
                            print " skipping feature <%s> due to low counts (%d) " % (featName, numSamp)

        lineNo += 1

    fh.close()

    return (indexList, featList)

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

def getGolemInfo ( infoStr, tagStr ):

    tagStr = '"' + tagStr + '"'
    ## print " in getGolemInfo ... <%s> " % tagStr
    i1 = infoStr.find(tagStr)
    if ( i1 < 0 ): return ( "NA" )
    infoStr = infoStr[i1:]
    i1 = infoStr.find(": ")
    infoStr = infoStr[i1+2:]
    i1 = infoStr.find(",")
    infoStr = infoStr[:i1]
    ## print "     tagStr --> <%s> " % infoStr
    if ( infoStr.startswith('"') ): infoStr = infoStr[1:]
    if ( infoStr.endswith('"') ): infoStr = infoStr[:-1]
    if ( infoStr.endswith('}') ): infoStr = infoStr[:-1]
    if ( infoStr.endswith('\n') ): infoStr = infoStr[:-1]
    print " returning from getGolemInfo ... <%s> <%s> " % ( tagStr, infoStr )
    return ( infoStr )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getJobId ( output ):

    return ( getGolemInfo ( output, "JobId" ) )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getJobState ( output ):

    return ( getGolemInfo ( output, "State" ) )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getDoneFrac ( output ):

    try:
        numErr = int ( getGolemInfo ( output, "Errored" ) )
        numFin = int ( getGolemInfo ( output, "Finished" ) )
        numTot = int ( getGolemInfo ( output, "Total" ) )
        doneFrac = float ( numErr + numFin ) / float ( numTot )
        print " doneFrac : ", doneFrac, numErr, numFin, numTot
    except:
        print " "
        print " ??? "
        print " failed to get Errored, Finished or Total counts from "
        print output
        print " ??? "
        print " "
        doneFrac = -1.

    return ( doneFrac )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getTypeRanks(aType, tmpDir, indexList, featList):

    print " "
    print " in getTypeRanks ... ", aType

    outNames = []
    dTypeScores = []

    pCounts = {}

    for kk in range(len(indexList)):

        index = indexList[kk]
        featName = featList[kk]

        # first, open the previously generated pairwise file for this index
        # (feature)
        pwFile = tmpDir + ( "/%d.pw" % index )
        print " trying to open <%s> " % pwFile
        try:
            fh = file(pwFile, 'r')
        except:
            print " failed ??? "
            continue
            sys.exit(-1)

        print "         --> reading input file <%s> " % pwFile

        # initialze number of p-values
        pCounts[featName] = 0

        # allocate a vector of zeros
        dTypeVec = numpy.zeros(maxNum)
        iG = 0

        # read through the input file, line by line, and keep only
        # those pairs that involve the current data type

        # each line should look something like this:
        # <featA> <featB>  NC  +0.81  57  7.5  0  300.  0  300.  -

        for aLine in fh:
            if (aLine.startswith("##")):
                continue
            if (aLine.find(aType) >= 0):
                tokenList = aLine.split('\t')
                # check that the # of samples involved in the pairwise test was
                # at least 20 ...
                if (int(tokenList[4]) < 20):
                    continue

                # and then grab the -log(p)
                pValue = float(tokenList[5])
                dTypeVec[iG] = pValue
                iG += 1

        # close the file ...
        fh.close()

        outNames += [featName]

        if (iG > 0):
            # print "         --> got %d p-values " % iG
            pCounts[featName] += iG
            try:
                dTypeVec = dTypeVec[:iG]
                dTypeVec.sort()
                aScore = 0.
                for p in [0.80, 0.85, 0.90, 0.95]:
                    iG = int(p * len(dTypeVec))
                    aScore += dTypeVec[iG]
                # print index, featName, "GEXP", aScore, len(dTypeVec)
                dTypeScores += [aScore]
            except:
                dTypeScores += [0]
        else:
            # print "         --> did NOT get any p-values "
            dTypeScores += [0]

    print " "
    print " got this far ... returning from getTypeRanks "
    print "     names   : ", outNames[:5], outNames[-5:]
    print "     scores  : ", dTypeScores[:5], dTypeScores[-5:]
    if (0):
        dTypeRanks = rank(dTypeScores)
    else:
        dTypeRanks = rankdata(dTypeScores)
    print "     ranks   : ", dTypeRanks[:5], dTypeRanks[-5:]

    print " "
    pKeys = pCounts.keys()
    for ii in range(min(10, len(pKeys))):
        print "         pCounts[%s] = %d " % (pKeys[ii], pCounts[pKeys[ii]])
    print " "

    return (outNames, dTypeScores, dTypeRanks, pCounts)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makeOutFileName(tsvFile):

    ii = len(tsvFile) - 1
    while (tsvFile[ii] != '/'):
        ii -= 1

    # the output file name will look just like the input tsv file name,
    # but it will start with "featScores_" and end with ".txt" rather
    # than ".tsv"
    outName = tsvFile[:ii] + '/' + "featScoresV2_" + tsvFile[ii + 1:-3] + "txt"

    # NEW:
    outName = tsvFile[:-4] + ".featScoresV2.txt"
    return (outName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#

if __name__ == "__main__":

    global maxNum
    maxNum = 10000

    # ALL necessary inputs should be handled using this ArgumentParser ... there shouldn't
    # be any 'left-over' arguments ... any unrecognized command-line inputs will result
    # in an error like:
    # rkpw_list_gen.py: error: unrecognized arguments: abc def

    parser = argparse.ArgumentParser(
        description='Create runlist for pairwise')
    parser.add_argument('--min-ct-cell', '-minct',
                        action='store', default=3, type=int)
    parser.add_argument('--min-mx-cell', '-minmx',
                        action='store', default=3, type=int)
    parser.add_argument('--min-samples', '-M',
                        action='store', default=31, type=int)
    parser.add_argument('--verbosity', '-v',
                        action='store', default=0, type=int)
    parser.add_argument('--tsvFile', '-f', action='store', required=True)
    ## parser.add_argument ( '--runFile', '-r', action='store', required=True )

    args = parser.parse_args()
    print args

    # force user to be using the 'cncrreg' group to run this ...
    if (0):
        cmdString = "newgrp cncrreg"
        print " trying to force group ... "
        (status, output) = commands.getstatusoutput(cmdString)
        print " back from that ... "

    # at this point we should have a Namespace called 'args' that looks something like this:
    # Namespace ( tsvFile=['test.tsv'],
    # runFile=['test.run'],
    ##		   byname=False, input=None,
    # min_ct_cell=5,
    # tail=0, verbosity=0 )

    # get the tsv feature matrix file and also the number of features it
    # contains
    tsvFile = args.tsvFile
    print " input tsv file name <%s> " % tsvFile
    if (not os.path.exists(tsvFile)):
        print " <%s> is not a valid file, exiting ... " % tsvFile
        sys.exit(-1)
    if (not tsvFile.endswith(".tsv")):
        print " <%s> input file should be a TSV file " % tsvFile
        sys.exit(-1)
    if (tsvFile[0] != "/"):
        print " absolute path name for input file <%s> is required " % tsvFile
        sys.exit(-1)
    (indexList, featList) = getClinSampFeat(tsvFile, args.min_samples)

    totNumFeat = getNumFeat(tsvFile)
    maxNum = totNumFeat

    if (len(indexList) < 5):
        print " ERROR ... does not seem worth continuing ... "
        print indexList
        print featList
        sys.exit(-1)

    print " --> number of features : ", len(indexList)
    numSamples = getNumSamples(tsvFile)
    print " --> number of samples  : ", numSamples

    # TODO:FILE_LAYOUT:EXPLICIT
    ## at this point, we can invoke the run-pairwise-v2 script like this:
    ## python ./run-pairwise-v2.py --pvalue 2. --one 24 --forRE \
    ##     --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/ucs/24jun14_27k/ucs.seq.24jun14_27k.TP.tsv 
    ## and then the output would be written to 
    ##     /titan/cancerregulome14/TCGAfmp_outputs/ucs/24jun14_27k/ucs.seq.24jun14_27k.TP.24.all.pwpv.sort

    # create a random name for this particular run ...
    # and then make a subdirectory for the outputs ...
    curJobName = miscIO.make_random_fname()
    print " "
    print " randomly generated job name : <%s> " % curJobName
    print " "

    tmpDir = "%s/%s" % (gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'], curJobName)
    cmdString = "mkdir %s" % tmpDir
    (status, output) = commands.getstatusoutput(cmdString)
    if (not os.path.exists(tmpDir)):
        print " mkdir command failed ??? "
        print cmdString
        sys.exit(-1)

    # open the jobInfo file ...
    jobFile = tmpDir + "/jobInfo.txt"
    try:
        fh = file(jobFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % jobFile
        sys.exit(-1)

    fh.write("tsvFile = %s\n" % args.tsvFile)
    fh.close()

    # now we need to create the pair lists for each feature ...
    numJobs = len(indexList)
    for eachI in indexList:
        listFile = tmpDir + "/%d.list" % eachI
        fh = file(listFile, 'w')
        for eachJ in range(totNumFeat):
            if ( eachI < eachJ ):
                fh.write ("%d %d\n" % ( eachI, eachJ ) )
            elif ( eachJ < eachI ):
                fh.write ("%d %d\n" % ( eachJ, eachI ) )
        fh.close()

    # and then write the runFile for golem ...
    runFile = tmpDir + "/runList.txt"
    try:
        fh = file(runFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % runFile
        sys.exit(-1)

    golempwd = "PASSWD_HERE"
    fhC = file (gidgetConfigVars['TCGAFMP_CLUSTER_HOME'] + "/GOLEMPW", 'r' )
    aLine = fhC.readline()
    fhC.close()
    aLine = aLine.strip()
    golempwd = aLine
    print " got this p ... <%s> " % golempwd
    print " "

    for eachI in indexList:

        outName = tmpDir + "/%d.pw" % eachI
        listFile = tmpDir + "/%d.list" % eachI

        cmdString = "1 ignoreThree.py " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
        cmdString += " --by-index %s " % listFile
        ## cmdString += " --dry-run "
        cmdString += " --p-value 2. "
        cmdString += " --min-ct-cell %d --min-mx-cell %d --min-samples %d " % \
                    ( args.min_ct_cell, args.min_mx_cell, args.min_samples )
        cmdString += " %s  %s  " % ( args.tsvFile, outName )
        fh.write ( "%s\n" % cmdString )

    fh.close()

    ## and then FINALLY we launch the job ...
    print " "
    print " ********************************************* "
    print " Number of jobs about to be launched : ", numJobs
    print " ********************************************* "
    print " (b) TIME ", time.asctime(time.localtime(time.time()))
    print " "

    # ok, now we want to actually launch the jobs ...
    # this command will look something like this:
    # python /<path-to-python-script>/golem.py http://glados.systemsbiology.net:7083 -p <password> \
    #     -L pairwise-2.0.0 -u <user> \
    #     runlist /<path-to-scratch-space>/runList.txt
    cmdString = "python %s/main/golem.py " % gidgetConfigVars['TCGAFMP_ROOT_DIR']
    cmdString += "http://glados.systemsbiology.net:7083 -p " + golempwd + " "
    cmdString += "-L pairwise-2.1.0 -u "
    cmdString += getpass.getuser() + " "
    cmdString += "runlist " + runFile
    print cmdString
    (status, output) = commands.getstatusoutput(cmdString)
    print " status = <%s> " % status
    print " output = <%s> " % output
    print " "
    print " "

    # ------------------------------------------------------------------------------
    # before we get to the post-processing, we need to make sure the job is done ...

    # find the job id in the output above ...
    jobId = getJobId ( output )

    # put together the command to ask if this job is done ...
    cmdString = "python %s/main/golem.py " % gidgetConfigVars['TCGAFMP_ROOT_DIR']
    cmdString += "http://glados.systemsbiology.net:7083 -p " + golempwd + " "
    cmdString += "status " + jobId
    print cmdString

    done = 0
    numAsk = 0
    tTot = 0
    tSleep = 5
    while not done:

        # now we need to keep asking if the job is done ...
        print " --> sleeping ", tSleep
        time.sleep(tSleep)

        tTot += tSleep
        print " --> tTot = ", tTot

        (status, output) = commands.getstatusoutput(cmdString)
        ## print " status = <%s> " % status
        ## print " output = <%s> " % output
        ## print " "

        jobState = getJobState ( output )
        ## print " **************************** ", jobState

        if ( jobState == "COMPLETE" ):
            print "     job COMPLETE !!! "
            done = 1

        if ( jobState == "RUNNING" ):
            doneFrac = getDoneFrac ( output )
            if ( doneFrac > 0. ):
                tSleep = (tTot/doneFrac) / 5.
                ## limit the nap to between 5 and 60 seconds
                tSleep = max(tSleep,5)
                tSleep = min(tSleep,60)
                print "     --> new tSleep = ", tSleep
            else:
                tSleep = 5
                print "     --> using default tSleep = ", tSleep

        numAsk += 1
        if ( numAsk > 1000 ):
            print " "
            print " bailing out ... too many tries !!! "
            print " "
            sys.exit(-1)

    ## check that we have the right # of output files
    numOutFiles = 0
    for aName in os.listdir(tmpDir):
        if (aName.endswith(".pw")): numOutFiles += 1
    print numOutFiles
    if ( numOutFiles != numJobs ):
        print " WARNING: wrong number of output files ??? "
        print numOutFiles, numJobs

    print " should be done !!! ", numOutFiles, numJobs

    # now we are ready for the post-processing ...

    print " "
    print " "

    featScores = {}
    pCounts = {}

    # we are looking for associations with 5 different molecular data types:
    typeList = ["N:GEXP:", "N:RPPA:", "N:METH:", "N:MIRN:", "N:CNVR:"]
    for aType in typeList:
        print " aType : ", aType

        outNames = []

        (outNames, typeScores, typeRanks, pTmp) = getTypeRanks (aType, tmpDir, indexList, featList)

        # at this point we have:
        # names : vector of feature names
        # typeScores : vector of scores (a higher score is better)
        # typeRanks  : vector of ranks (a higher rank is better)
        # pTmp : # of p-values considered for each feature name (this is a
        # dictionary with the feature name as the key)

# for iR in range(len(typeRanks)):
####	    jR = len(typeRanks) - iR - 1
####	    kR = typeRanks.index(jR)
# print iR, jR, kR, outNames[kR], typeScores[kR]
# if ( outNames[kR] in featScores.keys() ):
####	        featScores[outNames[kR]] += [ jR ]
####		pCounts[outNames[kR]] += pTmp[outNames[kR]]
# else:
####		featScores[outNames[kR]] = [ jR ]
####		pCounts[outNames[kR]] = pTmp[outNames[kR]]

        for iR in range(len(outNames)):
            if (outNames[iR] in featScores.keys()):
                featScores[outNames[iR]] += [typeRanks[iR]]
                pCounts[outNames[iR]] += pTmp[outNames[iR]]
            else:
                featScores[outNames[iR]] = [typeRanks[iR]]
                pCounts[outNames[iR]] = pTmp[outNames[iR]]

        # now we have
        # featScores{} : this is now based on the *rank* (rather than the *score* which was based on p-values)
        # pCounts{}    : this keeps track of how many p-values contributed to
        # this rank/score

        print " "
        keyList = featScores.keys()
        for ii in range(min(10, len(keyList))):
            print keyList[ii], featScores[keyList[ii]], pCounts[keyList[ii]]
        print " "

    print " "
    print " "
    print " FINISHED looping over typeList ... "

    if (1):
        print " "
        print " "
        for aName in featScores.keys():
            print aName, featScores[aName], pCounts[aName]

    print " "
    print " "

    # sum up the scores ...
    nameList = featScores.keys()
    sumScores = []
    for aName in nameList:
        aSum = 0
        for aScore in featScores[aName]:
            aSum += aScore
        sumScores += [aSum]

    # also, find the median pCounts value, and reset the scores for those to 0
    pList = []
    for aName in nameList:
        pList += [pCounts[aName]]
    pList.sort()
    nHalf = len(pList) / 2
    pMedian = pList[nHalf]
    pMin = pMedian / 2
    if (pMin == 0):
        pMin = 1
    print " pMin = ", pMin

    print " "
    print " "
    if (1):
        scoreRanks = rank(sumScores)
    else:
        scoreRanks = rankdata(sumScores)
    newScores = [0] * len(sumScores)
    maxScore = len(typeList) * len(nameList)
    for iR in range(len(sumScores)):
        jR = len(sumScores) - iR - 1
        kR = scoreRanks.index(jR)
        aName = nameList[kR]
        # print iR, jR, kR, nameList[kR], sumScores[kR], (
        # float(sumScores[kR])/float(maxScore) )
        if (pCounts[aName] >= pMin):
            # this line looks like this:
            # 57 48724 B_CLIN_person_neoplasm_cancer_status 338 0.140248962656
            print jR, pCounts[aName], aName, sumScores[kR], (float(sumScores[kR]) / float(maxScore))
            newScores[kR] = sumScores[kR]

    print " "
    print " "

    outFile = makeOutFileName(tsvFile)
    print " --> opening output file <%s> " % outFile
    fh = file(outFile, 'w')

    # finally we want to pretty print the output ...
    numOut = 0
    for iR in range(len(sumScores)):
        jR = len(sumScores) - iR - 1
        kR = scoreRanks.index(jR)
        aName = nameList[kR]
        nameTokens = aName.split(':')
        shortName = nameTokens[2]
        featName = aName
        typeName = aName[2:6]
        if (newScores[kR] > 0):
            fh.write("%s\t%s\t%s\t%.3f\n" %
                     (shortName, featName, typeName, newScores[kR]))
            numOut += 1

    if (numOut == 0):
        fh.write(
            "## there were no significant associations between clinical/sample features and molecular features \n")
    fh.close()

    # and we can delete the individual *.pw files ...
    cmdString = "rm -fr %s" % tmpDir
    print cmdString
    ## ( status, output ) = commands.getstatusoutput ( cmdString )

    print " "
    print " "
    print " FINISHED "
    print " "




# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
