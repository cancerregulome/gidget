#! /usr/bin/env python

import miscClin
import miscIO
import miscMath

import commands
from datetime import datetime
import csv
import math
import numpy
import os
import sys

#------------------------------------------------------------------------------

NA_VALUE = -999999

#------------------------------------------------------------------------------

def replaceBlanks ( aString, newChr ):

    newString = ''
    aString = aString.strip()
    for ii in range(len(aString)):
        if ( aString[ii] == ' ' ):
            newString += newChr
        else:
            newString += aString[ii]

    if ( newString == "_0" ): 
        sys.exit(-1)

    # make sure we don't have any double 'newChr' substrings
    doubleChr = newChr + newChr
    ii = newString.find(doubleChr)
    while ( ii >= 0 ):
        newString = newString[:ii] + newString[ii+1:]
        ii = newString.find(doubleChr)

    # HACK ... if this is a microRNA feature, then correct the case ...
    # N:MIRN:hsa-let-7a
    # N:MIRN:hsa-mir-99a
    if (newString[2:6] == "MIRN"):
        tmpString = newString[:6] + newString[6:].lower()
        i1 = tmpString.find("mimat")
        if (i1 > 0):
            newString = tmpString[:i1] + "MIMAT" + tmpString[i1 + 5:]
        else:
            newString = tmpString

    return ( newString )

#------------------------------------------------------------------------------

def fixWeirdCharacters ( aString ):

    newString = ''
    aString = aString.strip()
    for ii in range(len(aString)):
        if ( aString[ii] == '"' ):
            skipChar = 1
        elif ( aString[ii] == '/' ):
            skipChar = 1
        elif ( aString[ii] == "'" ):
            skipChar = 1
        elif ( aString[ii] == '"' ):
            skipChar = 1
        elif ( aString[ii] == ' ' ):
            newString += "_"
#      elif ( aString[ii] == ')' ):
##          skipChar = 1
#      elif ( aString[ii] == '(' ):
##          skipChar = 1
#      elif ( aString[ii] == '-' ):
# #         newString += "_"
        else:
            newString += aString[ii]

    aString = newString
    newString = ''
    for ii in range(len(aString)-1):
        if ( aString[ii:ii+2] == "__" ):
            skipChar = 1
        else:
            newString += aString[ii]
    newString += aString[-1]

    if ( newString == "_0" ): 
        sys.exit(-1)

    return ( newString )

#------------------------------------------------------------------------------
# this is kind of messy at the moment because I have two different types of
# "data dictionaries" -- one for the clinical data and one for the large
# data matrices ...

def writeAttributeHeader ( dataD, bestKeyOrder, fh, sortRowFlag=0 ):

    # handling the data matrix type ...
    if ( 'rowLabels' in dataD.keys() ):
        rowLabels = dataD['rowLabels']
        if ( sortRowFlag ):
            rowLabels.sort()
        for ii in range(len(rowLabels)):
            fh.write ( "@ATTRIBUTE\t%40s\n" % rowLabels[ii] )

    # otherwise handle the clinical-style data matrix ...
    # the keys are the TCGA patient ids
    else:
        # the bestKeyOrder is a list of dictionary keys / feature names
        # and it starts with 'bcr_patient_barcode'
        # NOTE: these feature names do not yet start with "C:CLIN:" etc...
        aKey = bestKeyOrder[0]
        numKeys = len(bestKeyOrder)
        # for each key, there is a vector of values and the length of that
        # vector indicates the number of patients for whom we have data
        numPatients = len(dataD[aKey])
        for aKey in bestKeyOrder:

            outLine = "@ATTRIBUTE\t%40s" % aKey

            ( keyType, nCount, naCount, cardCount, labelList, 
              labelCount ) = miscClin.lookAtKey ( dataD[aKey] )
            # print keyType, nCount, naCount, cardCount, labelList, labelCount

            outLine += "\t%d\t%d\t%d\t%s" % ( nCount, 
                                              naCount, (nCount-naCount), keyType )

            # keyType is either "NOMINAL" or "NUMERIC" ... if it is numeric, let's
            # look at some statistics ...
            if ( keyType == "NUMERIC" ):

                isInt = 1
                tmpV = numpy.zeros ( (nCount-naCount) )
                kk = 0
                for ii in range(nCount):
                    if ( dataD[aKey][ii] != "NA" ):
                        if ( dataD[aKey][ii] != NA_VALUE ):
                            tmpV[kk] = dataD[aKey][ii]
                            delta = tmpV[kk] - int(tmpV[kk])
                            if ( abs(delta) > 0.0001 ): 
                                isInt = 0
                            kk += 1
                print kk, len(tmpV)
                tmpV.sort()

                minV = tmpV[0]
                maxV = tmpV[-1]

                if ( maxV > minV ):
                    medianV = tmpV[kk/2]
                    meanV = tmpV.mean()
                    sigmaV = math.sqrt(tmpV.var())
                    mean2 = 0.
                    mean3 = 0.
                    for kk in range(len(tmpV)):
                        curV = tmpV[kk]
                        mean2 += ( curV - meanV )**2
                        mean3 += ( curV - meanV )**3
                    skewV = mean3 / (mean2**1.5)
                    print " statistics : ", isInt, minV, maxV, medianV, meanV, sigmaV, skewV
                    outLine += "\tCONTINUOUS"
                    if ( isInt ):
                        outLine += "\t%d\t%d\t%d\t%d\t%d\t%5.2f" % ( int(minV), 
                                                                     int(maxV), int(medianV), int(meanV), int(sigmaV), skewV )
                    else:
                        outLine += "\t%f\t%f\t%f\t%f\t%f\t%5.2f" % ( minV, 
                                                                     maxV, medianV, meanV, sigmaV, skewV )
                    # outLine += "\t%f
                else:
                    outLine += "\tCONSTANT"
                    if ( isInt ):
                        outLine += "\t%d" % int(minV)
                    else:
                        outLine += "\t%f" % minV

            elif ( keyType == "NOMINAL" ):
                if ( cardCount == 0 ):
                    print " how can this happen ??? "
                    sys.exit(-1)
                elif ( cardCount == 1 ):
                    outLine += "\tCONSTANT\t{%s}" % labelList[0]
                elif ( max(labelCount) == 1 ):
                    outLine += "\tALL_UNIQUE"
                else:
                    sortList = []
                    for kk in range(cardCount):
                        sortList += [ labelList[kk] ]
                    sortList.sort()
                    print " more info : ", cardCount, labelList, labelCount
                    outLine += "\tCARD=%d" % cardCount
                    outLine += "\t{"
                    for kk in range(cardCount):
                        jj = labelList.index(sortList[kk])
                        outLine += "%s:%d" % ( labelList[jj], labelCount[jj] )
                        if ( kk < (cardCount-1) ):
                            outLine += ", "
                    outLine += "}"

            else:
                print " ERROR ??? "
                sys.exit(-1)

            print " outLine : ", outLine
            fh.write ( "%s\n" % outLine )


#------------------------------------------------------------------------------

def writeTSV_clinical ( allClinDict, bestKeyOrder, outName ):

    # if the output file name does not end with ".tsv", add that suffix
    if ( not outName.endswith(".tsv") ):
        outName += ".tsv"

    print " "
    print " writing output tsv file ", outName

    # figure out how many patients (numClin) we have data for
    aKey = bestKeyOrder[0]
    try:
        numClin = len(allClinDict[aKey])
        print "     size : ", len(bestKeyOrder), numClin
    except:
        print "\n ??? what is happening ??? \n"
        print allClinDict
        sys.exit(-1)

    # open the output file, and write out the dictionary keys on the first
    # line, with tabs in between ...
    fh = file ( outName, 'w' )
    outLine = aKey
    for ii in range(1,len(bestKeyOrder)):
        aKey = bestKeyOrder[ii]
        if (len(allClinDict[aKey]) == numClin):
            outLine += "\t%s" % aKey
    fh.write ( "%s\n" % outLine )

    # check to see if patients are repeated ???
    ignoreKeys = [ "batch_number", "day_of_dcc_upload", "month_of_dcc_upload" ]
    ignoreKeys = []
    keepPatient = [1] * numClin
    for k1 in range(numClin):
        p1 = allClinDict[bestKeyOrder[0]][k1]
        for k2 in range(k1+1,numClin):
            p2 = allClinDict[bestKeyOrder[0]][k2]

            if ( keepPatient[k1] == 0 ): 
                continue
            if ( keepPatient[k2] == 0 ): 
                continue

            if ( p1 == p2 ):
                print " repeated patient !!! ", k1, k2, p1
                sameFlag = 1
                for ii in range(1,len(bestKeyOrder)):
                    aKey = bestKeyOrder[ii]
                    if ( allClinDict[aKey][k1] != allClinDict[aKey][k2] ):
                        if ( aKey not in ignoreKeys ):
                            sameFlag = 0
                            print " differ at ", aKey, allClinDict[aKey][k1], allClinDict[aKey][k2]
                if ( sameFlag == 1 ):
                    print " ALL IDENTICAL dropping %d " % k2
                    keepPatient[k2] = 0
                else:

                    try:
                        if ( allClinDict["batch_number"][k1] > allClinDict["batch_number"][k2] ):
                            print " --> keeping %d over %d " % ( k1, k2 )
                            keepPatient[k2] = 0
                        elif ( allClinDict["batch_number"][k1] < allClinDict["batch_number"][k2] ):
                            print " --> keeping %d over %d " % ( k2, k1 )
                            keepPatient[k1] = 0
                        else:
                            # if the batch numbers appear to be the same, check 
                            # the BCR ...
                            if ( allClinDict["bcr"][k1] != allClinDict["bcr"][k2] ):
                                if ( allClinDict["bcr"][k1].startswith("nationwide") ):
                                    print " --> keeping %d over %d " % ( k1, k2 )
                                    keepPatient[k2] = 0
                                elif ( allClinDict["bcr"][k2].startswith("nationwide") ):
                                    print " --> keeping %d over %d " % ( k2, k1 )
                                    keepPatient[k1] = 0
                            else:
                                print " CANNOT DECIDE WHICH ONE TO KEEP ??? "
                                print allClinDict["batch_number"][k1], allClinDict["bcr"][k1]
                                print allClinDict["batch_number"][k2], allClinDict["bcr"][k2]

                    except:
                        print " DO NOT HAVE BATCH_NUMBER KEY ??? "
                        sys.exit(-1)

    # now loop over the patients
    # dictionary keys are in the "bestKeyOrder" (which automatically starts
    # with the bcr_patient_barcode)
    for kk in range(numClin):
        if ( not keepPatient[kk] ): 
            continue
        aKey = bestKeyOrder[0]
        outLine = "%s" % ( replaceBlanks ( str ( allClinDict[aKey][kk] ), '_' ) )
        for ii in range(1,len(bestKeyOrder)):
            aKey = bestKeyOrder[ii]
            if (len(allClinDict[aKey]) != numClin):
                continue
            try:
                outLine += "\t%s" % str ( allClinDict[aKey][kk] )
            except:
                print " ERROR ??? ", aKey, kk
                print allClinDict[aKey]
                sys.exit(-1)
        fh.write ( "%s\n" % outLine )

    # finally close the file
    fh.close()

