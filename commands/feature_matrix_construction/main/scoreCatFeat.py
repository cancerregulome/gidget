
import argparse
import commands
import getpass
import itertools
import numpy
import os
import os.path
import sys
import time

from env import gidgetConfigVars
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

    lineNo = 0
    for aLine in fh:
        aLine = aLine.strip()
        if (lineNo > 0):
            tokenList = aLine.split('\t')
            featName = tokenList[0]
            if (featName.find(":CLIN:") > 0):
                numSamp = countSamples(tokenList)
                if (numSamp >= min_samples):
                    indexList += [lineNo - 1]
                    featList += [featName]
                else:
                    print " skipping feature <%s> due to low counts (%d) " % (featName, numSamp)
            elif (featName.find(":SAMP:") > 0):
                numSamp = countSamples(tokenList)
                if (numSamp >= min_samples):
                    indexList += [lineNo - 1]
                    featList += [featName]
                else:
                    print " skipping feature <%s> due to low counts (%d) " % (featName, numSamp)
        lineNo += 1

    fh.close()

    return (indexList, featList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getNumSamples(featureMatrixFile):

    fh = file(featureMatrixFile)
    numCols = miscIO.num_cols(fh, '\t')
    numSamples = numCols - 1
    fh.close()

    return (numSamples)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# input file is assumed to end in .tsv
# this function checks to see if the binFile exists and is up to date
# with respect to the tsvFile ... if necessary, it will call prep4pairwise
# to create the bin file


def preProcessTSV(tsvFile):

    tsvTime = os.path.getmtime(tsvFile)
    # print tsvTime

    binFile = tsvFile[:-4] + ".bin"
    catFile = tsvFile[:-4] + ".cat"
    try:
        binTime = os.path.getmtime(binFile)
        # print binTime
    except:
        binTime = 0

    if (tsvTime > binTime):

        # just to be sure, delete the *.bin and *.cat files ...
        cmdString = "rm -fr %s" % binFile
        (status, output) = commands.getstatusoutput(cmdString)
        cmdString = "rm -fr %s" % catFile
        (status, output) = commands.getstatusoutput(cmdString)

        print " creating bin file "
        cmdString = "%s %s/prep4pairwise.py %s" % (gidgetConfigVars['TCGAFMP_PYTHON3'], gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'], tsvFile)
        (status, output) = commands.getstatusoutput(cmdString)
        if (status != 0):
            print " ERROR ??? failed to execute command ??? "
            print cmdString
            sys.exit(-1)
    else:
        print " bin file already up to date "

    return (binFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getTypeRanks(aType, tmpDir, indexList, featList):

    print " "
    print " in getTypeRanks ... ", aType

    outNames = []
    dTypeScores = []
    maxNum = 50000

    pCounts = {}

    for kk in range(len(indexList)):

        index = indexList[kk]
        featName = featList[kk]

        # first, open the previously generated pairwise file for this index
        # (feature)
        pwFile = tmpDir + "/%d.pw" % index
        try:
            fh = file(pwFile, 'r')
        except:
            continue

        # print "         --> reading input file <%s> " % pwFile

        # initialze number of p-values
        pCounts[featName] = 0

        # allocate a vector of zeros
        dTypeVec = numpy.zeros(maxNum)
        iG = 0

        # read through the input file, line by line, and keep only
        # those pairs that involve the current data type

        # each line should look something like this:
        # <featA> <featB> <??>  +0.753   186   +9.236   0   -0.000   0   -0.000   <*>

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
    outName = tsvFile[:ii] + '/' + "featScores_" + tsvFile[ii + 1:-3] + "txt"
    return (outName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#

if __name__ == "__main__":

    # ALL necessary inputs should be handled using this ArgumentParser ... there shouldn't
    # be any 'left-over' arguments ... any unrecognized command-line inputs will result
    # in an error like:
    # rkpw_list_gen.py: error: unrecognized arguments: abc def

    parser = argparse.ArgumentParser(
        description='Create runlist for pairwise')
    parser.add_argument('--min-ct-cell', '-minct',
                        action='store', default=5, type=int)
    parser.add_argument('--min-mx-cell', '-minmx',
                        action='store', default=5, type=int)
    parser.add_argument('--min-samples', '-M',
                        action='store', default=30, type=int)
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

    if (len(indexList) < 5):
        print " ERROR ... does not seem worth continuing ... "
        print indexList
        print featList
        sys.exit(-1)

    print " --> number of features : ", len(indexList)
    numSamples = getNumSamples(tsvFile)
    print " --> number of samples  : ", numSamples

    # we need to pre-process the tsv file (unless it appears to have already
    # been done)
    binFile = preProcessTSV(tsvFile)

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

    # write the jobInfo file ...
    jobFile = tmpDir + "/jobInfo.txt"
    try:
        fh = file(jobFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % jobFile
        sys.exit(-1)
    fh.write("tsvFile = %s\n" % args.tsvFile)
    fh.close()

    # open the runFile ...
    runFile = tmpDir + "/runList.txt"
    try:
        fh = file(runFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % runFile
        sys.exit(-1)

    pythonbin = sys.executable

    golempwd = "PASSWD_HERE"
    fhC = file ( gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'] + "/config", 'r' )
    aLine = fhC.readline()
    fhC.close()
    aLine = aLine.strip()
    golempwd = aLine
    print " got this ... <%s> " % golempwd

    numJobs = 0
    for index in indexList:
        outName = tmpDir + "/" + str(index) + ".pw"
        cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-1.1.2"
        cmdString += " --pvalue 1. --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
            % (args.min_ct_cell, args.min_mx_cell, args.min_samples)
        cmdString += " --outer %d:%d:1 --inner 0::1  %s  %s " \
            % (index, index + 1, binFile, outName)
        fh.write("%s\n" % cmdString)
        numJobs += 1

    fh.close()

    # ok, now we want to actually launch the jobs ...
    cmdString = "python " + gidgetConfigVars['TCGAFMP_ROOT_DIR'] + "/main/golem.py "
    cmdString += "http://glados.systemsbiology.net:7083 -p " + golempwd + " "
    cmdString += "-L scoreCatFeat -u "
    cmdString += getpass.getuser() + " "
    cmdString += "runlist " + runFile
    print cmdString
    (status, output) = commands.getstatusoutput(cmdString)
    print status
    print output
    print " "
    print " "
    print " --------------- "

    done = 0
    lastCheck = -1
    noChange = 0
    while not done:

        ## count up the number of output files ...
        numOutFiles = 0
        for aName in os.listdir(tmpDir):
            if (aName.endswith(".pw")):
                numOutFiles += 1
        print numOutFiles

        ## if the number of output files matches the
        ## number of jobs, we're good to go
        if (numOutFiles == numJobs): done = 1

        ## if this count has not changed in a while,
        ## they we probably want to bail ...
        if ( lastCheck == numOutFiles ):
            noChange += 1
        if ( noChange > 5 ): done = 1
        lastCheck = numOutFiles

        time.sleep(10)

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
    # ...
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

    ## outFile = tmpDir + "/featScores.tsv"
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
