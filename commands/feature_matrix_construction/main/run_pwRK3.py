#!/usr/bin/env python

import argparse
import commands
import getpass
import os
import os.path
import sys
import time

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

    # print " in getIndexRanges ... ", tsvFile, aType

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
            if (tokenList[0].find(aType) >= 0):
                iList += [ii]
        ii += 1
        # if ( ii%10000 == 0 ): print ii, len(tokenList)

    fh.close()

    # print iList
    numI = len(iList)

    iStart = iList[0]
    for ii in range(1, numI):
        if (iList[ii] > (iList[ii - 1] + 1)):
            iRanges += [(iStart, iList[ii - 1])]
            iStart = iList[ii]

    iRanges += [(iStart, iList[-1])]
    # print iRanges

    # now make sure that none of the ranges are too big ...
    maxRngSize = 100
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
        cmdString = "/users/rkramer/bin/python3 /titan/cancerregulome8/TCGA/scripts/prep4pairwise.py %s" % tsvFile
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
                        action='store', default=20, type=int)
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

    args = parser.parse_args()
    print args

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
    print args
    indexString = ''

    if (args.all):
        print " --> running ALL by ALL "
        args.byType = False
        args.one = None
    elif (args.byType):
        if (args.type1 == None or args.type2 == None):
            print " ERROR ... when using the byType option, type1 and type2 must be specified "
            sys.exit(-1)
        print " --> running <%s> by <%s> " % (args.type1, args.type2)
        args.all = False
        args.one = None
    elif (args.one != None):
        print " --> running <%s> by ALL " % (args.one)
        args.all = False
        args.byType = False
        indexString = str(args.one)
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
        iRanges2 = getIndexRanges(tsvFile, args.type2)

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

    tmpDir = "/titan/cancerregulome9/TCGA/pw_scratch/%s" % curJobName
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
    if (args.all):
        fh.write("all = TRUE\n")
    elif (args.byType):
        fh.write("type1 = %s\n" % args.type1)
        fh.write("type2 = %s\n" % args.type2)
    else:
        try:
            index = int(args.one)
        except:
            index = getFeatureIndex(args.one, args.tsvFile)
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
    runFile = tmpDir + "/runList.txt"
    try:
        fh = file(runFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % runFile
        sys.exit(-1)

    pythonbin = "/tools/bin/python2.7"
    golempwd = "g0l3mm45t3r"

    if (args.all):
        # handle the all by all option ...
        # calling with these options:
        # --outer index:index:1  --inner +1::1
        numJobs = 0
        for index in range(numFeat - 1):
            outName = tmpDir + "/" + str(index) + ".pw"
            cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise-1.1.2"
            ## cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise"
            cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
                % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
            cmdString += " --outer %d:%d:1 --inner +1::1  %s  %s " \
                % (index, index + 1, binFile, outName)
            fh.write("%s\n" % cmdString)
            numJobs += 1

    elif (args.byType):
        numJobs = 0
        # print " index ranges: "
        # print iRanges1
        # print iRanges2
        for iTuple in iRanges1:
            for jTuple in iRanges2:
                index = numJobs
                outName = tmpDir + "/" + str(index) + ".pw"
                cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise-1.1.2"
                ## cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise"
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

        # handle the single index vs all option ...
        outName = tmpDir + "/" + str(index) + ".pw"
        cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise-1.1.2"
        ## cmdString = "1 /titan/cancerregulome8/TCGA/scripts/pairwise"
        cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
            % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
        cmdString += " --outer %d:%d:1 --inner 0::1  %s  %s " \
            % (index, index + 1, binFile, outName)
        fh.write("%s\n" % cmdString)
        numJobs = 1

    fh.close()

    print " "
    print " ********************************************* "
    print " Number of jobs about to be launched : ", numJobs
    print " ********************************************* "
    print " "

    # ok, now we want to actually launch the jobs ...
    cmdString = "python $TCGAFMP_ROOT_DIR/main/golem.py "
    #### cmdString += "http://glados.systemsbiology.net:8083 -p g0l3mm45t3r "
    cmdString += "http://glados.systemsbiology.net:7083 -p g0l3mm45t3r "
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
        for aName in os.listdir(tmpDir):
            if (aName.endswith(".pw")):
                numOutFiles += 1
        print numOutFiles

        if (numOutFiles == numJobs):
            done = 1
        else:
            tSleep = max(10, int((numJobs - numOutFiles) / 200))
            print " ( sleeping for %.0f seconds ) " % float(tSleep)
            time.sleep(tSleep)

    print " should be done !!! ", numOutFiles, numJobs

    tSleep = 10
    time.sleep(tSleep)

    # if there was only one job, then we're done now ...
    if (numJobs == 1 and (not args.byType)):
        print " handling a one-by-all run ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_rkpw.py which writes
        # out something that looks like the output from runPWPV
        iOne = index
        cmdString = "python $TCGAFMP_ROOT_DIR/main/post_pwRK2.py %s %s %d %g" % (
            tmpDir, tsvFile, iOne, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "sort -grk 5 --temporary-directory=/local/sreynold/scratch/ %s/post_proc_all.tsv >& %s/%d.all.pwpv.sort" % (
            tmpDir, tmpDir, iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "mv %s/%d.all.pwpv.sort %s.%d.all.pwpv.sort" % (tmpDir,
                                                                    iOne, tsvFile[:-4], iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        print "\n\n DONE \n\n"
        sys.exit(-1)

    # now that the job is finished, we need to handle the post-processing

    if (args.forRE):
        print " post-processing for RE ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_rkpw.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python $TCGAFMP_ROOT_DIR/main/post_pwRK2.py %s %s -1 %g" % (
            tmpDir, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output

        # and then we run the script that sorts and trims the output file
        cmdString = "$TCGAFMP_ROOT_DIR/shscript/proc_pwpv2.sh %s" % tmpDir
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output

        # and now we move the files that we want to keep ...
        if (args.byType):
            cmdString = "uniq %s/post_proc_all.short.sort.mapped.noPathway > %s.%s.%s.pwpv.forRE" % \
                (tmpDir, tsvFile[:-4], cleanString(args.type1),
                 cleanString(args.type2))
        else:
            cmdString = "mv %s/post_proc_all.short.sort.mapped.noPathway %s.pwpv.forRE" % (
                tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        if (args.byType):
            cmdString = "mv %s/post_proc_all.tsv %s.%s.%s.pwpv" % \
                (tmpDir, tsvFile[:-4], cleanString(args.type1),
                 cleanString(args.type2))
        else:
            cmdString = "mv %s/post_proc_all.tsv %s.pwpv" % (tmpDir,
                                                             tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

    elif (args.forLisa):
        print " post-processing for Lisa's pancan analysis ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post_rkpw.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python $TCGAFMP_ROOT_DIR/main/post_pwRK2.py %s %s -1 %g" % (
            tmpDir, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        # at this point we have post_proc_all.tsv
        # and post_proc_all.NGEXP.NGEXP.tmp
        cmdString = "$TCGAFMP_ROOT_DIR/shscript/proc_pancan.sh %s" % tmpDir
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        # and now we move the files that we want to keep ...
        cmdString = "mv %s/post_proc_all.NGEXP.NGEXP.tmp.sort.top1M %s.pwpv.NGEXP.NGEXP.top1M" % (
            tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        cmdString = "mv %s/post_proc_all.NGEXP.NGEXP.tmp.sort %s.pwpv.NGEXP.NGEXP.all" % (
            tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        cmdString = "mv %s/post_proc_all.tsv %s.pwpv" % (tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

    print "\n\n DONE \n\n"

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