#------------------------------------------------------------------------------

def normalizeVector ( inVec ):

    nV = len(inVec)
    outVec = ["NA"] * nV

    sum1 = 0.
    sum2 = 0.
    num1 = 0
    for ii in range(nV):
        if ( inVec[ii] != "NA" ):
            z = inVec[ii]
            sum1 += ( z )
            sum2 += ( z * z )
            num1 += 1

    mean1 = sum1 / float(num1)
    mean2 = sum2 / float(num1)
    sigma = math.sqrt ( mean2 - (mean1*mean1) )

    print " in normalizeVector : ", mean1, sigma

    for ii in range(nV):
        if ( inVec[ii] != "NA" ):
            outVec[ii] = ( inVec[ii] - mean1 ) / sigma

    return ( outVec )

#------------------------------------------------------------------------------
# this function writes clinical data in the "flipped" orientation (ie columns
# are patients and rows are features) and everything is numeric in order to
# go into the "merge" process ...

def writeTSV_clinicalFlipNumeric ( allClinDict, bestKeyOrder, outName ):

    print " "
    print " "
    print " in writeTSV_clinicalFlipNumeric ... ", outName
    print len(bestKeyOrder)
    print bestKeyOrder
    print " "

    # if the output file name does not end with ".tsv", add that suffix
    if ( not outName.endswith(".tsv") ):
        outName += ".tsv"

    print " "
    print " writing output tsv file ", outName

    # figure out how many patients we have data for, and how many featurs
    aKey = bestKeyOrder[0]
    numClin = len(allClinDict[aKey])
    numKey = len(bestKeyOrder)

    # get the barcodes ...
    if ( aKey != "bcr_patient_barcode" ):
        print " why is the first key not the barcode ??? "
        print aKey
        print allClinDict[aKey]
        sys.exit(-1)
    barcodeList = allClinDict[aKey]

    # open the output file ...
    fh = file ( outName, 'w' )

    # write out the first row ...
    outLine = "M:CLIN"
    for jj in range(numClin):
        outLine += "\t%s" % barcodeList[jj]
    fh.write ( "%s\n" % outLine )

    # the outer loop is over the 'keys' (features) in the clinical
    # dictionary, but we will only write out those that are either
    # numeric or have only two possible values ...
    print " LOOPING over KEYS ... "

    for ii in range(1,numKey):

        aKey = bestKeyOrder[ii]

        if (len(allClinDict[aKey]) != numClin):
            continue

        ( keyType, nCount, nNA, nCard, labelList, labelCount ) \
                = miscClin.lookAtKey ( allClinDict[aKey] )
        print ii, aKey, keyType, nCount, nNA, nCard, labelList, labelCount

        if ( aKey == "patient_id" ):
            print " --> FORCING patient_id to be treated as a CATEGORICAL feature "
            keyType = "NOMINAL"
            nCard = len(allClinDict[aKey])

        if ( keyType == "NOMINAL" ):

            # for nominal features, set the default type to "C"
            # but then if cardinality is 2, reset to "B"
            dType = "C"
            if ( 0 ):
                if ( nCard == 2 ): 
                    dType = "B"

            if ( aKey.startswith("B:") ):
                if ( dType == "B" ):
                    featureName = aKey
                else:
                    featureName = "C:" + aKey[2:]

            elif ( aKey.startswith("C:") ):
                if ( dType == "C" ):
                    featureName = aKey
                else:
                    featureName = "B:" + aKey[2:]

            elif ( aKey.lower().find("_mut")>0 ):
                featureName = dType + ":GNAB:" + aKey + "::::"
            elif ( aKey.lower().find("cluster")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("mlh1_meth")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("|mrna_c")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("|mir_c")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("msi_class")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("cin")>0 ):
                featureName = dType + ":SAMP:" + aKey + "::::"
            else:
                featureName = dType + ":CLIN:" + aKey + "::::"

            if ( featureName != aKey ):
                print " (a) tacked on feature type to <%s> to create <%s> " % ( aKey, featureName )

            # handle categorical features ...
            if ( nCard > 2 ):
                print " writing out categorical key ... ", labelList, featureName
                outLine = "%s" % ( replaceBlanks ( featureName, '_' ) )
                for jj in range(numClin):
                    curLabel = replaceBlanks ( 
                        str(allClinDict[aKey][jj]).upper(), '_' )
                    outLine += "\t%s" % curLabel
                fh.write ( "%s\n" % outLine )

            # do we want to write out features that have cardinality of 1 ???
            elif ( nCard == 1 ):
                print " writing out categorical key BUT only ONE category ??? ", labelList, featureName
                outLine = "%s" % ( replaceBlanks ( featureName, '_' ) )
                for jj in range(numClin):
                    curLabel = replaceBlanks ( 
                        str(allClinDict[aKey][jj]).upper(), '_' )
                    outLine += "\t%s" % curLabel
                fh.write ( "%s\n" % outLine )

            else:

                print " handling special case nominal feature ... ", aKey, keyType, nCard, labelList, labelCount

                # should we call a "categorical" feature with cardinality 2 
                # binary ???
                if ( 0 ):
                    if ( nCard == 2 ):
                        if ( featureName[0] != "B" ):
                            featureName = "B" + featureName[1:]

                if ( 0 ):
                    print " remapping from labels to integers ... ", labelList, featureName
                    outLine = "%s" % ( replaceBlanks ( featureName, '_' ) )
                    for jj in range(numClin):
                        curLabel = allClinDict[aKey][jj].upper()
                        try:
                            outLine += "\t%d" % labelList.index(curLabel)
                        except:
                            if ( curLabel != "NA" ):
                                print " this should be NA ??? ", curLabel
                                sys.exit(-1)
                            outLine += "\tNA"
                    fh.write ( "%s\n" % outLine )
                else:
                    print " NOT remapping from labels to integers ... ", labelList, featureName
                    outLine = "%s" % ( replaceBlanks ( featureName, '_' ) )
                    for jj in range(numClin):
                        curLabel = replaceBlanks ( 
                            allClinDict[aKey][jj].upper(), '_' )
                        outLine += "\t%s" % curLabel
                    fh.write ( "%s\n" % outLine )


        elif ( keyType == "NUMERIC" ):

            if ( aKey.startswith("N:") ):
                featureName = aKey
            elif ( aKey.startswith("B:") ):
                featureName = aKey
            elif ( aKey.startswith("C:") ):
                if ( aKey.lower().find("gistic")>0  and  aKey.lower().find("_d")>0 ):
                    featureName = aKey
                else:
                    print " ERROR ??? numeric type with categorical label ??? "
                    print keyType, aKey
                    sys.exit(-1)

            elif ( aKey.lower().find("globalsv")>0 ):
                featureName = "N:SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("localsv")>0 ):
                featureName = "N:SAMP:" + aKey + "::::"
            elif ( aKey.lower().find("msi_")>=0 ):
                featureName = "N:SAMP:" + aKey + "::::"
            else:
                featureName = "N:CLIN:" + aKey + "::::"
            outLine = "%s" % featureName

            if ( featureName != aKey ):
                print " tacked on feature type to <%s> to create <%s> " % ( aKey, featureName )

            for jj in range(numClin):
                if ( allClinDict[aKey][jj] != NA_VALUE ):
                    try:
                        if ( allClinDict[aKey][jj] >= 0 ):
                            iVal = int ( allClinDict[aKey][jj] + 0.1 )
                        else:
                            iVal = int ( allClinDict[aKey][jj] - 0.1 )
                        if ( abs(iVal-allClinDict[aKey][jj]) < 0.001 ):
                            outLine += "\t%d" % iVal
                        else:
                            outLine += "\t%.3f" % allClinDict[aKey][jj]
                    except:
                        outLine += "\t%s" % allClinDict[aKey][jj]
                else:
                    outLine += "\tNA"
            fh.write ( "%s\n" % outLine )

        else:
            print " ERROR ??? invalid keyType ??? ", keyType
            sys.exit(-1)


    # finally close the file
    fh.close()

