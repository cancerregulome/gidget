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

blockDone = 0
blockList = []
maxCard = 30

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

def getBlockList(tsvFile):

    global blockDone
    global blockList

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

            if ( aLine.startswith("C:") ):
                uList = []
                for jj in range(1,len(tokenList)):
                    if ( tokenList[jj] != "NA" ):
                        if ( tokenList[jj] not in uList ):
                            uList += [ tokenList[jj] ]
                if ( len(uList) > maxCard ): blockList += [ii]

        ii += 1

    fh.close()

    blockDone = 1
    print " got blockList : ", blockList


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

            if ( ii not in blockList ):
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
    maxRngSize = 100000000
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

        sleepTime=5
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

    sleepTime = 5

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
    print " leaving watchDir "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def writeLuaScript ( tmpDir13, args, iRanges1, iRanges2 ):

    luaFile = tmpDir13 + "/pair_generator.lua"
    try:
        fh = file(luaFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % luaFile
        sys.exit(-1)

    if (args.all):
        print " --> handling the all by all option ... "

        fh.write ( "function pair_generator ( N )\n" )
        fh.write ( "    for i = 0, (N-1) do\n" )
        fh.write ( "        for j = i+1, (N-1) do\n" )
        fh.write ( "            coroutine.yield ( i, j )\n" )
        fh.write ( "        end\n" )
        fh.write ( "    end\n" )
        fh.write ( "end\n" )

    elif (args.byType):
        print " --> handling the byType option ... "

        # FIRST, if the two types are DIFFERENT ...
        if ( args.type1 != args.type2 ):

            ## first we need to write out the two lists of indices
            aFile = tmpDir13 + "/listA.txt"
            fhA = file(aFile, 'w')
            for iTuple in iRanges1:
                print " (A) writing out tuple ", iTuple, " from %d to %d inclusive " % ( iTuple[0], iTuple[1] )
                for ii in range(iTuple[0],iTuple[1]+1):
                    fhA.write("%d\n" % ii)
            fhA.close()
    
            bFile = tmpDir13 + "/listB.txt"
            fhB = file(bFile, 'w')
            for iTuple in iRanges2:
                print " (B) writing out tuple ", iTuple, " from %d to %d inclusive " % ( iTuple[0], iTuple[1] )
                for ii in range(iTuple[0],iTuple[1]+1):
                    fhB.write("%d\n" % ii)
            fhB.close()
    
            ## and here is the lua code 
            fh.write ( 'function pair_generator ( N )\n' )
            fh.write ( ' \n' )
            fh.write ( '    i = 1\n' )
            fh.write ( '    aList = {}\n' )
            fh.write ( '    for lineA in io.lines("%s") do\n' % aFile )
            fh.write ( '        aList[i] = tonumber(lineA)\n' )
            fh.write ( '        i = i + 1\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( '    j = 1\n' )
            fh.write ( '    bList = {}\n' )
            fh.write ( '    for lineB in io.lines("%s") do\n' % bFile )
            fh.write ( '        bList[j] = tonumber(lineB)\n' )
            fh.write ( '        j = j + 1\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( '    for i,a in ipairs(aList) do\n' )
            fh.write ( '        for j,b in ipairs(bList) do\n' )
            fh.write ( '            if ( a < b ) then\n' )
            fh.write ( '                coroutine.yield ( a, b )\n' )
            fh.write ( '            elseif ( a > b ) then\n' )
            fh.write ( '                coroutine.yield ( b, a )\n' )
            fh.write ( '            end\n' )
            fh.write ( '        end\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( 'end\n' )

        # SECOND, if the two types are the SAME ...
        elif ( args.type1 == args.type2 ):

            ## first we need to write out the two lists of indices
            aFile = tmpDir13 + "/listA.txt"
            fhA = file(aFile, 'w')
            for iTuple in iRanges1:
                print " (A) writing out tuple ", iTuple, " from %d to %d inclusive " % ( iTuple[0], iTuple[1] )
                for ii in range(iTuple[0],iTuple[1]+1):
                    fhA.write("%d\n" % ii)
            fhA.close()
    
            bFile = tmpDir13 + "/listB.txt"
            fhB = file(bFile, 'w')
            for iTuple in iRanges2:
                print " (B) writing out tuple ", iTuple, " from %d to %d inclusive " % ( iTuple[0], iTuple[1] )
                for ii in range(iTuple[0],iTuple[1]+1):
                    fhB.write("%d\n" % ii)
            fhB.close()
    
            ## and here is the lua code 
            fh.write ( 'function pair_generator ( N )\n' )
            fh.write ( ' \n' )
            fh.write ( '    i = 1\n' )
            fh.write ( '    aList = {}\n' )
            fh.write ( '    for lineA in io.lines("%s") do\n' % aFile )
            fh.write ( '        aList[i] = tonumber(lineA)\n' )
            fh.write ( '        i = i + 1\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( '    j = 1\n' )
            fh.write ( '    bList = {}\n' )
            fh.write ( '    for lineB in io.lines("%s") do\n' % bFile )
            fh.write ( '        bList[j] = tonumber(lineB)\n' )
            fh.write ( '        j = j + 1\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( '    for i,a in ipairs(aList) do\n' )
            fh.write ( '        for j,b in ipairs(bList) do\n' )
            fh.write ( '            if ( a < b ) then\n' )
            fh.write ( '                coroutine.yield ( a, b )\n' )
            fh.write ( '            end\n' )
            fh.write ( '        end\n' )
            fh.write ( '    end\n' )
            fh.write ( ' \n' )
            fh.write ( 'end\n' )

    else:
        print " --> handling the one vs all option ... ", index

        fh.write ( "function pair_generator ( N )\n" )
        fh.write ( "    one = %d\n" % index )
        fh.write ( "    for i = 0, (N-1) do\n" )
        fh.write ( "        if i < one then\n" )
        fh.write ( "            coroutine.yield ( i, one )\n" )
        fh.write ( "        elseif i > one then\n" )
        fh.write ( "            coroutine.yield ( one, i )\n" )
        fh.write ( "        end\n" )
        fh.write ( "    end\n" )
        fh.write ( "end\n" )

    fh.close()
    return ( luaFile )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def writeFullList ( tmpDir13, args, numFeat, iRanges1, iRanges2 ):

    print " in writeFullList ... (numFeat=%d) " % ( numFeat )

    listFile = tmpDir13 + "/full_list.txt"
    try:
        fh = file(listFile, 'w')
    except:
        print " failed to open output file <%s>, exiting ... " % listFile
        sys.exit(-1)

    numPairs = 0

    if (args.all):
        print " --> handling the all by all option ... "

        if ( numFeat > 40000 ):
            print " "
            print " WARNING !!! this seems like a bad idea ... "
            print " "

        for ii in range(numFeat):
            if ( ii in blockList ): continue
            for jj in range(ii+1,numFeat):
                if ( jj in blockList ): continue
                fh.write ( "%d %d\n" % ( ii, jj ) )
                numPairs += 1

    elif (args.byType):
        print " --> handling the byType option ... "

        # FIRST, if the two types are DIFFERENT ...
        if ( args.type1 != args.type2 ):

            for iTuple in iRanges1:
                for ii in range(iTuple[0],iTuple[1]+1):
                    for jTuple in iRanges2:
                        for jj in range(jTuple[0],jTuple[1]+1):
                            if ( ii < jj ):
                                fh.write ( "%d %d\n" % ( ii, jj ) )
                                numPairs += 1
                            elif ( ii > jj ):
                                fh.write ( "%d %d\n" % ( jj, ii ) )
                                numPairs += 1

        # SECOND, if the two types are the SAME ...
        elif ( args.type1 == args.type2 ):

            for iTuple in iRanges1:
                for ii in range(iTuple[0],iTuple[1]+1):
                    for jTuple in iRanges2:
                        for jj in range(jTuple[0],jTuple[1]+1):
                            if ( ii < jj ):
                                fh.write ( "%d %d\n" % ( ii, jj ) )
                                numPairs += 1

    else:
        print " --> handling the one vs all option ... ", index

        for ii in range(numFeat):
            if ( index < ii ):
                fh.write ( "%d %d\n" % ( index, ii ) )
                numPairs += 1
            elif ( index > ii ):
                fh.write ( "%d %d\n" % ( ii, index ) )
                numPairs += 1

    fh.close()

    print "     --> leaving writeFullList ... numPairs=%d " % ( numPairs )
    return ( listFile, numPairs )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makePartialListFile ( numFiles, listFile ):

    ii = len(listFile) - 1
    while ( listFile[ii] != '/' ): ii -= 1
    newFile = listFile[:ii+1] + "%d.list" % numFiles

    try:
        fh = file ( newFile, 'w' )
    except:
        print " ERROR ??? failed to open ", newFile
        sys.exit(-1)

    return ( fh )

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

def splitList ( listFile, numPairs, numJobs ):

    print " in splitList ... (numPairs=%d, numJobs=%d) " % ( numPairs, numJobs )
    numPairs_per_Job = (numPairs / numJobs) + 1
    numOut = 0
    numFiles = 0

    fh = file ( listFile, 'r' )
    for aLine in fh:
        if ( (numOut % numPairs_per_Job) == 0 ):
            if ( numFiles > 0 ): fhO.close()
            fhO = makePartialListFile ( numFiles, listFile )
            numFiles += 1
        fhO.write ( aLine )
        numOut += 1

    fhO.close()

    print numOut, numFiles
    print "     --> finished with splitList ... (numOut=%d, numFiles=%d) " % ( numOut, numFiles )
    return ( numFiles )

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
    parser.add_argument('--outFile', '-o', action='store')
    parser.add_argument('--forRE', '-R', action='store_true')
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

    # note that we must either have an integer (or string) value in 'one'
    # OR 'all' must be TRUE
    # OR 'byType' must be TRUE

    # new 02jan14 : when using the --one option, we can also use the --byType
    # option and only specify *one* of the types ...

    print args
    indexString = ''
    
    ## make sure that some sort of post-processing has been specified ...

    useExplicitList = 1
    useLuaScript = 0
    one_vs_all_flag = 0

    if (args.all):
        print " --> running ALL by ALL "
        args.byType = False
        args.one = None

    elif (args.one != None):
        if (args.byType):
            if (args.type1 == None):
                print " ERROR ... when using the one and byType options together, type1 must be specified "
                sys.exit(-1)
            elif (args.type2 != None):
                print " ERROR ... when using the one and byType options together, only type1 should be specified "
                sys.exit(-1)
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
            one_vs_all_flag = 1

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

    # make sure that we will block high-cardinality features ...
    getBlockList(tsvFile)

    # if we are doing the 'byType' option, we need to figure out which indices
    # are involved ...
    iRanges1 = []
    iRanges2 = []
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


    ## this block of code used to actually write out the calls to pairwise
    ## that were going to be sent to the cluster, but now all that we 
    ## will do here is write out a "pairs_list" file that contains 
    ## a complete list of the pairs of indices that are to be tested ...

    if ( useLuaScript ):
        luaFile = writeLuaScript ( tmpDir13, args, iRanges1, iRanges2 )

    elif ( useExplicitList ):

        # first write the entire list ...
        ( listFile, numPairs ) = writeFullList ( tmpDir13, args, numFeat, iRanges1, iRanges2 )

        numJobs = ( numPairs / 1000 )
        if ( numJobs > 500 ): numJobs = 500
        if ( numJobs < 1 ): numJobs = 1
        splitList ( listFile, numPairs, numJobs )

    else:
        print " ERROR ??? "
        sys.exit(-1)

    ## now we write the "runFile" for golem ...
    runFile = tmpDir13 + "/runList.txt"
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

    for iJob in range(numJobs):

        outName = tmpDir13 + "/%d.pw" % iJob
        listFile = tmpDir13 + "/%d.list" % iJob

        cmdString = "1 ignoreThree.py " + gidgetConfigVars['TCGAFMP_PAIRWISE_ROOT'] + "/pairwise-2.1.2"
        cmdString += " --by-index %s " % listFile
        ## cmdString += " --dry-run "
        cmdString += " --p-value %g " % args.pvalue
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
    cmdString += "-L pairwise-2.1.2 -u "
    cmdString += getpass.getuser() + " "
    cmdString += "runlist " + runFile
    print cmdString
    (status, output) = commands.getstatusoutput(cmdString)
    print " status = <%s> " % status
    print " output = <%s> " % output
    print " "
    print " "
    print " --------------- "

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
    for aName in os.listdir(tmpDir13):
        if (aName.endswith(".pw")): numOutFiles += 1
    print numOutFiles
    if ( numOutFiles != numJobs ):
        print " WARNING: wrong number of output files ??? "
        print numOutFiles, numJobs

    print " should be done !!! ", numOutFiles, numJobs

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

    # if this was a one-by-all job, then we're nearly done ...
    if ((not args.byType) and (one_vs_all_flag==1)):
        print " handling a one-by-all run ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post-pairwise-v2.py which writes
        # out something that looks like the output from runPWPV
        iOne = index
        cmdString = "python %s/main/post-pairwise-v2.py %s %s %d %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, iOne, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        cmdString = "sort -grk 5 --temporary-directory=%s %s/post_proc_all.tsv >& %s/%d.all.pwpv.sort" % \
            (localDir, tmpDir13, tmpDir13, iOne)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        if ( args.outFile ):
            cmdString = "mv %s/%d.all.pwpv.sort %s" % (tmpDir13, iOne, args.outFile)
        else:
            cmdString = "mv %s/%d.all.pwpv.sort %s.%d.all.pwpv.sort" % (tmpDir13, iOne, tsvFile[:-4], iOne)
        print " MOVING OUTPUT FILE < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print status, output

        print "\n\n DONE \n\n"
        print " (d) TIME ", time.asctime(time.localtime(time.time()))

        if ( 0 ):
            cmdString = "rm -fr %s" % tmpDir13
            print " final command : <%s> " % cmdString
            (status, output) = commands.getstatusoutput(cmdString)
        else:
            print " skipping RM -FR ... "

        sys.exit(-1)

    # now that the job is finished, we need to handle the post-processing

    if (args.forRE):
        print " post-processing for RE ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post-pairwise-v2.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post-pairwise-v2.py %s %s -1 %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output
        print " (d) TIME ", time.asctime(time.localtime(time.time()))

        # and then we run the script that sorts and trims the output file
        cmdString = "%s/shscript/proc_pwpv2b.sh %s" % (gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13)
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

    else:

        print " post-processing but NOT for RE ... "
        if (args.useBC < 1.):
            print "     --> will filter on Bonferonni-corrected p-value with threshold of ", args.useBC

        # first we run post-pairwise-v2.py which concatenates them all and writes
        # out something that looks like the output from runPWPV
        cmdString = "python %s/main/post-pairwise-v2.py %s %s -1 %g" % (
            gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpDir13, tsvFile, args.useBC)
        print " < %s > " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
        print " STATUS : ", status
        print " OUTPUT : ", output
        print " (d) TIME ", time.asctime(time.localtime(time.time()))

        # and now we move the files that we want to keep ...
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

    if ( 0 ):
        cmdString = "rm -fr %s" % tmpDir13
        print " final command : <%s> " % cmdString
        (status, output) = commands.getstatusoutput(cmdString)
    else:
        print " skipping RM -FR ... "

    print "\n\n DONE \n\n"

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
