#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import arffIO
import miscClin
import tsvIO

import sys

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#	TCGA-AG-A02G-01A-01D-A008-01
#	          111111111122222222
#	0123456789012345678901234567

def fixCode ( aCode ):

    newCode = aCode.lower()
    if ( newCode.startswith("tcga") ):
        sepChr = newCode[4]
	if ( sepChr == '-' ): return ( newCode )
	newCode[4] = '-'
	newCode[7] = '-'
	if ( len(newCode) > 12 ): newCode[12] = '-'
	if ( len(newCode) > 16 ): newCode[16] = '-'
	if ( len(newCode) > 20 ): newCode[20] = '-'
	if ( len(newCode) > 25 ): newCode[25] = '-'
	return ( newCode )

    print " ERROR in fixCode ??? ", aCode
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findCode ( codeVec, zCode ):

    aCode = codeVec[0].upper()

    ## print " in findCode: ", len(aCode), len(zCode)

    if ( not aCode.startswith("TCGA")  and  not aCode.startswith("tcga") ):
        print " (a) ERROR in findCode ... ", aCode
	sys.exit(-1)

    if ( not zCode.startswith("TCGA")  and  not zCode.startswith("tcga") ):
        print " (z) ERROR in findCode ... ", zCode
	sys.exit(-1)

    aSep = aCode[4]
    zSep = zCode[4]
    if ( zSep != aSep ):
        newCode = ''
	for ii in range(len(zCode)):
	    if ( zCode[ii] != zSep ):
	        newCode += zCode[ii]
	    else:
	        newCode += aSep
	## print " %s --> %s " % ( zCode, newCode )
	zCode = newCode

    for ii in range(len(codeVec)):
        if ( codeVec[ii] == zCode ): return ( ii )
	if ( len(zCode) < len(codeVec[ii]) ):
	    if ( codeVec[ii][:len(zCode)] == zCode ): return ( ii )

    print " returning from findCode ... did NOT find %s ", zCode
    ## print codeVec
    ## print " "
    ## print " "

    return ( -1 )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def mergeClinDict ( aDict, bDict ):

    print " "
    print " "
    print " in mergeClinDict ... "
    print " "

    ## we assume that one input file uses the xml bcr_patient_barcode
    aKey = 'bcr_patient_barcode'
    if ( aKey not in aDict.keys() ):
	print ' ERROR ??? %s not in keys ??? ' % aKey
	print aDict.keys()
	sys.exit(-1)
    aLen = len(aDict[aKey][0])
    print " aKey, aLen : ", aKey, aLen

    numSamples = len(aDict[aKey])

    ## but for the other one, we need to figure out which column has the 
    ## barcode id ...
    keepKey = "NA"
    keepLen = 0
    for bKey in bDict.keys():
        isBarcode = 1
	print bKey, bDict[bKey][0]
	## loop over all the entries for this key and see if they
	## all starts with TCGA ...
	for ii in range(len(bDict[bKey])):
	    try:
	        if ( bDict[bKey][ii].startswith("TCGA") ):
		    bLen = len(bDict[bKey][ii] )
		elif ( bDict[bKey][ii].startswith("tcga") ):
		    bLen = len(bDict[bKey][ii] )
		else:
		    isBarcode = 0
	    except:
	        isBarcode = 0
	## if this is a barcode key, then keep it and the length
	if ( isBarcode ):
	    if ( keepKey == "NA" ):
	        keepKey = bKey
	        keepLen = bLen
	    if ( keepLen > bLen ):
	        keepKey = bKey
	        keepLen = bLen
	    if ( bLen == aLen ):
	        keepKey = bKey
	        keepLen = bLen
	    
    print " sample ID key from input file #2 : ", keepKey, keepLen

    if ( aLen != keepLen ):

        ## as long as keepLen > aLen, we're ok, we will just need to 
	## shorten the new barcodes

	## 1234567890123456789012345678
	## TCGA-AL-3468-01A-01R-1193-07

        print " barcode lengths differ ... ", aLen, keepLen
	if ( keepLen not in [12, 15, 16, 20, 27, 28] ):
	    print " ERROR ??? non-standard barcode length ??? "
	    print bKey, bDict[bKey][0]
	    print bDict[keepKey][0], bDict[keepKey][-1]
	    print " BAILING !!! "
	    print " "
	    print " "
	    sys.exit(-1)
	if ( keepLen < aLen ):
	    print " --> this may be a problem ... "
	    print "     YES, I THINK THIS HAS TO BE FIXED "
	    sys.exit(-1)
	print " --> abbreviating longer set of barcodes ... "
	for ii in range(len(bDict[keepKey])):
	    ## print bDict[keepKey][ii]
	    bDict[keepKey][ii] = bDict[keepKey][ii][:aLen]
	    ## print bDict[keepKey][ii]


    ## first we add in the new fields to the aDict ...
    print " adding new features from bDict to aDict ... "
    for bKey in bDict.keys():
        if ( bKey == keepKey ): continue
	if ( bKey in aDict.keys() ):
	    print " WARNING !!! ??? new key <%s> is already in original data ??? " % bKey
	    ## sys.exit(-1)
	else:
	    print " adding new key <%s> " % bKey
	    aDict[bKey] = ["NA"] * numSamples

    ## if there are any missing samples in the aDict for which we
    ## have information in the bDict, then we want to add them in ...
    print " checking for barcode IDs from bDict in aDict ... ", len(aDict[aKey]), len(bDict[keepKey])
    for ii in range(len(bDict[keepKey])):
        bCode = bDict[keepKey][ii]
	jj = findCode ( aDict[aKey], bCode )
	if ( jj < 0 ):
	    aDict[aKey] += [ fixCode(bCode) ]
	    print " adding barcode <%s> " % ( bCode )
	    for oKey in aDict.keys():
	        if ( oKey == aKey ): continue
		aDict[oKey] += [ "NA" ]
	else:
	    ## print " found <%s> at %4d " % ( bCode, jj )
            doNothing = 1

    print "     --> length of code vectors now : ", len(aDict[aKey]), len(bDict[keepKey])

    ## and now we put all the information from bDict that we can into aDict
    allBkeys = bDict.keys()
    allBkeys.sort()
    notFoundCodes = []
    for bKey in allBkeys:
        if ( bKey == keepKey ): continue
	print "         --> merging new column ", bKey
        for ii in range(len(bDict[keepKey])):
	    bCode = bDict[keepKey][ii]
	    jj = findCode ( aDict[aKey], bCode )
	    if ( jj >= 0 ):
	        aDict[bKey][jj] = bDict[bKey][ii]
	    else:
	        if ( bCode not in notFoundCodes ):
		    notFoundCodes += [ bCode ]

    print " "
    if ( len(notFoundCodes) > 0 ):
        notFoundCodes.sort()
        print " list of %d not-found codes : " % len(notFoundCodes)
	print notFoundCodes
	sys.exit(-1)
    ## else:
    ##    print " ALL codes in the new dataset existed in the initial set! "
    print " "

    return ( aDict )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if ( len(sys.argv) != 4 ):
        print " Usage : %s <old input TSV> <new input TSV> <output merged TSV> " % sys.argv[0]
	print "         ", sys.argv
	sys.exit(-1)

    tsvName1 = sys.argv[1]
    tsvName2 = sys.argv[2]
    tsvName3 = sys.argv[3]

    ## test out readTSV ...
    ## tsvName = "coad_read_clinical.27jan.tsv"
    print " "
    print " ****************************************************************** "
    print " IN add2clinTSV.py ... "
    print " reading input file <%s> " % tsvName1
    allClinDict = tsvIO.readTSV ( tsvName1 )

    ## take a look ...
    ( naCounts, otherCounts ) = miscClin.lookAtClinDict ( allClinDict )
    bestKeyOrder = miscClin.getBestKeyOrder ( allClinDict, naCounts )

    ## now we want to read in a new tsv file ...
    ## newInfo = "/users/sreynold/TCGA/COAD+READ/tcga_crc_cluster_info_12272010_b.tsv"
    ## tsvName2 = "/users/sreynold/TCGA/COAD+READ/crc_dna_methylation_cluster_01-20-11_b.tsv"
    print " "
    print " ****************************************************************** "
    print " reading input file <%s> " % tsvName2
    tmpDict = tsvIO.readTSV ( tsvName2 )

    ## check to make sure that we actually got something back ...
    if ( len(tmpDict) == 0 ):
        print " WARNING ... no information found ... "

    else:

        tmpDict = miscClin.check_barcodes ( tmpDict )
        ( newNfCounts, newOtherCounts ) = miscClin.lookAtClinDict ( tmpDict )
        ## now we merge these two dictionaries ...
        allClinDict = mergeClinDict ( allClinDict, tmpDict )

        if ( 0 ):
            ## remove constant-value keys ...
            allClinDict = miscClin.removeConstantKeys ( allClinDict )

        ## look at the data again and re-pick the 'best' key order ...
        ( naCounts, otherCounts ) = miscClin.lookAtClinDict ( allClinDict )
        bestKeyOrder = miscClin.getBestKeyOrder ( allClinDict, naCounts )

    doWriteTSV = 1
    if ( doWriteTSV ):
        outName = tsvName3
        tsvIO.writeTSV_clinical ( allClinDict, bestKeyOrder, outName )

    doWriteARFF = 0
    if ( doWriteARFF ):
        outName = "testing"
        arffIO.writeARFF ( allClinDict, bestKeyOrder, sys.argv[0], outName )

    print " DONE with add2clinTSV.py "

    
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