#------------------------------------------------------------------------------

def buildPath ( outFilename ):

    # output filename might look something like this:
    # /titan/cancerregulome3/TCGA/outputs/brca_kirc/brca_kirc.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.test.tsv

    # so figure out the directory path name and then create it ...
    i1 = len(outFilename) - 1
    while ( outFilename[i1] != '/' ):
        i1 -= 1
    createDir ( outFilename[:i1] )

    # and that should be all we need to do ...

#------------------------------------------------------------------------------

def createDir ( dirName ):

    print " in createDir ... ", dirName
    if ( os.path.exists ( dirName ) ): 
        return

    print " directory does not exist ... "
    i1 = 0
    while ( dirName[i1]=='/' ): 
        i1 += 1
    while ( i1 < len(dirName) ):
        i2 = dirName.find("/",i1)
        if ( i2 <= i1 ): 
            i2 = len(dirName)
        tmpName = dirName[:i2]
        print " tmpName : <%s> " % tmpName
        if ( not os.path.exists ( tmpName ) ):
            cmdString = "mkdir " + tmpName
            print " cmdString : <%s> " % cmdString
            ( status, output ) = commands.getstatusoutput ( cmdString )
            if ( not os.path.exists ( tmpName ) ):
                print " mkdir command failed ??? "
                print cmdString
                sys.exit(-1)
        i1 = i2 + 1

#------------------------------------------------------------------------------

