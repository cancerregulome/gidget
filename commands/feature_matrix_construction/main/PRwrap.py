#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#!/usr/bin/env python

import commands
import os.path
import os
import sys
import time

from env import gidgetConfigVars
import miscIO
import tsvIO

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def splitPath ( tsvFilename ):

    ii = len(tsvFilename) - 1
    while ( tsvFilename[ii] != '/' ): ii -= 1

    rootDirName = tsvFilename[:ii+1]
    justFileName = tsvFilename[ii+1:]
    return ( rootDirName, justFileName )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def prAlreadyDone ( prOutFile, tTSV ):

    print " in prAlreadyDone (b) ... ", prOutFile, time.ctime(tTSV)

    try:
        print " --> trying to getmtime on <%s> " % prOutFile
        tPR5 = os.path.getmtime ( prOutFile )
        print "     --> tPR5 ", time.ctime(tPR5)
    except:
        print " --> failed to getmtime ??? "
        return ( 0 )

    print " comparing "
    print "     tPR5 : ", time.ctime(tPR5)
    print "     tTSV : ", time.ctime(tTSV)

    try:
        if ( tPR5 > tTSV ):
            print " tPR5 is BIGGER "
            fh = file ( prOutFile )
            looksGood = 0
            for aLine in fh:
                if ( aLine.find(" (m) TIME ") >= 0 ):
                    looksGood = 1
            fh.close()
            if ( looksGood ):
                print "         already done ! "
                return ( 1 )
            else:
                print "         seems to have been done, but needs to be redone ... "
                return ( 0 )
        else:
            print " tTSV is BIGGER "
            print "         seems to have been done, but needs to be redone ... "
            return ( 0 )
    except:
        try:
            fh = file ( prOutFile )
            fh.close()
            print "         failed to get timestamp ??? "
        except:
            print "         PR5 output file does not exist "
        print "         need to rerun ... "
        return ( 0 )

    print " SHOULD NOT GET HERE ??? "
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def checkMultiCat ( curLabel, dataVec ):

    if ( curLabel.startswith("N:") ): return ( 0 )
    uVec = []
    for ii in range(len(dataVec)):
        if ( dataVec[ii] != "NA" ):
            if ( dataVec[ii] not in uVec ):
                uVec += [ dataVec[ii] ]

    if ( len(uVec) > 2 ): return ( 1 )
    return ( 0 )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def handleOneFeature ( featString, typeString, tsvFilename, \
                       pathwaysFilename, numRandFactor=200, dirName='' ):

    print " "
    print " ***************************************************************** "
    print " "
    print " in handleOneFeature <%s> <%s> <%s> <%s> " % \
        ( featString, typeString, tsvFilename, dirName )
    print " "

    isBinaryFeat = 0
    isNumericFeat = 0
    if ( featString.startswith("B:") ):
        isBinaryFeat = 1
    elif ( featString.startswith("N:") ):
        isNumericFeat = 1

    ## get the time-stamp for the TSV file
    tTSV = os.path.getmtime ( tsvFilename ) 

    ## first we need to read in the feature matrix ...
    dataD = tsvIO.readTSV ( tsvFilename )

    rowLabels = dataD['rowLabels']
    dataMatrix = dataD['dataMatrix']
    foundRows = []
    exactMatch = []
    for iRow in range(len(rowLabels)):

        if ( rowLabels[iRow].startswith(featString) ):
            exactMatch += [ iRow ]

    foundRows = exactMatch

    if ( len(foundRows) < 1 ):
        print " ERROR ... no features found ", featString, len(rowLabels)
        print tsvFilename
        print " --> SKIPPING ... "
        return()
        ## sys.exit(-1)
    elif ( len(foundRows) > 1 ):
        print " ERROR ... more than one feature found ", featString, len(rowLabels)
        print tsvFilename
        print foundRows
        print " --> SKIPPING ... "
        return ()
        ## sys.exit(-1)

    print " "
    print " "

    ## figure out the root directory name and then the base output file name
    ( rootDirName, justFileName ) = splitPath ( tsvFilename )
    print " rootDirName = <%s> " % rootDirName
    print " justFileName = <%s> " % justFileName

    if ( dirName != '' ):
        if ( dirName[-1] != '/' ): dirName += '/'

    ## test whether output directory already exists ...
    if ( not os.path.exists(rootDirName+dirName) ):
        ## create output directory
        cmdString = 'mkdir %s%s' % ( rootDirName, dirName )
        ## print cmdString
        ( status, output ) = commands.getstatusoutput ( cmdString )
        if ( not os.path.exists(rootDirName+dirName) ):
            print " ERROR ??? failed to create output directory ??? "
            print cmdString
            print status
            sys.exit(-1)
        else:
            print " output directory created %s " % (rootDirName+dirName)
    else:
        print " output directory already exists %s " % (rootDirName+dirName)


    prBaseName = rootDirName + dirName + justFileName[:-3]
    print " prBaseName = <%s> " % prBaseName

    for iRow in foundRows:

        print " "
        print " "
        curLabel = rowLabels[iRow]
        print iRow, curLabel
        multiCatFlag = checkMultiCat ( curLabel, dataMatrix[iRow] )
        ## print dataMatrix[iRow]

        ## maybe we actually don't have to redo anything ...
        prOutFile = prBaseName + "%d.pxP" % iRow
        if ( prAlreadyDone ( prOutFile, tTSV ) ):
            prOutFile = prBaseName + "%d.pxN" % iRow
            if ( prAlreadyDone ( prOutFile, tTSV ) ):
                prOutFile = prBaseName + "%d.pxA" % iRow
                if ( prAlreadyDone ( prOutFile, tTSV ) ):
                    print "  -->  already done !!! <%s> " % curLabel
                    continue

        print " "
        print " "
        print " ************************************************************* "
        print " TIME : ", time.asctime(time.localtime(time.time()))
        print " "

        cmdString = 'python %s/main/run-pairwise-v2.py ' % ( gidgetConfigVars['TCGAFMP_ROOT_DIR'] )
        cmdString += '--pvalue 2. --one "%s" --tsvFile %s' % ( curLabel, tsvFilename )
        print cmdString
        ( status, output ) = commands.getstatusoutput ( cmdString )
        print " status : ", status
        print " output : ", output

        print " "
        print " "
        print " ************************************************************* "
        print " "

        pwpvFile = tsvFilename[:-3] + "%d.all.pwpv.sort" % iRow

        ## ok, now we are going to loop over 3 different scoring options ...
        signList = [ '+', '-', 'x' ]
        tagList  = [ 'pxP', 'pxN', 'pxA' ]

        ## if this feature is a categorical feature with more than 2 categories,
        ## then we cannot test the sign of the correlation ...
        if ( multiCatFlag ):
            print " WARNING: will only create the pxA output file for this feature "
            signList = [ 'x' ]
            tagList  = [ 'pxA' ]

        for iTest in range(len(signList)):

            ## first do the pathway-ranking looking for positive correlations ...
            prOutFile = prBaseName + "%d.%s" % ( iRow, tagList[iTest] )

            if ( not prAlreadyDone ( prOutFile, tTSV ) ):
                cmdString = 'rm -fr %s' % prOutFile
                print cmdString
                ( status, output ) = commands.getstatusoutput ( cmdString )
                print " "
                print " "
                cmdString = 'python %s/main/runPR.py ' % ( gidgetConfigVars['TCGAFMP_ROOT_DIR'] )
                cmdString += ' --tsvFile %s ' % tsvFilename
                cmdString += ' --pwpvFile %s ' % pwpvFile
                cmdString += ' --pathways %s ' % pathwaysFilename
                cmdString += ' --featName "%s" ' % curLabel
                cmdString += ' --sign "%s" ' % signList[iTest]
                cmdString += ' --nRand %d ' % numRandFactor
                cmdString += ' > %s ' % prOutFile
                print cmdString
                print " "
    
                if ( 1 ):
                    if ( 0 ):
                        print " just pretending ... "
                    else:
                        ( status, output ) = commands.getstatusoutput ( cmdString )
                        print " status : ", status
                        print " output : ", output
                else:
                    os.system ( cmdString )
    
                time.sleep ( 10 )
    

        print " "
        print " "
        print " ************************************************************* "
        print " "


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
## MAIN PROGRAM STARTS HERE
##
## required inputs:
##      input feature matrix
##      feature substring (eg "B:SAMP:I(C2|CofC_k13)" or just "CofC_k13"

