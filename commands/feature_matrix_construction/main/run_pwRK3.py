#!/usr/bin/env python

import argparse
import commands
import getpass
import os
import os.path
import sys
import time

from env import gidgetConfigVars
import miscIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanString(aType):
    aString = ""
    for ii in range(len(aType)):
        if (aType[ii] != ":"):
            aString += aType[ii]
    return (aString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getFeatureIndex(indexString, featureMatrixFile):

    print " <%s> <%s> " % (indexString, featureMatrixFile)

    matchList = []
    indexList = []
    fh = file(featureMatrixFile)
    ii = 0
    for aLine in fh:
        if (aLine.find(indexString) >= 0):
            tokenList = aLine.split('\t')
            if (tokenList[0].find(indexString) >= 0):
                matchList += [tokenList[0]]
                indexList += [(ii - 1)]
        ii += 1

    if (len(matchList) == 0):
        print " no matching feature ??? ", indexString
        sys.exit(-1)

    if (len(matchList) == 1):
        return (indexList[0])

    for ii in range(len(matchList)):
        if (matchList[ii] == indexString):
            return (indexList[ii])
    for ii in range(len(matchList)):
        tokenList = matchList[ii].split(':')
        if (tokenList[2] == indexString):
            return (indexList[ii])

    print " in getFeatureIndex ... too many possible matches ??? "
    print matchList
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getIndexRanges(tsvFile, aType):

    print " in getIndexRanges ... ", tsvFile, aType

    typeList = ["CLIN", "CNVR", "GEXP", "GNAB",
                "METH", "MIRN", "RPPA", "SAMP"]
    if (aType in typeList):
        aType = ":" + aType + ":"

    iRanges = []
    iList = []
    fh = file(tsvFile)
    aLine = fh.readline()
    done = 0
    ii = 0

    while not done:
        aLine = fh.readline()
        aLine = aLine.strip()
        if (len(aLine) < 5):
            done = 1
        else:
            tokenList = aLine.split('\t')
            if (aType=="ANY"):
                iList += [ii]
            elif (tokenList[0].find(aType) >= 0):
                iList += [ii]
        ii += 1
        # if ( ii%10000 == 0 ): print ii, len(tokenList)

    fh.close()

    numI = len(iList)
    if ( numI < 1 ): return ( [] )

    print " numI = ", numI
    print iList[:5]
    print iList[-5:]

    iStart = iList[0]
    for ii in range(1, numI):
        if (iList[ii] > (iList[ii - 1] + 1)):
            iRanges += [(iStart, iList[ii - 1])]
            iStart = iList[ii]

    iRanges += [(iStart, iList[-1])]
    print " len(iRanges) = ", len(iRanges)
    print iRanges[:5]
    print iRanges[-5:]

    # now make sure that none of the ranges are too big ...
    maxRngSize = max ( 100, (numI/20) )
    print " --> maxRngSize = ", maxRngSize
    newRanges = []
    for aTuple in iRanges:
        iStart = aTuple[0]
        iStop = aTuple[1]
        if ((iStop - iStart) < maxRngSize):
            newRanges += [aTuple]
        else:
            jStart = iStart
            jStop = jStart + maxRngSize
            while (jStop < iStop):
                bTuple = (jStart, min(jStop, iStop))
                newRanges += [bTuple]
                jStart = jStop
                jStop = jStart + maxRngSize

            bTuple = (jStart, min(jStop, iStop))
            newRanges += [bTuple]

    print " original # of range blocks : ", len(iRanges)
    print iRanges[:5], iRanges[-5:]
    print " new # of range blocks : ", len(newRanges)
    print newRanges[:5], newRanges[-5:]

    return (newRanges)

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
            print " (a) ERROR ??? failed to execute command ??? "
            print cmdString
            print status
            print output
            sys.exit(-1)
        print " --> bin file created "

        # verify that the bin file actually exists now, otherwise bail ...
        try:
            binTime = os.path.getmtime(binFile)
        except:
            print " "
            print " FATAL ERROR ... prep4pairwise has failed "
            print " "
            print cmdString
            print status
            print output
            sys.exit(-1)

    else:
        print " bin file already up to date "

    return (binFile)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getLocalScratchDir():

    defaultscratch = gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH']
    localscratch = gidgetConfigVars['TCGAFMP_LOCAL_SCRATCH']

    if (not os.path.exists(localscratch)):
        if (not os.path.exists(defaultscratch)):
            print " FATAL ERROR ... need access to some scratch space !!! "
            sys.exit(-1)
        else:
            print " --> using this scratch directory : ", defaultscratch
            return ( defaultscratch )
    else:
        print " --> using this scratch directory : ", localscratch
        return ( localscratch )
        
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def tuplesOverlap(iTuple, jTuple):

    # temporarily turning this off
    return (0)

    # overlapping tuples would be for example:
    ##     (4767, 4867)  and  (4767, 4867)
    # although they need not be identical, maybe:
    ##     (4767, 4867)  and  (4807, 6000)

    # print " iTuple : ", iTuple
    # print " jTuple : ", jTuple

    if (iTuple[0] >= jTuple[1]):
        return (0)
    if (jTuple[0] >= iTuple[1]):
        return (0)

    return (1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#  tmpDir13 : <.../TCGA/pw_scratch/YNNROlQo.1388771679.87.scratch>
#  localDir : </local/<user>/pw_scratch/>

def copyScratchFiles ( tmpDir13, localDir ):

    print " in copyScratchFiles ... <%s> <%s> " % ( tmpDir13, localDir )

    if ( not tmpDir13.startswith(localDir) ):

        sleepTime=60
        time.sleep(sleepTime)
        watchDir ( tmpDir13 )

        ii = len(tmpDir13) - 3
        while ( tmpDir13[ii] != "/" ): ii -= 1
        sName = tmpDir13[ii+1:]
        ## print ii, sName

        cmdString = "cp -fr %s %s/" % ( tmpDir13, localDir )
        print " DOING COPY ... cmdString : <%s> " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        newDir = localDir + "/" + sName
        print " --> newDir : <%s> " % newDir

        time.sleep(sleepTime)
        watchDir ( newDir )

        print "     --> returning <%s> " % newDir
        return ( newDir )

    else:
        print " NOT copying scratch files ... "
        print "     --> returning <%s> " % tmpDir13
        return ( tmpDir13 )


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lastModTime ( aDir ):

    tLast = -1
    for aName in os.listdir(aDir):
        if (aName.endswith(".pw")):
            ## print "     aName = <%s> " % aName
            t = os.path.getmtime ( aDir+"/"+aName )
            if ( t > tLast ): tLast = t
    return ( tLast )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def watchDir ( aDir ):

    if ( aDir[-1] == "/" ): aDir = aDir[:-1]

    t1 = lastModTime ( aDir )
    print " watchDir t1 ", t1

    nLoop = 0

    sleepTime = 20

    time.sleep(sleepTime)
    t2 = lastModTime ( aDir )

    print " watchDir ", t1, t2, nLoop
    while ( t2 > t1 ):
        t1 = t2
        time.sleep(sleepTime)
        t2 = lastModTime ( aDir )
        nLoop += 1
        print " watchDir ", t1, t2, nLoop
        if ( nLoop > 100 ):
            print " BAILING out of watchDir ... ERROR ... EXITING "
            sys.exit(-1)

    time.sleep(sleepTime)
    time.sleep(sleepTime)
    print " leaving watchDir "

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
                        action='store', default=3, type=int)
    parser.add_argument('--min-mx-cell', '-minmx',
                        action='store', default=3, type=int)
    parser.add_argument('--min-samples', '-M',
                        action='store', default=11, type=int)
    parser.add_argument('--pvalue', '-p', action='store',
                        default=0.000001, type=float)
    parser.add_argument('--adjP', '-a', action='store_true')
    parser.add_argument('--all', '-A', action='store_true')
    parser.add_argument('--one', '-O', action='store')
    parser.add_argument('--byType', '-T', action='store_true')
    parser.add_argument('--type1', '-t1', action='store')
    parser.add_argument('--type2', '-t2', action='store')
    parser.add_argument('--verbosity', '-v',
                        action='store', default=0, type=int)
    parser.add_argument('--tsvFile', '-f', action='store', required=True)
    parser.add_argument('--forRE', '-R', action='store_true')
    parser.add_argument('--forLisa', '-L', action='store_true')
    parser.add_argument('--useBC', '-B', action='store',
                        default=99, type=float)

    if (len(sys.argv) < 2):
        print " "
        print " Output of this script is a tab-delimited file with 12 columns, and "
        print " one line for each significant pairwise association: "
        print " "
        print "     # 1  feature A "
        print "     # 2  feature B (order is alphabetical, and has no effect on result) "
        print "     # 3  Spearman correlation coefficient (range is [-1,+1], or NA "
        print "     # 4  number of samples used for pairwise test (non-NA overlap of feature A and feature B) "
        print "     # 5  -log10(p-value)  (uncorrected) "
        print "     # 6  log10(Bonferroni correction factor) "
        print "     # 7  -log10(corrected p-value)   [ col #7 = min ( (col #5 - col #6), 0 ) ] "
        print "     # 8  # of non-NA samples in feature A that were not used in pairwise test "
        print "     # 9  -log(p-value) that the samples from A that were not used are 'different' from those that were "
        print "     #10  (same as col #8 but for feature B) "
        print "     #11  (same as col #9 but for feature B) "
        print "     #12  genomic distance between features A and B (or 500000000) "
        print " "
        print " ERROR -- bad command line arguments "

    args = parser.parse_args()
    print args

    print " (a) TIME ", time.asctime(time.localtime(time.time()))

    # at this point we should have a Namespace called 'args' that looks something like this:
    # Namespace ( tsvFile=['test.tsv'],
    # runFile=['test.run'],
    ##		   byname=False, input=None,
    # min_ct_cell=5, one=None, all=True,
    # pvalue=1e-06, tail=0, verbosity=0 )

    if (0):
        # NEW 19feb13 : need to have either "forRE" or "forLisa" specified so that we know
        # what type of post-processing to invoke ...
        if (args.forRE):
            if (args.forLisa):
                print " ERROR : must choose either --forRE or --forLisa, not both "
                sys.exit(-1)
        else:
            if (not args.forLisa):
                print " ERROR : must specify either --forRE or --forLisa "
                sys.exit(-1)

    # note that we must either have an integer (or string) value in 'one'
    # OR 'all' must be TRUE
    # OR 'byType' must be TRUE

    # new 02jan14 : when using the --one option, we can also use the --byType
    # option and only specificy *one* of the types ...

    print args
    indexString = ''

    if (args.all):
        print " --> running ALL by ALL "
        args.byType = False
        args.one = None
    elif (args.one != None):
        if (args.byType):
            if (args.type1 == None and args.type2 == None):
                print " ERROR ... when using the one and byType options together, either type1 or type2 must be specified "
            elif (args.type1 != None and args.type2 != None):
                print " ERROR ... when using the one and byType options together, you can specific only type1 or type2, not both "
            else:
                if (args.type1 == None):
                    args.type1 = args.type2
                    args.type2 = None
            args.all = False
            indexString = str(args.one)
            print " --> running <%s> by <%s> " % (args.one, args.type1)
        else:
            print " --> running <%s> by ALL " % (args.one)
            args.all = False
            args.byType = False
            indexString = str(args.one)
    elif (args.byType):
        if (args.type1 == None or args.type2 == None):
            print " ERROR ... when using the byType option, type1 and type2 must be specified "
            sys.exit(-1)
        print " --> running <%s> by <%s> " % (args.type1, args.type2)
        args.all = False
        args.one = None
    else:
        print " ERROR ... invalid settings for --all or --byType or --one "
        sys.exit(-1)

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
    numFeat = getNumFeat(tsvFile)
    print " --> number of features : ", numFeat
    numSamples = getNumSamples(tsvFile)
    print " --> number of samples  : ", numSamples

    # if we are doing the 'byType' option, we need to figure out which indices
    # are involved ...
    if (args.byType):
        iRanges1 = getIndexRanges(tsvFile, args.type1)
        if (args.type2 != None):
            iRanges2 = getIndexRanges(tsvFile, args.type2)
        else:
            try:
                index = int(args.one)
            except:
                index = getFeatureIndex(args.one, args.tsvFile)
            iRanges2 = [ ( index, index ) ]
            print " single index range : ", iRanges2

    # if the user wants to use the "adjP" option, then we set the p-value based on
    # the number of samples  ... right now the approach is to do 1.e-X where X=5+(N/100)
    # and N is the number of samples
    if (args.adjP):
        args.pvalue = (1. / 100000.) / float(10. ** (int(numSamples / 100)))
        print " --> setting pvalue threshold to : ", args.pvalue


    # we need to pre-process the tsv file (unless it appears to have already
    # been done)
    binFile = preProcessTSV(tsvFile)

    # create a random name for this particular run ...
    # and then make a subdirectory for the outputs ...
    curJobName = miscIO.make_random_fname()
    print " "
    print " randomly generated job name : <%s> " % curJobName
    print " "

    tmpDir13 = "%s/%s" % (gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'], curJobName)
    cmdString = "mkdir %s" % tmpDir13
    (status, output) = commands.getstatusoutput(cmdString)
    if (not os.path.exists(tmpDir13)):
        print " mkdir command failed ??? "
        print cmdString
        sys.exit(-1)

    # open the jobInfo file ...
    jobFile = tmpDir13 + "/jobInfo.txt"
    try:
        fh = file(jobFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % jobFile
        sys.exit(-1)
    fh.write("tsvFile = %s\n" % args.tsvFile)
    if (args.all):
        fh.write("all = TRUE\n")
    elif (args.byType):
        fh.write("type1 = %s\n" % args.type1)
        if (args.type2 != None):
            fh.write("type2 = %s\n" % args.type2)
    elif (args.one):
        try:
            index = int(args.one)
        except:
            index = getFeatureIndex(args.one, args.tsvFile)
        print " --> got this index : ", index
        fh.write("one = %d\n" % index)
    if (args.useBC < 1.):
        fh.write("useBC = %g\n" % args.useBC)

    if (args.adjP):
        fh.write("adjP = TRUE\n")
    fh.write("pvalue = %f\n" % args.pvalue)
    fh.write("min-samples = %d\n" % args.min_samples)
    fh.write("min-ct-cell = %d\n" % args.min_ct_cell)
    fh.write("min-mx-cell = %d\n" % args.min_mx_cell)
    fh.close()

    # next open the runFile ...
    runFile = tmpDir13 + "/runList.txt"
    try:
        fh = file(runFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % runFile
        sys.exit(-1)

    pythonbin = sys.executable

    golempwd = "PASSWD_HERE"
    fhC = file (gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'] + "/config", 'r' )
    aLine = fhC.readline()
    fhC.close()
    aLine = aLine.strip()
    golempwd = aLine
    print " got this p ... <%s> " % golempwd
    print " "

    one_vs_all_flag = 0

    if (args.all):
        print " --> handling the all by all option ... "
        # handle the all by all option ...
        # calling with these options:
        # --outer index:index:1  --inner +1::1

        # changing this 02Jan14 ... to limit the # of tasks being sent to the cluster
        maxJobs = 500
        nFpJ = max ( 100, (numFeat/maxJobs) )
        print "     --> number of features per task : ", nFpJ
        iStart = 0
        numJobs = 0
        while iStart < numFeat:
            iStop = min ( (iStart + nFpJ), numFeat )
            outName = tmpDir13 + "/" + str(numJobs) + ".pw"
            cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
            cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
                % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
            cmdString += " --outer %d:%d:1 --inner +1::1  %s  %s " \
                % (iStart, iStop, binFile, outName)
            fh.write("%s\n" % cmdString)
            numJobs += 1
            iStart += nFpJ

    elif (args.byType):
        print " --> handling the byType option ... "
        try:
            print "         ", args.type1
        except:
            doNothing=1
        try:
            print "         ", args.type2
        except:
            doNothing=1
        numJobs = 0
        # print " index ranges: "
        # print iRanges1
        # print iRanges2
        for iTuple in iRanges1:
            for jTuple in iRanges2:
                outName = tmpDir13 + "/" + str(numJobs) + ".pw"
                cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
                cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
                    % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)

                # here we need to adjust things so that we don't do the same
                # comparison twice ...
                if (tuplesOverlap(iTuple, jTuple)):
                    # print "     handling overlapping tuples ", iTuple, jTuple
                    jStart = jTuple[0] - iTuple[0] + 1
                    jStop = jTuple[1] - iTuple[0] + 1
                    if (jStart < 1):
                        print " ERROR ??? ", iTuple, jTuple
                        sys.exit(-1)
                    cmdString += " --outer %d:%d:1 --inner +%d:%d:1  %s  %s " \
                        % (iTuple[0], iTuple[1] + 1, jStart, jStop, binFile, outName)
                else:
                    # print "     handling NONoverlapping tuples ", iTuple,
                    # jTuple
                    cmdString += " --outer %d:%d:1 --inner %d:%d:1  %s  %s " \
                        % (iTuple[0], iTuple[1] + 1, jTuple[0], jTuple[1] + 1, binFile, outName)

                fh.write("%s\n" % cmdString)
                # print numJobs, cmdString

                # print "%s" % cmdString
                numJobs += 1

    else:

        one_vs_all_flag = 1
        print " --> handling the one vs all option ... ", index

        # handle the single index vs all option ...
        # ( note that the single-index vs a specified "type" is handled above )
        outName = tmpDir13 + "/" + str(index) + ".pw"
        cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
        cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
            % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
        cmdString += " --outer %d:%d:1 --inner 0::1  %s  %s " \
            % (index, index + 1, binFile, outName)
        fh.write("%s\n" % cmdString)
        numJobs = 1

    fh.close()

    if ( numJobs < 1 ):
        print " "
        print " Bailing out now because there is nothing to do ... "
        print " "
        sys.exit(-1)

    print " "
    print " ********************************************* "
    print " Number of jobs about to be launched : ", numJobs
    print " ********************************************* "
    print " (b) TIME ", time.asctime(time.localtime(time.time()))
    print " "

    # ok, now we want to actually launch the jobs ...
    cmdString = "python %s/main/golem.py " % gidgetConfigVars['TCGAFMP_ROOT_DIR']
    cmdString += "http://glados.systemsbiology.net:7083 -p " + golempwd + " "
    cmdString += "-L pairwiseRK -u "
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
    while not done:

        numOutFiles = 0
        for aName in os.listdir(tmpDir13):
            if (aName.endswith(".pw")):
                numOutFiles += 1
        print numOutFiles

        if (numOutFiles == numJobs):
            done = 1
        else:
            tSleep = max(10, int((numJobs - numOutFiles) / 20))
            if (args.byType): tSleep = min(20,tSleep)
            print " ( sleeping for %.0f seconds ) " % float(tSleep)
            time.sleep(tSleep)

    print " should be done !!! ", numOutFiles, numJobs

    if ( 0 ):
        tSleep = 120
        time.sleep(tSleep)
    else:
        # now we need to poll to make sure that the last file is done
        # being written ...
        watchDir ( tmpDir13 )

    print " (c) TIME ", time.asctime(time.localtime(time.time()))

    # make sure that we have a local scratch directory to use for the sorting
    localDir = getLocalScratchDir()

    print " "
    print " now we should move or copy stuff ... "
    print " tmpDir13 : <%s> " % tmpDir13
    print " localDir : <%s> " % localDir
    tmpDir13 = copyScratchFiles ( tmpDir13, localDir )
    print " "

    ## NOTE that from now on, tmpDir13 hopefully points to a LOCAL scratch directory ...

    # if there was only one job, then we're done now ...
    if ((numJobs == 1) and (not args.byType) and (one_vs_all_flag==1)):
        print " handling a one-by-all run ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_pwRK2.py which writes
        # out something that looks like the output from runPWPV
        iOne = index
        cmdString = "python %s/main/post_pwRK2.py %s %s %d %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, iOne, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "sort -grk 5 --temporary-directory=%s %s/post_proc_all.tsv >& %s/%d.all.pwpv.sort" % \
            (localDir, tmpDir13, tmpDir13, iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "mv %s/%d.all.pwpv.sort %s.%d.all.pwpv.sort" % (tmpDir13,
                                                                    iOne, tsvFile[:-4], iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        print "\n\n DONE \n\n"
        print " (d) TIME ", time.asctime(time.localtime(time.time()))

        cmdString = "rm -fr %s" % tmpDir13
        print " final command : <%s> " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        sys.exit(-1)

    # now that the job is finished, we need to handle the post-processing

    if (args.forRE):
        print " post-processing for RE ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_pwRK2.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post_pwRK2.py %s %s -1 %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output
        print " (d) TIME ", time.asctime(time.localtime(time.time()))

        # and then we run the script that sorts and trims the output file
        cmdString = "%s/shscript/proc_pwpv2.sh %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output
        print " (e) TIME ", time.asctime(time.localtime(time.time()))

        # and now we move the files that we want to keep ...
        if (args.byType):
            cmdString = "uniq %s/post_proc_all.short.sort.mapped.noPathway > %s.%s.%s.pwpv.forRE" % \
                (tmpDir13, tsvFile[:-4], cleanString(args.type1),
                 cleanString(args.type2))
        else:
            cmdString = "mv %s/post_proc_all.short.sort.mapped.noPathway %s.pwpv.forRE" % (
                tmpDir13, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (f) TIME ", time.asctime(time.localtime(time.time()))

        if (args.byType):
            cmdString = "mv %s/post_proc_all.tsv %s.%s.%s.pwpv" % \
                (tmpDir13, tsvFile[:-4], cleanString(args.type1),
                 cleanString(args.type2))
        else:
            cmdString = "mv %s/post_proc_all.tsv %s.pwpv" % (tmpDir13,
                                                             tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (g) TIME ", time.asctime(time.localtime(time.time()))

    elif (args.forLisa):
        print " post-processing for Lisa's pancan analysis ... "
        print " (d) TIME ", time.asctime(time.localtime(time.time()))
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_pwRK2.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post_pwRK2.py %s %s -1 %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (e) TIME ", time.asctime(time.localtime(time.time()))

        # at this point we have post_proc_all.tsv
        # and post_proc_all.NGEXP.NGEXP.tmp
        cmdString = "%s/shscript/proc_pancan.sh %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (f) TIME ", time.asctime(time.localtime(time.time()))

        # and now we move the files that we want to keep ...
        cmdString = "mv %s/post_proc_all.NGEXP.NGEXP.tmp.sort.top1M %s.pwpv.NGEXP.NGEXP.top1M" % (
            tmpDir13, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (g) TIME ", time.asctime(time.localtime(time.time()))

        cmdString = "mv %s/post_proc_all.NGEXP.NGEXP.tmp.sort %s.pwpv.NGEXP.NGEXP.all" % (
            tmpDir13, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (h) TIME ", time.asctime(time.localtime(time.time()))

        cmdString = "mv %s/post_proc_all.tsv %s.pwpv" % (tmpDir13, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " (i) TIME ", time.asctime(time.localtime(time.time()))

    else:
        print " ************************************************** "
        print " *** NO POST-PROCESSING ??? OUTPUTS MAY BE LOST *** "
        print " ************************************************** "

    cmdString = "rm -fr %s" % tmpDir13
    print " final command : <%s> " % cmdString
    (status, output) = commands.getstatusoutput(cmdString)

    print "\n\n DONE \n\n"

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