def checkUnique ( aList ):

    print " in checkUnique ... ", len(aList), aList[0], " ... ", aList[-1]
    uList = []
    n = 0
    n10 = len(aList)/10

    rmList = []

    for a in aList:
        # if ( n%n10 == 0 ): print "             ", n, len(aList)
        if ( a not in uList ):
            uList += [ a ]
        else:
            print " WARNING: <%s> is repeated ??? " % a
            # print aList[:10]
            i0 = 0
            dupList = []
            outLine = ""
            while ( i0 < len(aList) ):
                try:
                    i1 = aList.index(a,i0)
                except:
                    i1 = -1
                if ( i1 >= 0 ):
                    outLine += " %d " % i1
                    dupList += [ i1 ]
                    i0 = i1 + 1
                else:
                    i0 = len(aList)
            print outLine
            rmList += dupList[1:]
        n += 1

    print "     done ... rmList : ", rmList

    return ( rmList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function returns a list of rows or columns that should be skipped
# based on the fraction of NA samples ...
#
# NOTE: if we are choosing which columns to skip, we want the fraction of NA
# samples to not be exceeded for each feature "type" ...

def getSkipList ( maxNAfrac, dataD, rowColFlag ):

    print " in getSkipList ... ", maxNAfrac, rowColFlag, dataD['dataType']

    skipList = []
    dataMatrix = dataD['dataMatrix']

    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print "                      %5d x %5d " % ( numRow, numCol )

    if ( rowColFlag == 'row' ):
        outerLoopCount = numRow
        innerLoopCount = numCol
        labelList = dataD['rowLabels']
        if ( len(labelList) != numRow ):
            print " ERROR in getSkipList ??? ", rowColFlag, numRow, len(labelList)
            sys.exit(-1)
    elif ( rowColFlag == 'col' ):
        outerLoopCount = numCol
        innerLoopCount = numRow
        labelList = dataD['colLabels']
        if ( len(labelList) != numCol ):
            print " ERROR in getSkipList ??? ", rowColFlag, numCol, len(labelList)
            sys.exit(-1)
    else:
        print " ERROR in getSkipList ... ", rowColFlag
        sys.exit(-1)

    print " outer loop over %d %ss " % ( outerLoopCount, rowColFlag )
    for jG in range(outerLoopCount):

        numNA = {}
        numNot = {}

        if ( rowColFlag == 'row' ):
            numNA['all'] = 0
            numNot['all'] = 0

        else:
            numNA['CNVR'] = 0
            numNA['GEXP'] = 0
            numNA['MIRN'] = 0
            numNA['METH'] = 0
            numNA['CLIN'] = 0
            numNA['SAMP'] = 0
            numNA['GNAB'] = 0

            numNot['CNVR'] = 0
            numNot['GEXP'] = 0
            numNot['MIRN'] = 0
            numNot['METH'] = 0
            numNot['CLIN'] = 0
            numNot['SAMP'] = 0
            numNot['GNAB'] = 0

        for jS in range(innerLoopCount):
            # check if this value is NA or not ...
            if ( rowColFlag == 'row' ):
                curVal = dataMatrix[jG][jS]
            else:
                curVal = dataMatrix[jS][jG]

            if ( rowColFlag == 'row' ):
                aKey = 'all'
            else:
                tokenList = dataD['rowLabels'][jS].split(':')
                ## aKey = "%s:%s" % ( tokenList[0], tokenList[1] )
                aKey = tokenList[1]

            if ( curVal == NA_VALUE ):
                numNA[aKey] += 1
            elif ( curVal == "NA" ):
                numNA[aKey] += 1
            else:
                numNot[aKey] += 1

        # print numNA
        # print numNot

        # check that the NA fraction does not exceed the limit ...
        for aKey in numNA.keys():

            # look at the fraction of NA values relative to the total ...
            numTot = numNA[aKey] + numNot[aKey]
            if ( numTot <= 0 ):
                print " --> no features of this type ", aKey
                continue

            tmpNAfrac = float(numNA[aKey])/float(numTot)

            # if this class of features doesn't have many counts, let's
            # leave it in regardless ...
            #     --> some times we may want to keep this, other times
            #         we may not want to ...
            if ( 0 ):
                if ( numTot < 50 ):
                    print " --> not subjecting this class of features to the NA fraction limit ", aKey, numTot, tmpNAfrac, maxNAfrac
                    continue

            # print aKey, numNA[aKey], numNot[aKey], numTot, tmpNAfrac, 
            # maxNAfrac
            print " --> testing ", aKey, numTot, tmpNAfrac, maxNAfrac, labelList[jG]
            if ( tmpNAfrac > maxNAfrac ):
                if ( jG not in skipList ):
                    skipList += [ jG ]
                    print "         --> will skip %s %5d %32s (%s,%5d,%5d) " % ( rowColFlag, jG, labelList[jG], aKey, numNot[aKey], numNA[aKey] ), numNA

    print "     returning from getSkipList: "
    if ( len(skipList) > 0 ):
        print "     --> skipping a total of %d %s " % ( len(skipList), rowColFlag )
    else:
        print "     --> NOT skipping any %s " % ( rowColFlag )

    return ( skipList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def addConstFeature ( dataD, newFeatureName, newFeatureValue ):

    print " "
    print " --> in addConstFeature ... <%s> <%s> " % ( newFeatureName, newFeatureValue )
    print " "

    numRow = len ( dataD['rowLabels'] )
    numCol = len ( dataD['colLabels'] )
    for iRow in range(numRow):
        if (newFeatureName == dataD['rowLabels'][iRow]):
            print "     NOT adding this feature ... already exists ... ", dataD['rowLabels'][iRow]
            return (dataD)

    dataD['rowLabels'] += [ newFeatureName ]
    dataMatrix = [0] * (numRow+1)
    for iR in range(numRow+1):
        if ( iR < numRow ):
            dataMatrix[iR] = dataD['dataMatrix'][iR]
        else:
            dataMatrix[iR] = [ newFeatureValue ] * numCol

    dataD['dataMatrix'] = dataMatrix

    return ( dataD )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lookAtDataD ( dataD ):

    try:
        print "         >>>>", dataD.keys()
        print "         >>>>", dataD['dataType']
    except:
        print " no data to look at ??? "
        return ( )

    if ( len(dataD['rowLabels']) < 8 ):
        print "         >>>>", dataD['rowLabels']
    else:
        print "         >>>>", dataD['rowLabels'][:3], " ... ", dataD['rowLabels'][-3:]

    if ( len(dataD['colLabels']) < 8 ):
        print "         >>>>", dataD['colLabels']
    else:
        print "         >>>>", dataD['colLabels'][:3], " ... ", dataD['colLabels'][-3:]

    print "         >>>>", len(dataD['rowLabels']), len(dataD['colLabels'])
    print "         >>>>", len(dataD['dataMatrix']), len(dataD['dataMatrix'][0])

    if ( len(dataD['rowLabels']) != len(dataD['dataMatrix']) ):
        print " ERROR in lookAtDataD ... why do these dimensions not match ??? !!! ", len(dataD['rowLabels']), len(dataD['dataMatrix'])
        sys.exit(-1)

    if ( len(dataD['colLabels']) != len(dataD['dataMatrix'][0]) ):
        print " ERROR in lookAtDataD ... why do these dimensions not match ??? !!! ", len(dataD['colLabels']), len(dataD['dataMatrix'][0])
        sys.exit(-1)

    # check for blank tokens ...
    numRow = len(dataD['rowLabels'])
    numCol = len(dataD['colLabels'])
    for ii in range(numRow):
        for jj in range(numCol):
            if ( dataD['dataMatrix'][ii][jj] == "" ):
                print " ERROR ??? data matrix has a blank token ??? "
                print ii, jj, dataD['dataMatrix'][ii][jj]
                sys.exit(-1)

    # count up number of missing values ...
    numNA = 0
    numNot = 0
    for ii in range(numRow):
        for jj in range(numCol):
            if ( dataD['dataMatrix'][ii][jj] == NA_VALUE ):
                numNA += 1
            elif ( dataD['dataMatrix'][ii][jj] == "NA" ):
                numNA += 1
            else:
                numNot += 1

    numTot = numNA + numNot
    if ( numTot != (numRow*numCol) ):
        print " why do these not match ??? ", numRow, numCol, (numRow*numCol), numTot
    fracNA = float(numNA)/float(numTot)
    print " number of cells in data matrix .... %12d " % numTot
    print " number of data values ............. %12d  (%5.3f) " % ( numNot, (1.-fracNA) )
    print " number of missing values .......... %12d  (%5.3f) " % ( numNA, fracNA )
    print " "

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def dataMatrix_stats ( dataMatrix, type ):

    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print " in tsvIO.dataMatrix_stats ... ", numRow, numCol, type

    if ( type == 'row' ):

        meanVec = numpy.zeros ( numRow )
        sigmaVec = numpy.zeros ( numRow )
        countVec = numpy.zeros ( numRow )
        maxVec   = numpy.zeros ( numRow )
        minVec   = numpy.zeros ( numRow )

        tmpVec = numpy.zeros ( numCol )

        for ii in range(numRow):

            kk = 0
            sum1 = 0.
            sum2 = 0.
            minVal = -NA_VALUE - 100
            maxVal =  NA_VALUE + 100

            allFloat = 1
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal != NA_VALUE ):
                    try:
                        floatVal = float(curVal)
                    except:
                        # if ( allFloat ): print " --> will skip row #%d " % ( 
                        # ii+1 )
                        allFloat = 0
            if ( not allFloat ): 
                continue

            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal == NA_VALUE ): 
                    continue
                if ( curVal < minVal ): 
                    minVal = curVal
                if ( curVal > maxVal ): 
                    maxVal = curVal
                sum1 += ( curVal )
                sum2 += ( curVal * curVal )
                kk += 1

            countVec[ii] = kk
            minVec[ii] = minVal
            maxVec[ii] = maxVal
            if ( kk < 3 ):
                meanVec[ii] = NA_VALUE
                sigmaVec[ii] = NA_VALUE

            else:
                mean1 = sum1 / float(kk)
                mean2 = sum2 / float(kk)
                try:
                    sigma = math.sqrt ( mean2 - (mean1*mean1) )
                except:
                    print " ERROR computing sigma ??? ", kk, mean2, mean1, mean1*mean1, (mean2-(mean1*mean1))
                    sigma = NA_VALUE

                if ( 0 ):
                    if ( sigma < 0.0005 ):
                        print " how do we get such a small value for sigma ??? ", kk, mean1, mean2, mean1*mean1, (mean2-(mean1*mean1))

                meanVec[ii] = mean1
                sigmaVec[ii] = sigma

        print " returning mean and sigma output vectors of length ", len(meanVec)
        return ( meanVec, sigmaVec, minVec, maxVec, countVec )

    elif ( type == 'col' ):

        meanVec = numpy.zeros ( numCol )
        sigmaVec = numpy.zeros ( numCol )
        countVec = numpy.zeros ( numCol )
        maxVec   = numpy.zeros ( numRow )
        minVec   = numpy.zeros ( numRow )

        tmpVec = numpy.zeros ( numRow )

        for ii in range(numCol):

            kk = 0
            sum1 = 0.
            sum2 = 0.
            minVal = -NA_VALUE - 100
            maxVal =  NA_VALUE + 100

            allFloat = 1
            for jj in range(numRow):
                curVal = dataMatrix[jj][ii]
                if ( curVal != NA_VALUE ):
                    try:
                        float(curVal)
                    except:
                        allFloat = 0
            if ( not allFloat ): 
                continue

            for jj in range(numRow):
                curVal = dataMatrix[jj][ii]
                if ( curVal == NA_VALUE ): 
                    continue
                if ( curVal < minVal ): 
                    minVal = curVal
                if ( curVal > maxVal ): 
                    maxVal = curVal
                sum1 += ( curVal )
                sum2 += ( curVal * curVal )
                kk += 1

            countVec[ii] = kk
            minVec[ii] = minVal
            maxVec[ii] = maxVal

            if ( kk < 3 ):
                meanVec[ii] = NA_VALUE
                sigmaVec[ii] = NA_VALUE

            else:
                mean1 = sum1 / float(kk)
                mean2 = sum2 / float(kk)
                try:
                    sigma = math.sqrt ( mean2 - (mean1*mean1) )
                except:
                    print " ERROR computing sigma ??? ", kk, mean2, mean1, mean1*mean1, (mean2-(mean1*mean1))
                    sigma = NA_VALUE

                if ( 0 ):
                    if ( sigma < 0.0005 ):
                        print " how do we get such a small value for sigma ??? ", kk, mean1, mean2, mean1*mean1, (mean2-(mean1*mean1))

                meanVec[ii] = mean1
                sigmaVec[ii] = sigma

        print " returning mean and sigma output vectors of length ", len(meanVec)
        return ( meanVec, sigmaVec, minVec, maxVec, countVec )

    else:
        print " ERROR in dataMatrix_stats ... type should be either 'row' or 'col' ", type
        sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def dataMatrix_quantiles ( dataMatrix, type, nQuant ):

    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print " in tsvIO.dataMatrix_quantiles ... ", numRow, numCol, type

    qMat = [0] * (nQuant+1)

    if ( type == 'row' ):

        for iQ in range(nQuant+1):
            qMat[iQ] = numpy.zeros ( numRow )

        tmpVec = numpy.zeros ( numCol )

        for ii in range(numRow):

            kk = 0

            allFloat = 1
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal != NA_VALUE ):
                    try:
                        floatVal = float(curVal)
                    except:
                        allFloat = 0
            if ( not allFloat ): 
                continue

            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal == NA_VALUE ): 
                    continue
                tmpVec[kk] = curVal
                kk += 1

            nCount = kk
            srtVec = tmpVec[:nCount]
            srtVec.sort()

            if ( nCount < 2*nQuant ):
                for iQ in range(nQuant+1):
                    qMat[iQ][ii] = NA_VALUE

            else:

                srtVec = tmpVec[:nCount]
                srtVec.sort()

                for iQ in range(nQuant+1):
                    if ( iQ == 0 ): 
                        jj = 0
                    elif ( iQ == nQuant ): 
                        jj = nCount-1
                    else: 
                        jj = int ( float(nCount) * float(iQ)
                                   / float(nQuant)  +  0.50 )
                    qMat[iQ][ii] = srtVec[jj]

        print " returning quantiles ... %d x %d " % ( len(qMat), len(qMat[0]) )
        return ( qMat )

    elif ( type == 'col' ):
        print " not yet implemented !!! "
        sys.exit(-1)

    else:
        print " ERROR in dataMatrix_quantiles ... type should be either 'row' or 'col' ", type
        sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def dataMatrix_medianVec ( dataMatrix, type ):

    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print " in tsvIO.dataMatrix_medianVec ... ", numRow, numCol, type

    if ( type == 'row' ):

        medVec = numpy.zeros ( numRow )
        madVec = numpy.zeros ( numRow )
        numVec = numpy.zeros ( numRow )
        tmpVec = numpy.zeros ( numCol )
        for ii in range(numRow):
            medVec[ii] = NA_VALUE
            madVec[ii] = NA_VALUE
            allFloat = 1
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal != NA_VALUE ):
                    try:
                        floatVal = float(curVal)
                    except:
                        # if ( allFloat ): print " --> will skip row #%d " % ( 
                        # ii+1 )
                        allFloat = 0
            if ( not allFloat ): 
                continue
            kk = 0
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal == NA_VALUE ): 
                    continue
                tmpVec[kk] = curVal
                kk += 1
            numVec[ii] = kk
            if ( kk >= 5 ):
                try:
                    ( madVec[ii], medVec[ii] 
                      ) = miscMath.computeMAD ( tmpVec[:kk] )
                except:
                    print miscMath.computeMAD ( tmpVec[:kk] )
                    print kk, tmpVec[:kk]
                    sys.exit(-1)

        print " returning median output vector of length ", len(medVec)
        return ( medVec, madVec, numVec )

    elif ( type == 'col' ):

        medVec = numpy.zeros ( numCol )
        madVec = numpy.zeros ( numCol )
        numVec = numpy.zeros ( numCol )
        tmpVec = numpy.zeros ( numRow )
        for ii in range(numCol):
            allFloat = 1
            for jj in range(numRow):
                curVal = dataMatrix[jj][ii]
                if ( curVal != NA_VALUE ):
                    try:
                        floatVal = float(curVal)
                    except:
                        allFloat = 0
            if ( not allFloat ): 
                continue
            kk = 0
            for jj in range(numRow):
                curVal = dataMatrix[jj][ii]
                if ( curVal == NA_VALUE ): 
                    continue
                tmpVec[kk] = curVal
                kk += 1
            numVec[ii] = kk
            if ( kk < 3 ):
                medVec[ii] = NA_VALUE
                madVec[ii] = NA_VALUE
            else:
                ( madVec[ii], medVec[ii] ) = miscMath.computeMAD ( tmpVec[:kk] )

        print " returning median output vector of length ", len(medVec)
        return ( medVec, madVec, numVec )

    else:
        print " ERROR in dataMatrix_medianVec ... type should be either 'row' or 'col' ", type
        sys.exit(-1)


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def dataMatrix_histogram ( dataMatrix, histInfo=(-1,-1,-1,-1) ):

    ( minVal, maxVal, delVal, numBins ) = histInfo

    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print " in tsvIO.dataMatrix_histogram ... ", numRow, numCol, numBins
    print minVal, maxVal, delVal, numBins

    # if we have not been given the histogram range, etc, then figure
    # out some suitable values here ...

    if ( numBins == -1 ):

        # first need to figure out the range of this data ...
        # as well as the total number of non-NA samples
        minVal =  9999
        maxVal = -9999
        totSamp = 0
        for ii in range(numRow):
            allFloat = 1
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal != NA_VALUE ):
                    try:
                        floatVal = float(curVal)
                    except:
                        # if ( allFloat ): print " --> will skip row #%d " % ( 
                        # ii+1 )
                        allFloat = 0
            if ( not allFloat ): 
                continue
            for jj in range(numCol):
                curVal = dataMatrix[ii][jj]
                if ( curVal != NA_VALUE ):
                    totSamp += 1
                    if ( minVal > curVal ): 
                        minVal = curVal
                    if ( maxVal < curVal ): 
                        maxVal = curVal

        print totSamp, minVal, maxVal

        # try to figure out a nice bin size that will produce ~100 useful bins

        # first we want to have the # of bins depend somewhat on the
        # number of data samples we have, but we also don't want, to
        # hae too many bins ...
        numBins = min ( int(totSamp/1000), 50 )
        print numBins
        # next we want to come up with 'nice' intervals ...
        delVal = (maxVal-minVal) / float(numBins)
        log10_delVal = math.log10 ( delVal )
        ilog10 = int ( log10_delVal )
        idel = abs ( log10_delVal - ilog10 )
        # print delVal, log10_delVal, ilog10, idel
        delVal = 10.**(float(ilog10))
        if ( idel > 0.6 ): 
            delVal = delVal * 0.2
        elif ( idel > 0.4 ): 
            delVal = delVal * 0.4
        elif ( idel > 0.3 ): 
            delVal = delVal * 0.4
        # print delVal
        minVal = float(delVal) * ( int(minVal/delVal) - 1 )
        maxVal = float(delVal) * ( int(maxVal/delVal) + 1 )
        # print minVal, maxVal
        numBins = int( ((maxVal-minVal)/delVal) + 1.1 )
        # print numBins
        print " --> chosen bin specs: ", minVal, maxVal, delVal, numBins

    # build histogram ...
    hist = [0] * numBins
    numTot = 0
    for ii in range(numRow):

        allFloat = 1
        for jj in range(numCol):
            curVal = dataMatrix[ii][jj]
            if ( curVal != NA_VALUE ):
                try:
                    floatVal = float(curVal)
                except:
                    allFloat = 0
        if ( not allFloat ): 
            continue

        for jj in range(numCol):
            curVal = dataMatrix[ii][jj]
            if ( curVal == NA_VALUE ): 
                continue
            ibin = int(((curVal-minVal)/delVal)  +  0.001)
            if ( ibin < 0 ):
                print " WARNING !!! resetting bin value to 0 ... ", curVal, ibin
                ibin = 0
            if ( ibin > (numBins-1) ):
                print " WARNING !!! resetting bin value to numBins-1 ... ", curVal, ibin, numBins
                ibin = numBins-1
            try:
                hist[ibin] += 1
            except:
                print " ERROR : ", ibin, curVal, minVal, delVal
                sys.exit(-1)
            numTot += 1

    # now strip off any leading or trailing bins with zero counts ...
    iFirst = 0
    while ( hist[iFirst] == 0 ): 
        iFirst += 1
    iLast = numBins - 1
    while ( hist[iLast] == 0 ): 
        iLast -= 1
    print " iFirst=%d    iLast=%d    (numBins=%d) " % ( iFirst, iLast, numBins )

    if ( 0 ):
        # print out the histogram ...
        cumTot = 0
        for ibin in range(iFirst,iLast+1):
            if ( hist[ibin] > 0 ):
                curVal = (float(ibin)+0.5) * delVal  +  minVal
                curFrac = float(hist[ibin])/float(numTot)
                cumTot += hist[ibin]
                cumFrac = float(cumTot)/float(numTot)
                print " %12d  %3d  %8.3f  %6.4f  %6.4f " % ( hist[ibin], ibin, curVal, curFrac, cumFrac )

    histInfo = ( 
        ((minVal+float(iFirst)*delVal), (maxVal-(float(numBins-iLast-1)*delVal)), delVal, 
        numBins-iFirst-(numBins-iLast-1) ), hist[iFirst:iLast+1], numTot)

    print " --> returning histInfo[0] : ", histInfo[0]

    return ( histInfo )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getSampleOverlap ( dataA, dataB ):

    colLabelsA = dataA['colLabels']
    colLabelsB = dataB['colLabels']

    overlapList = []
    isTCGA = 0

    if ( colLabelsA[0].startswith("TCGA-") ):
        if ( colLabelsB[0].startswith("TCGA-") ):
            isTCGA = 1

    if ( not isTCGA ):
        print " ERROR in getSampleOverlap, expecting TCGA barcodes "
        print colLabelsA[:5]
        print colLabelsB[:5]
        sys.exit(-1)

    for aSample in colLabelsA:
        if ( aSample in overlapList ): 
            continue
        for bSample in colLabelsB:
            if ( isTCGA ):
                if ( aSample[:12] == bSample[:12] ):
                    overlapList += [ aSample ]

    return ( overlapList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def filter_dataMatrix ( dataD, rmRowList, rmColList ):

    numRowDel = len(rmRowList)
    numColDel = len(rmColList)
    if ( (numRowDel+numColDel) == 0 ): 
        return ( dataD )

    rowLabels  = dataD['rowLabels']
    colLabels  = dataD['colLabels']
    dataMatrix = dataD['dataMatrix']

    # old dimensions
    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])

    # new dimensions
    numRowNew = numRow - numRowDel
    numColNew = numCol - numColDel

    print " in filter_dataMatrix ... "
    print "          input dimensions %5d x %5d " % ( numRow, numCol )
    print "         output dimensions %5d x %5d " % ( numRowNew, numColNew )
    if ( numRowNew*numColNew < 1 ):
        print " ERROR ??? we've lost all of the data ??? "
        sys.exit(-1)

    # allocate new space ...
    newRowLabels = []
    newColLabels = []
    newMatrix = [0] * numRowNew
    for ii in range(numRowNew):
        newMatrix[ii] = [0] * numColNew

    # copy the row labels we are keeping
    for ii in range(numRow):
        if ( ii not in rmRowList ):
            newRowLabels += [ rowLabels[ii] ]

    # copy the column labels we are keeping
    for jj in range(numCol):
        if ( jj not in rmColList ):
            newColLabels += [ colLabels[jj] ]

    # copy the data we are keeping
    i2 = 0
    for ii in range(numRow):
        if ( ii not in rmRowList ):
            j2 = 0
            for jj in range(numCol):
                if ( jj not in rmColList ):
                    newMatrix[i2][j2] = dataMatrix[ii][jj]
                    j2 += 1
            i2 += 1

    newD = {}
    newD['rowLabels'] = newRowLabels
    newD['colLabels'] = newColLabels
    newD['dataType'] = dataD['dataType']
    newD['dataMatrix'] = newMatrix

    return ( newD )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def pruneTSV_dataMatrix ( dataD, rowMaxNAfrac, colMaxNAfrac, pruneOrder ):

    rowLabels  = dataD['rowLabels']
    colLabels  = dataD['colLabels']

    print " in pruneTSV_dataMatrix ... ", len(rowLabels), len(colLabels), pruneOrder

    # double check that all of the row names and column names are unique
    rmRowList = checkUnique ( rowLabels )
    rmColList = checkUnique ( colLabels )

    dataD = filter_dataMatrix ( dataD, rmRowList, rmColList )
    lookAtDataD ( dataD )

    # -------------------------------------------------------------------
    # if there are any genes/probes or samples that have NO data, then
    # we don't even want to write it out ...

    # print " checking for features and/or samples that have too much missing 
    # data ... "

    nPass = len(pruneOrder)
    print " --> pruning in %d passes ... " % nPass

    for iPass in range(nPass):

        curChar = pruneOrder[iPass].upper()
        if ( curChar == "C" ):
            if ( colMaxNAfrac < 1. ):
                skipColList = getSkipList ( colMaxNAfrac, dataD, 'col' )
                dataD = filter_dataMatrix ( dataD, [], skipColList )
                lookAtDataD ( dataD )
        elif ( curChar == "R" ):
            if ( rowMaxNAfrac < 1. ):
                skipRowList = getSkipList ( rowMaxNAfrac, dataD, 'row' )
                dataD = filter_dataMatrix ( dataD, skipRowList, [] )
                lookAtDataD ( dataD )
        else:
            print " ERROR in pruneTSV_dataMatrix ... invalid pruneOrder string ??? ", pruneOrder
            sys.exit(-1)

    numRow = len(dataD['dataMatrix'])
    numCol = len(dataD['dataMatrix'][0])
    print " --> finished in pruneTSV_dataMatrix ... %d rows x %d columns " % ( numRow, numCol )
    print dataD['dataType']
    print len(dataD['rowLabels']), len(dataD['colLabels'])

    return ( dataD )

