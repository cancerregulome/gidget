# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import arffIO
import miscClin
import miscTCGA
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#	TCGA-AG-A02G-01A-01D-A008-01
#	          111111111122222222
#	0123456789012345678901234567


def fixCode(aCode):

    newCode = aCode.lower()
    if (newCode.startswith("tcga")):
        sepChr = newCode[4]
        if (sepChr == '-'):
            return (newCode)

        print " CASEFIXES: is this function used anymore ??? ", aCode
        print " Feb 2015 ... assuming NOT !!! "
        sys.exit(-1)

        newCode[4] = '-'
        newCode[7] = '-'
        if (len(newCode) > 12):
            newCode[12] = '-'
        if (len(newCode) > 16):
            newCode[16] = '-'
        if (len(newCode) > 20):
            newCode[20] = '-'
        if (len(newCode) > 25):
            newCode[25] = '-'
        return (newCode)

    print " ERROR in fixCode ??? ", aCode
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findCode(codeVec, zCode):

    aCode = codeVec[0]

    ## print " in findCode: ", len(aCode), len(zCode), aCode, zCode

    if (not aCode.upper().startswith("TCGA")):
        print " (a) ERROR in findCode ... ", aCode
        sys.exit(-1)

    if (not zCode.upper().startswith("TCGA")):
        print " (z) ERROR in findCode ... ", zCode
        sys.exit(-1)

    aSep = aCode[4]
    zSep = zCode[4]
    if (zSep != aSep):
        newCode = ''
        for ii in range(len(zCode)):
            if (zCode[ii] != zSep):
                newCode += zCode[ii]
            else:
                newCode += aSep
        ## print " %s --> %s " % ( zCode, newCode )
        zCode = newCode

    ##print aCode, codeVec[:5], zCode

    for ii in range(len(codeVec)):
        ## print ii, codeVec[ii], zCode
        if (codeVec[ii].lower() == zCode.lower()):
            ## print " returning %d " % ii
            return (ii)
        if (len(zCode) < len(codeVec[ii])):
            if (codeVec[ii][:len(zCode)].lower() == zCode.lower()):
                ## print " returning %d " % ii
                return (ii)

    # print " returning from findCode ... did NOT find %s " % zCode
    # print codeVec
    # print " "
    # print " "

    return (-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def alreadyThere ( bKey, aDict ):

    bKey2 = "XX"
    aKey2 = "YY"

    ## print "     in alreadyThere ... <%s> " % bKey

    aList = aDict.keys()
    for aKey in aList:

        ## print "         comparing to <%s> " % aKey

        ## print "             <%s> <%s> " % ( bKey, aKey )
        if ( bKey.lower() == aKey.lower() ):
            ## print " --> found match ", bKey, aKey
            return  ( aKey )

        if ( bKey[1] == ":" ):
            bTokens = bKey.split(':')
            if ( len(bTokens) == 8 ):
                bKey2 = bTokens[2] + ":" + bTokens[7]
                if ( bKey2[-1] == ":" ): bKey2 = bKey2[:-1]
            elif ( len(bTokens) > 2 ):
                bKey2 = bTokens[2]
            else:
                print " ERROR in alreadyThere ??? ", bKey
                print aDict
                sys.exit(-1)
            ## print "             <%s> <%s> " % ( bKey2, aKey )
            if ( bKey2.lower() == aKey.lower() ):
                ## print " --> found match ", bKey2, aKey
                return ( aKey )

        if ( aKey[1] == ":" ):
            aTokens = aKey.split(':')
            if ( len(aTokens) == 8 ):
                aKey2 = aTokens[2] + ":" + aTokens[7]
                if ( aKey2[-1] == ":" ): aKey2 = aKey2[:-1]
            elif ( len(aTokens) > 2 ):
                aKey2 = aTokens[2]
            else:
                print " ERROR in alreadyThere ??? ", bKey
                print aDict
                sys.exit(-1)
            ## print "             <%s> <%s> " % ( bKey, aKey2 )
            if ( bKey.lower() == aKey2.lower() ):
                ## print " --> found match ", bKey, aKey2
                return ( aKey )
            ## print "             <%s> <%s> " % ( bKey2, aKey2 )
            if ( bKey2.lower() == aKey2.lower() ):
                ## print " --> found match ", bKey2, aKey2
                return ( aKey )

    print " --> no match found in alreadyThere() "
    return ( "" )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def mergeClinDict(aDict, bDict):

    print " "
    print " "
    print " in mergeClinDict ... "
    ## print "     aDict : ", aDict.keys()
    ## print "     bDict : ", bDict.keys()
    print " "

    # we assume that one input file uses the xml bcr_patient_barcode

    testKeys = [ "bcr_patient_barcode", "C:CLIN:bcr_patient_barcode:::::" ]
    aKey = "NO KEY"
    for tKey in testKeys:
        if ( tKey in aDict.keys() ):
            aKey = tKey

    if ( aKey == "NO KEY" ):
        print ' ERROR ??? %s not in keys ??? ' % aKey
        print aDict.keys()
        sys.exit(-1)

    aLen = len(aDict[aKey][0])
    print " aKey, aLen : ", aKey, aLen

    numSamples = len(aDict[aKey])

    # but for the other one, we need to figure out which column has the
    # barcode id ...
    print " need to figure out where the bcr_patient_barcode column is ... "
    keepKey = "NA"
    keepLen = 0
    for bKey in bDict.keys():
        isBarcode = 1
        print bKey, bDict[bKey][0]
        # loop over all the entries for this key and see if they
        # all start with TCGA ...
        for ii in range(len(bDict[bKey])):
            try:
                if (bDict[bKey][ii].upper().startswith("TCGA")):
                    bLen = len(bDict[bKey][ii])
                else:
                    isBarcode = 0
            except:
                isBarcode = 0
        # if this is a barcode key, then keep it and the length
        if (isBarcode):
            if (keepKey.upper() == "NA"):
                keepKey = bKey
                keepLen = bLen
            if (keepLen > bLen):
                keepKey = bKey
                keepLen = bLen
            if (bLen == aLen):
                keepKey = bKey
                keepLen = bLen

    print " sample ID key from input file #2 : ", keepKey, keepLen

    if (aLen != keepLen):

        # as long as keepLen > aLen, we're ok, we will just need to
        # shorten the new barcodes

        # 1234567890123456789012345678
        # TCGA-AL-3468-01A-01R-1193-07

        print " barcode lengths differ ... ", aLen, keepLen
        if (keepLen not in [12, 15, 16, 20, 27, 28]):
            print " ERROR ??? non-standard barcode length ??? "
            print bKey, bDict[bKey][0]
            print bDict[keepKey][0], bDict[keepKey][-1]
            print " BAILING !!! "
            print " "
            print " "
            sys.exit(-1)

        if (keepLen < aLen):
            print " --> this may be a problem ... "
            ## if either keepLen and/or aLen are less than 16,
            ## then we want to lengthen them both ...
            if ( keepLen < 16 ):
                print "     --> changing barcodes in bDict to length 16 ... "
                for ii in range(len(bDict[keepKey])):
                    bDict[keepKey][ii] = miscTCGA.get_barcode16 ( bDict[keepKey][ii] )
                print "         OK done "
                keepLen = 16
            if ( aLen < 16 ):
                print "     --> changing barcodes in aDict to length 16 ... "
                for ii in range(len(aDict[aKey])):
                    aDict[aKey][ii] = miscTCGA.get_barcode16 ( aDict[aKey][ii] )
                print "         OK done "
                aLen = 16

    if ( keepLen > aLen ):
        print " --> abbreviating longer barcodes in bDict ... "
        for ii in range(len(bDict[keepKey])):
            # print bDict[keepKey][ii]
            bDict[keepKey][ii] = bDict[keepKey][ii][:aLen]
            # print bDict[keepKey][ii]

    existingKeys = {}

    # first we add in the new fields to the aDict ...
    print " adding new features from bDict to aDict ... "
    for bKey in bDict.keys():
        print "     bKey = <%s> " % bKey
        if (bKey.lower() == keepKey.lower()):
            continue

        taKey = alreadyThere ( bKey, aDict )
        if ( len(taKey) > 1 ):
            print " WARNING !!! ??? new key <%s> is already in original data as <%s> ??? " % ( bKey, taKey )
            existingKeys[bKey] = taKey
            # sys.exit(-1)
        else:
            print " adding new key <%s> (initially all NAs) " % bKey
            aDict[bKey] = ["NA"] * numSamples

    print " "
    print " "

    # if there are any missing samples in the aDict for which we
    # have information in the bDict, then we want to add them in ...
    print " checking for barcode IDs from bDict in aDict ... ", len(aDict[aKey]), len(bDict[keepKey])
    # print aKey, aDict[aKey]
    # print keepKey, bDict[keepKey]
    for ii in range(len(bDict[keepKey])):
        bCode = bDict[keepKey][ii]
        # print ii, bCode
        jj = findCode(aDict[aKey], bCode)
        # print jj
        if (jj < 0):
            aDict[aKey] += [fixCode(bCode)]
            print " adding barcode <%s> " % (bCode)
            for oKey in aDict.keys():
                if (oKey.lower() == aKey.lower()):
                    continue
                aDict[oKey] += ["NA"]
        else:
            # print " found <%s> at %4d " % ( bCode, jj )
            doNothing = 1

    print "     --> length of code vectors now : ", len(aDict[aKey]), len(bDict[keepKey])

    print " *** existingKeys *** "
    print existingKeys
    print " ******************** "

    # and now we put all the information from bDict that we can into aDict
    allBkeys = bDict.keys()
    allBkeys.sort()
    notFoundCodes = []
    for bKey in allBkeys:
        if (bKey.lower() == keepKey.lower()):
            continue
        print "         --> merging new column ", aKey, bKey, keepKey
        if ( bKey in existingKeys.keys() ):
            taKey = existingKeys[bKey]
            print "         got taKey from existingKeys : ", taKey
        else:
            taKey = bKey
            print "         defaulting taKey to : ", taKey

        if ( 0 ):
            print " making sure we have some values in bDict ... ", bKey
            print bDict[bKey][0:5]
            print " making sure we have some values in aDict ... ", taKey
            print aDict[taKey][0:5]

        for ii in range(len(bDict[keepKey])):
            bCode = bDict[keepKey][ii]
            jj = findCode(aDict[aKey], bCode)
            print ii, bCode, jj
            if (jj >= 0):
                try:
                    aDict[taKey][jj] = bDict[bKey][ii]
                    ## print " setting aDict[%s][%d] = bDict[%s][%d] = " % ( taKey, jj, bKey, ii ), bDict[bKey][ii]
                except:
                    print " this did not work ", ii, jj, taKey, bKey
                    print len(bDict[bKey]), bDict[bKey]
                    print len(aDict[taKey]), aDict[taKey]
                    print aDict[taKey][jj]
                    print bDict[bKey][ii]
                    sys.exit(-1)
            else:
                if (bCode not in notFoundCodes):
                    notFoundCodes += [bCode]

    print " "
    if (len(notFoundCodes) > 0):
        notFoundCodes.sort()
        print " list of %d not-found codes : " % len(notFoundCodes)
        print notFoundCodes
        sys.exit(-1)
    # else:
    # print " ALL codes in the new dataset existed in the initial set! "
    print " "

    return (aDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 4):
        print " Usage : %s <old input TSV> <new input TSV> <output merged TSV> " % sys.argv[0]
        print "         ", sys.argv
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    tsvName1 = sys.argv[1]
    tsvName2 = sys.argv[2]
    tsvName3 = sys.argv[3]

    # test out readTSV ...
    ## tsvName = "coad_read_clinical.27jan.tsv"
    print " "
    print " ****************************************************************** "
    print " IN add2clinTSV.py ... "
    print " reading input file <%s> " % tsvName1
    allClinDict = tsvIO.readTSV(tsvName1)

    # take a look ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)
    bestKeyOrder = miscClin.getBestKeyOrder(allClinDict, naCounts)

    # now we want to read in a new tsv file ...
    print " "
    print " ****************************************************************** "
    print " reading input file <%s> " % tsvName2
    tmpDict = tsvIO.readTSV(tsvName2)

    # check to make sure that we actually got something back ...
    if (len(tmpDict) == 0):
        print " WARNING ... no information found ... "

    else:

        tmpDict = miscClin.check_barcodes(tmpDict)
        (newNfCounts, newOtherCounts) = miscClin.lookAtClinDict(tmpDict)
        # now we merge these two dictionaries ...
        allClinDict = mergeClinDict(allClinDict, tmpDict)

        if (0):
            # remove constant-value keys ...
            allClinDict = miscClin.removeConstantKeys(allClinDict)

        # look at the data again and re-pick the 'best' key order ...
        (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)
        bestKeyOrder = miscClin.getBestKeyOrder(allClinDict, naCounts)

    doWriteTSV = 1
    if (doWriteTSV):
        outName = tsvName3
        tsvIO.writeTSV_clinical(allClinDict, bestKeyOrder, outName)

    doWriteARFF = 0
    if (doWriteARFF):
        outName = "testing"
        arffIO.writeARFF(allClinDict, bestKeyOrder, sys.argv[0], outName)

    print " DONE with add2clinTSV.py "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
