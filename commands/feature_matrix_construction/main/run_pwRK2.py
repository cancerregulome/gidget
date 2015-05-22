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
    parser.add_argument('--pvalue', '-p', action='store',
                        default=0.000001, type=float)
    parser.add_argument('--adjP', '-a', action='store_true')
    parser.add_argument('--all', '-A', action='store_true')
    parser.add_argument('--one', '-O', action='store')
    parser.add_argument('--verbosity', '-v',
                        action='store', default=0, type=int)
    parser.add_argument('--tsvFile', '-f', action='store', required=True)
    parser.add_argument('--forRE', '-R', action='store_true')
    parser.add_argument('--forLisa', '-L', action='store_true')

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

    # note that we must either have an integer value in 'one' or else 'all'
    # must be TRUE
    print args
    indexString = ''
    if (not args.all):
        if (args.one == None):
            args.all = True
            if (0):
                print " ERROR: either --all or --one must be specified "
                sys.exit(-1)
        else:
            try:
                indexString = str(args.one)
            except:
                print " could not get index ??? "
                print " ERROR: either --all or --one must be specified "
                sys.exit(-1)
    else:
        if (not args.one == None):
            print " ERROR: either --all or --one must be specified, NOT both "
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
    if (args.all):
        fh.write("all = TRUE\n")
    else:
        try:
            index = int(args.one)
        except:
            index = getFeatureIndex(args.one, args.tsvFile)
        fh.write("one = %d\n" % index)

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

    pythonbin = sys.executable

    golempwd = "PASSWD_HERE"
    fhC = file ( gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'] + "/config", 'r' )
    aLine = fhC.readline()
    fhC.close()
    aLine = aLine.strip()
    golempwd = aLine
    print " got this ... <%s> " % golempwd

    if (args.all):
        # handle the all by all option ...
        # calling with these options:
        # --outer index:index:1  --inner +1::1
        numJobs = 0
        for index in range(numFeat - 1):
            outName = tmpDir + "/" + str(index) + ".pw"
            cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
            cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
                % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
            cmdString += " --outer %d:%d:1 --inner +1::1  %s  %s " \
                % (index, index + 1, binFile, outName)
            fh.write("%s\n" % cmdString)
            numJobs += 1

    else:

        # handle the single index vs all option ...
        outName = tmpDir + "/" + str(index) + ".pw"
        cmdString = "1 " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
        cmdString += " --pvalue %g --min-ct-cell %d --min-mx-cell %d --min-samples %d" \
            % (args.pvalue, args.min_ct_cell, args.min_mx_cell, args.min_samples)
        cmdString += " --outer %d:%d:1 --inner 0::1  %s  %s " \
            % (index, index + 1, binFile, outName)
        fh.write("%s\n" % cmdString)
        numJobs = 1

    fh.close()

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
        for aName in os.listdir(tmpDir):
            if (aName.endswith(".pw")):
                numOutFiles += 1
        print numOutFiles

        if (numOutFiles == numJobs):
            done = 1

        tSleep = max(5, int((numJobs - numOutFiles) / 200))
        time.sleep(tSleep)

    print " should be done !!! ", numOutFiles, numJobs

    tSleep = 5
    time.sleep(tSleep)

    # if there was only one job, then we're done now ...
    if (numJobs == 1):
        print " handling a one-by-all run ... "

        # first we run post_rkpw.py which writes
        # out something that looks like the output from runPWPV
        iOne = index
        cmdString = "python %s/main/post_pwRK2.py %s %s %d" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir,
                                                               tsvFile, iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "sort -grk 5 --temporary-directory=%s/ %s/post_proc_all.tsv >& %s/%d.all.pwpv.sort" % (
            gidgetConfigVars['TCGAFMP_CLUSTER_SCRATCH'], tmpDir, tmpDir, iOne)
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

        # first we run post_rkpw.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post_pwRK2.py %s %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir,
                                                            tsvFile)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        # and then we run the script that sorts and trims the output file
        cmdString = "%s/shscript/proc_pwpv2.sh %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        # and now we move the files that we want to keep ...
        cmdString = "mv %s/post_proc_all.short.sort.mapped.noPathway %s.pwpv.forRE" % (
            tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        cmdString = "mv %s/post_proc_all.tsv %s.pwpv" % (tmpDir, tsvFile[:-4])
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

    elif (args.forLisa):
        print " post-processing for Lisa's pancan analysis ... "

        # first we run post_rkpw.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post_pwRK2.py %s %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir,
                                                            tsvFile)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)

        # at this point we have post_proc_all.tsv
        # and post_proc_all.NGEXP.NGEXP.tmp
        cmdString = "%s/shscript/proc_pancan.sh %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir)
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