#------------------------------------------------------------------------------

def uniqueFeatureLabels ( fLabels, dataMatrix ):

    print " in uniqueFeatureLabels ... "
    numRename = 0
    numRemove = 0

    if ( 0 ):
        print len(fLabels)
        print fLabels[:5]
        print fLabels[-5:]
        sys.exit(-1)

    rmRowList = set()
    
    label2indices = {}
    for index, fLabel in enumerate(fLabels):
        indices = label2indices.setdefault(fLabel, set())
        indices.add(index)
        
    for fLabel, indices in label2indices.iteritems():
        for ii in range(len(indices)):
            if ( ii in rmRowList ): 
                continue
            for jj in range(ii+1,len(indices)):
                if ( jj in rmRowList ): 
                    continue
                # 23apr13 : first let's check and see if the data is the same ...
                aVec = dataMatrix[ii]
                bVec = dataMatrix[jj]
                print fLabel, aVec[:10]
                print fLabel, bVec[:10]
                if ( aVec == bVec ):
                    print " identical !!! "
                    rmRowList.add(jj)
                    numRemove += 1
        indices = indices.difference(rmRowList)
        for ii in indices:
            try:
                newA = fLabel + str(ii)
            except:
                print fLabel
                sys.exit(-1)
            fLabels[ii] = newA
            print " <%s> renamed to <%s>" % ( fLabel, newA)
            numRename += 1
        
    if ( numRemove > 0 ):
        print " need to remove %d features " % numRemove
        sys.exit(-1)

    if ( numRename > 0 ):
        print " --> %d features were renamed to ensure uniqueness " % numRename

    return ( fLabels )