if __name__ == "__main__":

    if ( len(sys.argv) < 3  or  len(sys.argv) > 5 ):
        print " Usage: %s <tsvFilename> <featList file> [numRandFactor] [dirName] " % sys.argv[0]
	sys.exit(-1)

    tsvFilename = sys.argv[1]
    featListFile = sys.argv[2]
    typeString = "N:GEXP:"

    if ( len(sys.argv) >= 4 ):
        numRandFactor = int ( sys.argv[3] )
    else:
        ## set default to 200
        numRandFactor = 200

    if ( len(sys.argv) >= 5 ):
        dirName = sys.argv[4]
    else:
        dirName = ''

    ## sanity check the input parameters ...

    ## first, check the input feature matrix
    testD = tsvIO.readTSV_dataMatrix ( tsvFilename )
    try:
        print " got feature matrix ", testD['dataType']
    except:
        print " ERROR ... failed to read input feature matrix ??? "
        print tsvFilename
        sys.exit(-1)

    ## next, make sure that the pathways file is accessible
    ## and looks good ...
    pathwaysFilename = gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] \
        + "/nci_pid/only_NCI_Nature_ver5.tab"
    try:
        fh = file ( pathwaysFilename, 'r' )
        print " opening file <%s> " % pathwaysFilename
        numP = miscIO.num_lines ( fh )
        print "     --> numP = ", numP
        fh.close()
    except:
        numP = 0

    if ( numP < 10 ):
        print " ERROR ... pathways file looks bad ??? "
        print pathwaysFilename
        sys.exit(-1)         

    ## and now start looping over the features ...
    fh = file ( featListFile, 'r' )
    for aLine in fh:
        aLine = aLine.strip()
        featString = aLine

        handleOneFeature ( featString, typeString, tsvFilename, 
                           pathwaysFilename, numRandFactor, dirName )

    fh.close()

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