#------------------------------------------------------------------------------

def writeTSV_dataMatrix ( dataD, sortRowFlag,  sortColFlag, outFilename ):
    try:
        rowLabels  = dataD['rowLabels']
        colLabels  = dataD['colLabels']
        if ( len(rowLabels) == 0 ):
            print " ERROR in writeTSV_dataMatrix ??? zero rows ??? "
            return ( )
        if ( len(colLabels) == 0 ):
            print " ERROR in writeTSV_dataMatrix ??? zero columns ??? "
            return ( )
    except:
        print " ERROR in writeTSV_dataMatrix ??? bad data ??? "
        print dataD.keys()
        return ( )

    print datetime.now(), "in writeTSV_dataMatrix ... ", outFilename, len(rowLabels), len(colLabels)

    for kk in range(len(colLabels)):
        colName = colLabels[kk]
        if ( colName.startswith("tcga-") ):
            newName = colName.upper()
            colLabels[kk] = newName

    if ( not outFilename.endswith(".tsv") ):
        outFilename += ".tsv"

    try:
        fh = file ( outFilename, 'w' )
    except:
        print " ERROR ... failed to open output file <%s> " % outFilename
        try:
            buildPath ( outFilename )
            fh = file ( outFilename, 'w' )
        except:
            print " --> couldn't recover ... bailing "
            sys.exit(-1)

    lookAtDataD ( dataD )
    print '     (b) TIME ', datetime.now()
    
    dataMatrix = dataD['dataMatrix']

    numRow = len(rowLabels)
    numCol = len(colLabels)

    # -------------------------------------------------------------------
    # depending on the input flags, we may want to re-sort the sample
    # and 'gene' labels ...
    # print " --> reordering sample names and gene (or probe) names ... "

    tmpColList = []
    for aSample in colLabels:
        tmpColList += [ aSample ]

    newColOrder = [0] * len(colLabels)
    if ( not sortColFlag ):
        for index in range(len(colLabels)):
            newColOrder[index] = index
    else:
        tmpColList.sort()
        print '        sorted list of samples:', tmpColList[0], tmpColList[-1]
        # print " new column order : ", newColOrder[0:20]
        label2index = {}
        for index, label in enumerate(colLabels):
            label2index[label] = index
        
        for index, label in enumerate(tmpColList):
            origIndex = label2index[label]
            newColOrder[index] = origIndex
                
    # make sure that the rowLabels are unique!
    # this takes WAY TOOOOO looooong ...
    if ( 0 ):
        print " calling uniqueFeatureLabels ... ", len(rowLabels), rowLabels[0], rowLabels[-1]
        rowLabels = uniqueFeatureLabels ( rowLabels, dataMatrix )

    tmpRowList = []
    for aLabel in rowLabels:
        tmpRowList += [ aLabel ]

    newRowOrder = [0] * len(rowLabels)
    if ( not sortRowFlag ):
        for index in range(len(rowLabels)):
            newRowOrder[index] = index
    else:
        tmpRowList.sort()
        print '        sorted list of features:', tmpRowList[0], tmpRowList[-1]
        label2index = {}
        for index, label in enumerate(rowLabels):
            label2index[label] = index
        
        for index, label in enumerate(tmpRowList):
            origIndex = label2index[label]
            newRowOrder[index] = origIndex
        # print " new row order : ", newRowOrder[0:20]
                
    print '     (c) TIME ', datetime.now()
    # use the "type" in the top-left corner of the output data file
    tokenList = rowLabels[0].split(':')
    cornerString = dataD['dataType']
    if ( cornerString == "" ):
        if ( len(tokenList[0])==1 and len(tokenList[1])==4 ):
            cornerString = tokenList[0] + ":" + tokenList[1]
        else:
            cornerString = "M:MISC"
    # print " cornerString : <%s> " % cornerString
    # OLD, with quotes: aLine = '"%s"' % cornerString
    aLine = '%s' % cornerString
    ## aLine = ""

    numSout = 0
    numGout = 0

    for iS in range(numCol):
        jS = newColOrder[iS]
        numSout += 1
        aSample = colLabels[jS]
        # sanity check:
        if ( tmpColList[iS] != colLabels[jS] ):
            print " S : ERROR ??? shouldn't these match ??? "
            print iS, tmpColList[iS], jS, colLabels[jS]
            sys.exit(-1)
        # OLD, with quotes: aLine += '\t"%s"' % aSample
        aLine += '\t%s' % aSample
    fh.write ( "%s\n" % aLine )

    fTypeDict = {}
    numNA = 0
    numNot = 0

    print '     (d) TIME ', datetime.now()
    for iG in range(numRow):
        jG = newRowOrder[iG]
        numGout += 1
        # OLD, with quotes: aLine = '"%s"' % tmpRowList[iG]
        ## aLine = '%s' % tmpRowList[iG]
        aLine = "%s" % ( replaceBlanks ( tmpRowList[iG], '_' ) )
        tokenList = tmpRowList[iG].split(':')
        # print " CHECK: ", tokenList, iG, tmpRowList[iG]
        fType = "%s:%s" % ( tokenList[0], tokenList[1] )
        if ( fType not in fTypeDict.keys() ):
            fTypeDict[fType] = 0
        fTypeDict[fType] += 1
        # sanity check:
        if ( tmpRowList[iG] != rowLabels[jG] ):
            print " G : ERROR ??? shouldn't these match ??? "
            print iG, tmpRowList[iG], jG, rowLabels[jG]
            sys.exit(-1)
        for iS in range(numCol):
            jS = newColOrder[iS]
            if ( dataMatrix[jG][jS] == "" ):
                print " ERROR ??? blank token in dataMatrix ??? ", jG, jS
                sys.exit(-1)
            if ( dataMatrix[jG][jS] != NA_VALUE ):
                if ( tokenList[0] == "N" ):
                    if ( dataMatrix[jG][jS] >= 0 ):
                        iVal = int ( dataMatrix[jG][jS] + 0.1 )
                    else:
                        iVal = int ( dataMatrix[jG][jS] - 0.1 )
                    if ( abs(iVal-dataMatrix[jG][jS]) < 0.001 ):
                        aLine += "\t%d" % iVal
                    else:
                        aLine += "\t%.3f" % dataMatrix[jG][jS]
                else:
                    try:
                        if ( dataMatrix[jG][jS] >= 0. ):
                            iVal = int ( dataMatrix[jG][jS] + 0.1 )
                        else:
                            iVal = int ( dataMatrix[jG][jS] - 0.1 )
                        if ( abs(iVal-dataMatrix[jG][jS]) < 0.001 ):
                            aLine += "\t%d" % dataMatrix[jG][jS]
                        else:
                            aLine += "\t%s" % dataMatrix[jG][jS]
                    except:
                        aLine += "\t%s" % dataMatrix[jG][jS]
                numNot += 1
            else:
                aLine += "\tNA"
                numNA += 1
        fh.write ( "%s\n" % aLine )

    fh.close()

    numTot = numNA + numNot
    fracNA = float(numNA)/float(numTot)

    print " "
    print datetime.now(), "--> finished in writeTSV_dataMatrix ... wrote out %d rows x %d columns %5.3f NA in %s " % ( numGout, numSout, fracNA, outFilename  )
    print "     ", fTypeDict
    print " "

#------------------------------------------------------------------------------
# "clinical" tsv files and "data" tsv files are somewhat different, so we need
# to figure out which type we have and handle it appropriately
#
# at the moment, clinical tsv files have TCGA patients as the rows, with
# clinical data elements as the columns, and the first column has the
# barcode, with the column label being "bcr_patient_barcode"
#
# "data" tsv files, meanwhile are large data matrices with the samples being
# the columns and the data features (genes, CN segments, etc) being the rows

def readTSV ( inName ):

    # we should just need the first row to figure out what we have ...
    try:
        fh = file ( inName )
        hdrLine = fh.readline()
        fh.close()
    except:
        return ( {} )

    hdrTokens = hdrLine.split('\t')

    if (len(hdrTokens) < 2):
        return ({})

    # does the first column header look like a barcode / sample ID ???
    isClinical = 0
    firstColHdr = (hdrTokens[0]).lower()
    # print " in readTSV ... ", firstColHdr
    if ( firstColHdr == "bcr_patient_barcode" ): 
        isClinical = 1
    if ( firstColHdr.find("barcode") >= 0 ): 
        isClinical = 1
    if ( firstColHdr.find("sample") >= 0 ): 
        isClinical = 1
    if ( firstColHdr.find("patient") >= 0 ): 
        isClinical = 1
    if ( firstColHdr.find("tcga_id") >= 0 ): 
        isClinical = 1
    if ( isClinical ):
        # this returns a dictionary, where the keys are data elements
        # and each one has a vector of values (or strings), for the
        # N patients
        return ( readTSV_clinical ( inName ) )
    else:
        return ( readTSV_dataMatrix ( inName ) )

#------------------------------------------------------------------------------

def fixFeatureName ( rowTokens ):

    # print " in fixFeatureName ... ", rowTokens

    bitMutFlag = 0
    fltMutFlag = 0
    bitMutStrings = [ 'y_n', '_nonsilent', '_dna_bin', '_ns_or_fs', '_dom_',
                      '_missense', '_mnf', '_mni', '_code_potential', '_DNA_interface' ]
    fltMutStrings = [ '_binding_delta', 
                     '_bound_delta', '_oe_score', '_iarc_freq' ]

    dataTypeList = [ "B", "N", "C" ]
    featTypeList = [ "CLIN", "SAMP", "GNAB", 
                    "CNVR", "GEXP", "MIRN", "METH", "PRDM" ]

    if ( len(rowTokens) == 1 ):
        tmpName = rowTokens[0]
        for aString in bitMutStrings:
            if ( tmpName.find(aString) > 0 ): 
                bitMutFlag = 1
        for aString in fltMutStrings:
            if ( tmpName.find(aString) > 0 ): 
                fltMutFlag = 1

        # some of the "bound_delta" features are binary and some are continuous 
        # ...
        if ( fltMutFlag ):
            if ( tmpName.find("bound_delta_ge_") > 0 ):
                bitMutFlag = 1
                fltMutFlag = 0

        if ( bitMutFlag ):
            ii = tmpName.find("_")
            geneName = tmpName[:ii]
            newName = "B:GNAB:" + geneName + \
                ":::::" + rowTokens[0][ii+1:] + "_mut"
            return ( newName )
        elif ( fltMutFlag ):
            ii = tmpName.find("_")
            geneName = tmpName[:ii]
            newName = "N:GNAB:" + geneName + \
                ":::::" + rowTokens[0][ii+1:] + "_mut"
            return ( newName )

    elif ( len(rowTokens) == 3 ):
        if ( rowTokens[0] in dataTypeList ):
            if ( rowTokens[1] in featTypeList ):
                newName = rowTokens[0] + ":" + \
                    rowTokens[1] + ":" + rowTokens[2] + ":::::"
                return ( newName )

    elif ( len(rowTokens) >= 3 ):
        if ( len(rowTokens[0]) == 1 ):
            if ( len(rowTokens[1]) == 4 ):

                if ( rowTokens[1] == "GNAB" ):
                    tmpName = rowTokens[2]
                    if ( tmpName.find("y_n") > 0 ): 
                        bitMutFlag = 1
                    if ( tmpName.find("_nonsilent") > 0 ): 
                        bitMutFlag = 1
                    if ( tmpName.find("_dna_bin") > 0 ): 
                        bitMutFlag = 1
                    if ( tmpName.find("_ns_or_fs") > 0 ): 
                        bitMutFlag = 1
                    if ( tmpName.find("_dom_") > 0 ): 
                        bitMutFlag = 1
                    if ( bitMutFlag ):
                        ii = tmpName.find("_")
                        geneName = tmpName[:ii]
                        newName = "B:GNAB:" + geneName + \
                            ":::::" + rowTokens[0][ii+1:] + "_mut"
                        return ( newName )

                elif ( rowTokens[1] == "RPPA" ):
                    newName = rowTokens[0]
                    for ii in range(1,len(rowTokens)):
                        newName += ":"
                        newName += rowTokens[ii]
                    return ( newName )

                elif (len(rowTokens) == 6):
                    newName = rowTokens[0] + ":" + rowTokens[1] + ":" + rowTokens[2] + \
                        ":" + rowTokens[3] + ":" + \
                        rowTokens[4] + ":" + rowTokens[5] + ":"
                    return (newName)

    print " ERROR in fixFeatureName ... do not know what to do with these name tokens : ", len(rowTokens), rowTokens
    sys.exit(-1)
    # print " --> will remove this feature from merge ... "
    return ( '' )

#------------------------------------------------------------------------------

def buildName ( tokenList, aSep ):

    newName = tokenList[0]
    for ii in range(len(tokenList)-1):
        newName += aSep
        newName += tokenList[ii+1]

    return ( newName )

#------------------------------------------------------------------------------

def makeData ( dataType, numRow, numCol ):

    outDict = {}

    outDict['dataType'] = dataType
    outDict['rowLabels'] = [''] * numRow
    outDict['colLabels'] = [''] * numCol

    dataMatrix = [0] * numRow
    for ii in range(numRow):
        dataMatrix[ii] = [0] * numCol

    outDict['dataMatrix'] = dataMatrix

    return ( outDict )

#------------------------------------------------------------------------------
# this file reads a data tsv file ...

def readTSV_dataMatrix ( inName ):

    print " in readTSV_dataMatrix ... ", inName

    outDict = {}

    fh = file ( inName )
    numCol = miscIO.num_cols ( fh, '\t' )
    numRow = miscIO.num_lines ( fh )
    fh.close()

    numRow -= 1
    numCol -= 1

    outDict['rowLabels'] = [''] * numRow
    dataMatrix = [0] * numRow
    for ii in range(numRow):
        dataMatrix[ii] = [0] * numCol

    tsvReader = csv.reader ( 
        open(inName,'rb'), delimiter='\t', quoting=csv.QUOTE_NONE )
    ii = -1

    # print " looping over rows ... "

    for row in tsvReader:

        # print row
        if ( len(row) != (numCol+1) ):
            print " ERROR ??? inconsistent number of cols ??? "
            print len(row), numCol
            print row
            sys.exit(-1)

        if ( ii < 0 ):

            outDict['dataType'] = row[0]
            outDict['colLabels'] = row[1:]

        else:

            newName = row[0]
            outDict['rowLabels'][ii] = newName

            # sanity check feature name
            rowTokens = row[0].split(':')
            # print " sanity check : ", len(rowTokens), rowTokens

            if ( len(rowTokens) == 7 ):
                rowTokens += ['']
                newName = outDict['rowLabels'][ii] + ':'
            if ( len(rowTokens) != 8 ):
                newName = fixFeatureName ( rowTokens )
                if ( newName == '' ):
                    continue

            newName = fixWeirdCharacters ( newName )

            if ( newName != row[0] ):
                outDict['rowLabels'][ii] = newName
                # print "     subbing in new name <%s> for <%s> " % ( newName, row[0] )
                # sys.exit(-1)

            if ( newName.startswith("C:") ):
                for jj in range(numCol):
                    dataMatrix[ii][jj] = row[jj+1]
                    if (dataMatrix[ii][jj] == ""):
                        dataMatrix[ii][jj] = "NA"
            elif ( newName.startswith("B:") ):
                for jj in range(numCol):
                    try:
                        dataMatrix[ii][jj] = int ( row[jj+1] )
                    except:
                        dataMatrix[ii][jj] = row[jj+1]
                        if (dataMatrix[ii][jj] == ""):
                            dataMatrix[ii][jj] = NA_VALUE
            elif ( newName.startswith("N:") ):
                for jj in range(numCol):
                    if (row[jj + 1] == ""):
                        dataMatrix[ii][jj] = NA_VALUE
                    else:
                        try:
                            dataMatrix[ii][jj] = float ( row[jj+1] )
                        except:
                            if ( row[jj+1] == "NA" ):
                                dataMatrix[ii][jj] = NA_VALUE
                            else:
                                print " ERROR ??? unknown value in data matrix ??? ", row[jj+1]
                                print "     row : <%s> " % row[:40]
                                print "     jj  : %d   <%s> " % ( (jj+1), row[jj+1] )
                                sys.exit(-1)
            else:
                print " ERROR in readTSV_dataMatrix ??? "
                print rowTokens
                sys.exit(-1)


        ii += 1

    # print ii, numRow
    if ( numRow == -1 ):
        print " ERROR in readTSV_dataMatrix ??? no data ??? "
        return ( {} )

    if ( ii < (numRow-1) ):
        print " need to fix # of rows ... ", numRow, ii+1
        numRow = ii + 1
        outDict['rowLabels'] = outDict['rowLabels'][:numRow]
        newMatrix = [0] * numRow
        for ii in range(numRow):
            newMatrix[ii] = [0] * numCol
            for jj in range(numCol):
                newMatrix[ii][jj] = dataMatrix[ii][jj]
        dataMatrix = newMatrix

    outDict['dataMatrix'] = dataMatrix

    # HACK
    if ( 1 ):
        if ( outDict['dataType'] == "GEXP" ): 
            outDict['dataType'] = "N:GEXP"
        if ( outDict['dataType'] == "METH" ): 
            outDict['dataType'] = "N:METH"
        if ( outDict['dataType'] == "CNVR" ): 
            outDict['dataType'] = "N:CNVR"

    # print " returning ... "
    # print len(outDict['colLabels']), outDict['colLabels'][:5]
    # print len(outDict['rowLabels']), outDict['rowLabels'][:5]
    # print len(outDict['dataMatrix']), len(outDict['dataMatrix'][0])
    # sys.exit(-1)

    for kk in range(len(outDict['colLabels'])):

        colName = outDict['colLabels'][kk]
        ucName = colName.upper()
        # print kk, ucName

        tmpTokens = ucName.split("-")
        if ( len(tmpTokens) < 3 ):
            print " ERROR ??? invalid column name ??? "
            print ucName
            sys.exit(-1)

        if ( tmpTokens[0] == "ITMI" ):
            doNothing = 1
        elif ( tmpTokens[0] != "TCGA" ):
            print " replacing prefix <%s> with TCGA " % tmpTokens[0]
            tmpTokens[0] = "TCGA"
            ucName = buildName ( tmpTokens, "-" )
            print ucName

        if ( ucName.find("-TUMOR") > 0 ):
            print " need to fix this : <%s> " % ucName, tmpTokens
            newTokens = []
            for ii in range(len(tmpTokens)):
                print " looking at <%s> " % tmpTokens[ii]
                if ( tmpTokens[ii] != 'TUMOR' ):
                    newTokens += [ tmpTokens[ii] ]
            print newTokens
            ucName = buildName ( newTokens, "-" )
            print ucName
            tmpTokens = newTokens

        if ( ucName.find("-NATIVE") > 0 ):
            print " need to fix this : <%s> " % ucName, tmpTokens
            newTokens = []
            for ii in range(len(tmpTokens)):
                if ( tmpTokens[ii] != 'NATIVE' ):
                    newTokens += [ tmpTokens[ii] ]
            print newTokens
            ucName = buildName ( newTokens, "-" )
            print ucName
            tmpTokens = newTokens

        outDict['colLabels'][kk] = ucName

    return ( outDict )

#------------------------------------------------------------------------------

def parseTSVlabel ( aLabel ):
    tokenList = aLabel.split(':')

    if ( len(tokenList)<7 or len(tokenList)>8 ):
        print " ERROR in parseTSVlabel ... invalid ??? "
        print aLabel
        print tokenList
        sys.exit(-1)

    # return ( tokenList )
    dType = tokenList[0]
    fType = tokenList[1]
    fName = tokenList[2]
    cName = tokenList[3]
    startP = int ( tokenList[4] )
    endP   = int ( tokenList[5] )
    strand = tokenList[6]

    return ( dType, fType, fName, cName, startP, endP, strand )

#------------------------------------------------------------------------------

def fixToken ( aToken ):

    newToken = ""
    aToken = aToken.strip()
    aToken = str(aToken)
    for ii in range(len(aToken)):
        if ( aToken[ii] == " " ):
            if ( newToken[-1] != "_" ):
                newToken += "_"
        elif ( aToken[ii] == ":" ):
            if ( newToken[-1] != "_" ):
                newToken += "_"
        elif ( aToken[ii] == "/" ):
            if ( newToken[-1] != "_" ):
                newToken += "_"
        else:
            newToken += aToken[ii]

    if ( aToken == "_0" ):
        print " BAILING OUT FROM FIXTOKEN !!! ", aToken
        sys.exit(-1)

    return ( newToken )

#------------------------------------------------------------------------------
# this file reads in a clinical dataset in a TSV file and parses it into a
# dictionary called allClinDict

def readTSV_clinical ( inName ):

    print " "
    print " in readTSV_clinical ... ", inName

    # initialize dictionary
    allClinDict = {}

    # open file, read first line (with column labels), remove newline
    # character, and split at tabs
    fh = file ( inName )
    hdrLine = fh.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numHdrTokens = len(hdrTokens)
    print " %d hdrTokens : " % numHdrTokens, hdrTokens[:3], " ... ", hdrTokens[-3:]
    # print hdrTokens
    # print numHdrTokens

    # count up the number of lines that have the right number of tokens
    # in them -- this will be the number of "examples"
    numExamples = 0
    curPos = fh.tell()
    done = 0
    while not done:
        aLine = fh.readline()
        aLine = aLine.strip()
        # print " <%s> " % aLine
        if ( len(aLine) == 0 ): 
            done = 1
        try:
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            # print len(tokenList)
            if ( len(tokenList) == numHdrTokens ):
                numExamples += 1
        except:
            done = 1
    print " %d patients " % numExamples
    fh.seek ( curPos )

    # allocate space for the dictionary ... each column label is a
    # key and associated with that is a list of N pieces of information
    # where N is the number of examples (patients) we have
    for aToken in hdrTokens:
        # if ( aToken == '' ): continue
        aToken = aToken.strip()
        allClinDict[aToken] = [''] * numExamples

    ii = 0
    done = 0
    # now start reading through the rest of the file
    while not done:
        aLine = fh.readline()
        aLine = aLine.strip()
        # print " readTSV_clinical : %d  %d  aLine = <%s> " % ( ii, len(aLine), 
        # aLine )
        if ( len(aLine) == 0 ):
            done = 1
        else:
            try:
                aLine = aLine.strip()
                tokenList = aLine.split('\t')
                # print "     len(tokenList) = %d (%d) " % ( len(tokenList), 
                # numHdrTokens )
                if ( len(tokenList) == numHdrTokens ):
                    for kk in range(numHdrTokens):
                        aToken = hdrTokens[kk]
                        aToken = aToken.strip()
                        # if ( aToken == '' ): continue
                        allClinDict[aToken][ii] = fixToken ( tokenList[kk] )
                        # print " <%s>  %d  %d  " % ( aToken, ii, kk ), 
                        # tokenList[kk]
                    ii += 1
                else:
                    print " ERROR ??? wrong number of tokens ??? "
                    print len(tokenList), numHdrTokens, ii
                    print tokenList
                    print sys.exit(-1)
            except:
                print " HOW DID WE GET HERE ??? ", ii, kk, len(tokenList), len(hdrTokens), hdrTokens[kk], tokenList[kk]
                print " %d <%s> " % ( len(aLine), aLine )
                print tokenList
                print hdrTokens
                sys.exit(-1)
                done = 1

    print " --> ii = %d " % ii

    # HERE HERE
    # for aToken in allClinDict.keys():
    if ( 1 ):
        print " double-checking that we don't have any blank fields ... "
        for aToken in hdrTokens:
            print " aToken : <%s> " % aToken
            for kk in range(len(allClinDict[aToken])):
                if ( allClinDict[aToken][kk] == "" ):
                    if ( 1 ):
                        allClinDict[aToken][kk] = "NA"
                    else:
                        print " ERROR blank token ??? ", kk
                        allClinDict[aToken]
                        sys.exit(-1)

    # make sure that all barcodes are uppercase ...
    for kk in range(numHdrTokens):
        aKey = hdrTokens[kk]
        aKey = aKey.strip()
        for ii in range(len(allClinDict[aKey])):
            try:
                tmpS = allClinDict[aKey][ii].upper()
                if ( tmpS.startswith("TCGA-") ):
                    allClinDict[aKey][ii] = tmpS
            except:
                doNothing = 1

    # at this point all features are strings ... if any of them are
    # consistently numeric (except for "NA" or "NAN" values),
    # then recast them ...
    for kk in range(numHdrTokens):
        aKey = hdrTokens[kk]
        aKey = aKey.strip()
        if ( aKey == '' ): 
            continue

        # print " DEBUG : aKey=<%s> " % aKey
        # print allClinDict[aKey]

        # oddly enough it seems like they can get here and *not*
        # be strings ???  12sep13
        for ii in range(len(allClinDict[aKey])):
            allClinDict[aKey][ii] = str(allClinDict[aKey][ii])

        allNumeric = 1
        for ii in range(len(allClinDict[aKey])):
            if ( allClinDict[aKey][ii].upper() == "NA" ): 
                continue
            if ( allClinDict[aKey][ii].upper() == "NAN" ): 
                continue
            try:
                iVal = int ( allClinDict[aKey][ii] )
            except:
                try:
                    fVal = float ( allClinDict[aKey][ii] )
                except:
                    allNumeric = 0
        if ( allNumeric ):
            for ii in range(len(allClinDict[aKey])):
                if ( allClinDict[aKey][ii].upper() == "NA" ): 
                    continue
                if ( allClinDict[aKey][ii].upper() == "NAN" ): 
                    continue
                try:
                    iVal = int ( allClinDict[aKey][ii] )
                    allClinDict[aKey][ii] = iVal
                except:
                    fVal = float ( allClinDict[aKey][ii] )
                    allClinDict[aKey][ii] = fVal


    return ( allClinDict )

#------------------------------------------------------------------------------

def removeNearlyConstantRows ( tsvData, minFrac ):

    print " in removeNearlyConstantRows ... "

    skipRowList = []

    allKeys = tsvData.keys()

    dataMatrix = tsvData['dataMatrix']
    numRow = len(dataMatrix)
    numCol = len(dataMatrix[0])
    print len(dataMatrix), len(dataMatrix[0])
    print len(tsvData['colLabels'])
    print len(tsvData['rowLabels'])

    numKeep = 0
    numToss = 0
    for iRow in range(numRow):
        numNA = 0
        numZero = 0
        numOther = 0
        for iCol in range(numCol):
            # print iRow, iCol, dataMatrix[iRow][iCol]
            if ( dataMatrix[iRow][iCol] == NA_VALUE ):
                numNA += 1
            elif ( abs(dataMatrix[iRow][iCol]) < 0.0001 ):
                numZero += 1
            else:
                numOther += 1
        curFrac = float(numOther) / float(numZero+numOther)
        if ( curFrac < minFrac ):
            # print " eliminating this row ... ", iRow, 
            # tsvData['rowLabels'][iRow], numNA, numZero, numOther
            numToss += 1
            skipRowList += [ iRow ]
        else:
            # print " KEEPING this row ... \t%d\t%s\t%d\t%d\t%d" % ( iRow, 
            # tsvData['rowLabels'][iRow], numNA, numZero, numOther )
            numKeep += 1

        ## if ( numToss > 10 ): sys.exit(-1)
        ## if ( numKeep > 10 ): sys.exit(-1)

    print " number of rows to keep : ", numKeep
    print " number of rows to toss : ", numToss

    if ( skipRowList != [] ): 
        tsvData = filter_dataMatrix ( tsvData, skipRowList, [] )

    return ( tsvData )

#------------------------------------------------------------------------------
