#!/usr/bin/env python

__author__ = 'sreynolds'

## if this is set to 1 there will be a TON of debug output ...
debugFlag = 0

import argparse
import commands
import json
import math
import random
import sys
import time

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def cleanUpName ( aName ):

    bName = ''

    aName = aName.upper()

    ## ii = aName.find(" - Homo sapiens (human)")
    ii = aName.find(" - HOMO SAPIENS (HUMAN)")
    if ( ii >= 0 ):
        aName = aName[:ii]
    aName = aName.strip()

    ii = aName.find("(")
    while ( ii >= 0 ):
        jj = aName.find(")",ii)
	aName = aName[:ii] + aName[jj+1:]
 	ii = aName.find("(")
    aName = aName.strip()

    ii = aName.find("<")
    while ( ii >= 0 ):
        jj = aName.find(">",ii)
	aName = aName[:ii] + aName[jj+1:]
 	ii = aName.find("<")
    aName = aName.strip()

    for ii in range(len(aName)):
        if ( aName[ii] == ',' ):
	    continue
	elif ( aName[ii] == '(' ):
	    bName += '_'
	elif ( aName[ii] == ')' ):
	    bName += '_'
	elif ( aName[ii] == '-' ):
	    bName += '_'
	elif ( aName[ii] == '/' ):
	    bName += '_'
	elif ( aName[ii] == ';' ):
	    bName += '_'
	elif ( aName[ii] == '&' ):
	    continue
	elif ( aName[ii] == '#' ):
	    continue
	elif ( aName[ii] == ' ' ):
	    bName += '_'
	else:
	    bName += aName[ii].upper()

    ii = bName.find("__")
    while ( ii >= 0 ):
	## print "             ", ii, bName
        bName = bName[:ii] + bName[ii+1:]
	## print "             ", bName
	ii = bName.find("__")

    return ( bName )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def readPathways ( pathwaysFilename ):

    if ( debugFlag ):
        print " in readPathways ... <%s> " % pathwaysFilename

    fh = file ( pathwaysFilename, 'r' )

    pwDict = {}

    for aLine in fh:
	aLine = aLine.strip()
	aLine = aLine.upper()
	tokenList = aLine.split('\t')
	if ( len(tokenList) != 3 ): continue
	if ( tokenList[0] == "pathway" ): continue

	longPathwayName = tokenList[0]
	shortPathwayName = tokenList[1]

	geneTokens = tokenList[2].strip()
	geneList = geneTokens.split(',')
	geneList.sort()

	if ( len(geneList) > 0 ):
	    while ( geneList[0] == '' ):
	        geneList = geneList[1:]
		if ( len(geneList) == 0 ): continue

	if ( len(geneList) == 0 ): continue

	pathwayName = cleanUpName ( shortPathwayName )

	pathwayName = pathwayName + "__" + "%d" % len(geneList)

	if ( pathwayName not in pwDict.keys() ):
	    ## print " adding pathway %s (%d) " % ( pathwayName, len(geneList) )
	    pwDict[pathwayName] = geneList
	else:
	    if ( len(pwDict[pathwayName]) < len(geneList) ):
		## print " substituting shorter list of genes for %s (%d) " % ( pathwayName, len(geneList) )
	        pwDict[pathwayName] = geneList
	    ## else:
		## print " NOT substituing list for %s " % pathwayName

    fh.close()

    print "## "
    print "## have pathway dictionary with %d pathways " % len(pwDict)
    ## print "     --> now looking for duplicate pathways ... "
    pwList = pwDict.keys()
    pwList.sort()
    delList = []
    pairDict = {}

    for ii in range(len(pwList)-1):
	iiName = pwList[ii]
	iiLen = len(pwDict[iiName])
	for jj in range(ii+1,len(pwList)):
	    jjName = pwList[jj]
	    jjLen = len(pwDict[jjName])
	    if ( jjLen != iiLen ): continue

	    if ( pwDict[iiName] == pwDict[jjName] ):
		if ( debugFlag ): 
		    print "\n\n SAME !!! "
		    print iiName, iiLen
		    print pwDict[iiName]
		    print jjName, jjLen
		    print pwDict[jjName]

		iiSplit = iiName.split('__')
		jjSplit = jjName.split('__')

		if ( iiSplit[1] <= jjSplit[1] ):
		    pairNames = ( iiSplit[1], jjSplit[1] )
		else:
		    pairNames = ( jjSplit[1], iiSplit[1] )
		if ( pairNames in pairDict.keys() ):
		    pairDict[pairNames] += 1
		else:
		    pairDict[pairNames] = 1

		if ( iiSplit[1] == jjSplit[1] ):
		    if ( len(iiName) <= len(jjName) ):
			delList += [ jjName ]
		    else:
			delList += [ iiName ]

		else:

		    if ( iiSplit[1] == "NCI-NATURE" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "NCI-NATURE" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "PID" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "PID" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "KEGG" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "KEGG" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "PWCOMMONS" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "PWCOMMONS" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "REACTOME" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "REACTOME" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "WIKIPATHWAYS" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "WIKIPATHWAYS" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "WIKIPW" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "WIKIPW" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "SMPDB" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "SMPDB" ):
		        delList += [ iiName ]

		    elif ( iiSplit[1] == "HUMANCYC" ):
		        delList += [ jjName ]
		    elif ( jjSplit[1] == "HUMANCYC" ):
		        delList += [ iiName ]

		    else:
		        sys.exit(-1)
	    
    for aName in delList:
	try:
            del pwDict[aName]
	except:
	    doNothing = 1


    print "## "
    print "## returning pathway dictionary with %d pathways " % len(pwDict)
    print "## "
    if ( debugFlag ):
        for aKey in pairDict.keys():
            print aKey, pairDict[aKey]
        print " "
        print " "

    return ( pwDict )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def addRandomPathways ( pwDict, numRandFactor ):

    numRand = numRandFactor * len(pwDict)
    ( randDict, minLen, maxLen ) = makeRandomPathways ( pwDict, numRand )
    print "##     --> adding %d random pathways to original set of %d pathways " % ( len(randDict), len(pwDict ) )
    if ( 1 ):
        print "##         using current system time to set seed "
	random.seed()

    for aKey in randDict.keys():
	pwDict[aKey] = randDict[aKey]

    print "##     --> returning pathway dictionary with %d pathways " % len(pwDict)

    return ( pwDict, minLen, maxLen )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def pickRandom ( aList ):

    ii = random.randint ( 0, len(aList)-1 )
    return ( aList[ii] )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makeRandomPathways ( pwDict, numRand ):

    pwLenList = []
    pwGeneList = []
    randDict = {}

    ## create a non-unique gene list ... meaning that if a gene appears many
    ## times in different pathways, then it will appear many times in this
    ## list and will get selected many times to create random pathways
    ## geneListFlag = 'unique'
    geneListFlag = 'NOT-unique'

    print "## in makeRandomPathways ... ", len(pwDict), numRand, geneListFlag

    for aPw in pwDict.keys():
        for aGene in pwDict[aPw]:
	    if ( geneListFlag == 'unique' ):
	        if ( aGene not in pwGeneList ):
	            pwGeneList += [ aGene ]
	    elif ( geneListFlag == 'NOT-unique' ):
	        pwGeneList += [ aGene ]
	    else:
		print "## ERROR ??? invalid geneListFlag ", geneListFlag
		sys.exit(-1)
	curLen = len(pwDict[aPw])

	if ( 0 ):
	    pwLenList += [ curLen ]
	else:
	    ## or maybe we should only do unique pathway sizes so that we get
	    ## a better distribution for both common and uncommon pathway sizes?
	    if ( curLen not in pwLenList ):
	        pwLenList += [ curLen ]

    pwLenList.sort()

    print "##        len(pwGeneList) = %d " % len(pwGeneList)
    print "##        len(pwLenList)  = %d " % len(pwLenList), min(pwLenList), max(pwLenList)
    print "##        ", pwLenList

    jRand = 0
    for iRand in range(numRand):

        ## work through the length options methodically ...
	curLen = pwLenList[jRand]
	jRand += 1
	if ( jRand == len(pwLenList) ): jRand = 0

	curList = []
	while ( len(curList) < curLen ):
	    aGene = pickRandom ( pwGeneList )
	    if ( aGene not in curList ):
	        curList += [ aGene ]
	curName = "RANDOM_PATHWAY_%d__%d" % ( (iRand+1), curLen )
	randDict[curName] = curList
	## print curName, curList

    minLen = min(pwLenList)
    maxLen = max(pwLenList)

    return ( randDict, minLen, maxLen )
    

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getPairwisePvalues ( pwpvFilename, pwGeneList, featureName, geneDataType,
                         maxDist, corrSign, minLogP ):

    pwpvData = {}

    fh = file ( pwpvFilename )

    firstCheck = 1

    if ( debugFlag ): print " ... working our way through <%s> ... " % pwpvFilename
    numLines = 0
    for aLine in fh:

	numLines += 1
	if ( numLines%10000000 == 0 ):
	    print "##             ", numLines, len(pwpvData)

	if ( aLine.find(geneDataType) < 0 ): continue

        tokenList = aLine.split('\t')
        ## print tokenList
	if ( len(tokenList) < 12 ): continue

	## if a minimum distance has been set, then check that ...
	abDist = -1
	if ( maxDist >= 0 ):
	    try:
	        abDist = int ( tokenList[11] )
	        if ( abDist > maxDist ): continue
	    except:
	        print "## HUH ??? failed to get distance ??? "
	        print "##    ", tokenList
	        sys.exit(-1)

	## grab the two feature names
	try:
	    aLabel = tokenList[0]
	    bLabel = tokenList[1]
	except:
	    print "## HUH ??? failed to get two feature names ??? "
	    print "##    ", tokenList
	    sys.exit(-1)

	skipFlag = 1

	aMatch = ( aLabel == featureName )
	bMatch = ( bLabel == featureName )

	if ( aMatch ):
	    if ( bLabel.startswith(geneDataType) ):
	        bTokens = bLabel.split(':')
		bGene = bTokens[2]
		if ( bGene in pwGeneList ):
		    skipFlag = 0
		    aKey = bGene

	elif ( bMatch ):
	    if ( aLabel.startswith(geneDataType) ):
	        aTokens = aLabel.split(':')
		aGene = aTokens[2]
		if ( aGene in pwGeneList ):
		    skipFlag = 0
		    aKey = aGene

	if ( skipFlag ): continue

	pValue = float ( tokenList[4] )
	if ( abDist < 0 ): abDist = int ( tokenList[11] )

        ## moved this again ... 13dec13
        ## if the correlation sign does not match the ones we have been
        ## told to look for, then the pValue gets forced to ZERO
        ## (ie completely insignificant)
        try:
	    corrVal = float ( tokenList[2] )
        except:
            corrVal = "NA"

	if ( corrSign != "" ):
	    if ( tokenList[2] != "NA" ):
	        if ( corrSign == '+' ):
		    if ( corrVal < 0. ):
                        pValue = 0.
                        corrVal = 0.
		elif ( corrSign == '-' ):
		    if ( corrVal > 0. ): 
                        pValue = 0.
                        corrVal = 0.
            else:
                if ( firstCheck ):
                    print " WARNING !!! correlation sign not known ... careful interpreting results ", tokenList
                    firstCheck = 0

	try:
	    ( oldP, oldDist ) = pwpvData[aKey]
	    if ( oldP < pValue ):
	        pwpvData[aKey] = ( pValue, corrVal, abDist )
	except:
	    pwpvData[aKey] = ( pValue, corrVal, abDist )

    fh.close()

    ## filter out the lower p-values (optional)
    if ( minLogP > 0 ):
        pwpvData = filterLowP ( pwpvData, minLogP )

    print "## returning from getPairwisePvalues ... ", numLines, len(pwpvData)

    if ( debugFlag ): print "     --> DONE ... have p-values for %d pairs " % len(pwpvData)
    return ( pwpvData )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findTopGenes ( pwpvData, nTop ):

    print "## "
    print "## "

    allKeys = pwpvData.keys()
    numKeys = len(allKeys)
    if ( numKeys < nTop ):
        nTop2 = numKeys
    else:
        nTop2 = nTop

    pList = []
    for aKey in allKeys:
        pList += [ pwpvData[aKey][0] ]

    pList.sort(reverse=True)
    pThresh = pList[nTop2-1]
    print "##         range of p-values: %.1f to %.1f " % ( pList[-1], pList[0] )

    if ( 0 ):
        for ii in range(len(pList)):
            print "##             pList.sort \t %4d \t %5.1f " % ( ii, pList[ii] )

    print "##         p-value threshold for top %d genes is %.1f " % ( nTop2, pThresh )

    topGenes = []
    topPs = []
    for aKey in allKeys:
	if ( pwpvData[aKey][0] >= pThresh ):
	    topGenes += [ aKey ]
	    curP = pwpvData[aKey][0]
	    topPs += [ curP ]

    print "##         top-scoring genes (not sorted) : "

    for ii in range(nTop2):
	try:
            print "##             %16s %6.1f " % ( topGenes[ii], topPs[ii] )
	except:
	    doNothing = 1
    
    print "## "
    print "## "

    return ( topGenes )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def pwMembership ( pwDict, topGenes ):

    print "## "
    print "## in pwMembership ... "
    print "## topGenes list : ", topGenes
    print "## "

    oLapDict = {}
    maxO = 0
    for aPW in pwDict.keys():
	if ( aPW.startswith("RANDOM_PATHWAY") ): continue
        numO = 0
	for aGene in topGenes:
	    if ( aGene in pwDict[aPW] ):
	        numO += 1
	if ( numO > 1 ):
	    if ( numO in oLapDict.keys() ):
	        oLapDict[numO] += [ aPW ]
	    else:
	        oLapDict[numO] = [ aPW ]
	if ( maxO < numO ):
	    maxO = numO

    print "## "
    print "## pathway membership of the top-scoring genes : "
    for ii in range(maxO,0,-1):
	if ( ii in oLapDict.keys() ):
	    if ( len(oLapDict[ii]) > 0 ):
                print "## %3d " % ii, oLapDict[ii]
    print "## "

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def pwMembership2 ( pwDict, pwpvData ):

    allKeys = pwpvData.keys()
    numKeys = len(allKeys)

    for aPW in pwDict.keys():
        if ( aPW.startswith("RANDOM_PATHWAY") ): continue

        numO = 0
        oLapDict = {}
        for aGene in allKeys:
            ## print aGene, pwpvData[aGene]
            if ( aGene in pwDict[aPW] ):
                numO += 1
                pVal = pwpvData[aGene][0]
                rhoV = pwpvData[aGene][1]
                if ( pVal in oLapDict.keys() ):
                    oLapDict[pVal] += [ ( aGene, rhoV ) ]
                else:
                    oLapDict[pVal] = [ ( aGene, rhoV ) ]

        if ( len(oLapDict) > 0 ):
            oLapKeys = oLapDict.keys()
            oLapKeys.sort(reverse=True)
            outLine = "## pwMembership2: %3d %s (%d) " % ( numO, aPW, len(oLapKeys) )
            ## print len(oLapKeys), oLapKeys[0], oLapDict[oLapKeys[0]]
            for aKey in oLapKeys:
                for aTuple in oLapDict[aKey]:
                    aGene = aTuple[0]
                    rhoV = aTuple[1]
                    try:
                        outLine += " (%s, %.1f, %.1f) " % ( aGene, rhoV, aKey )
                    except:
                        if ( rhoV == "NA" ):
                            outLine += " (%s, NA, %.1f) " % ( aGene, aKey )
                        else:
                            print " ERROR adding to outLine ??? ", aGene, rhoV, aKey
            print outLine


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
## pwpvData has keys like ('sampleType', 'TP53BP1') 
##          and values like (7.5, 500000000)
## where the first value is the -log(p) and the second is the genomic distance

def filterLowP ( pwpvData, minLogP ):

    print "##         in filterLowP : ", len(pwpvData), minLogP

    newD = {}
    for aKey in pwpvData.keys():
	if ( pwpvData[aKey][0] >= minLogP ):
	    newD[aKey] = pwpvData[aKey]

    print "##         after filtering : ", len(newD)

    return ( newD )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getInfoFromTSV ( tsvFilename, featureName ):

    ## we start by opening and reading the entire input feature matrix 
    print "## "
    print "## opening input TSV file <%s> " % tsvFilename
    print "## "
    fh = file ( tsvFilename )
    wholeFile = fh.read()
    fh.close()

    print "##     --> data file size : %d " % len(wholeFile)
    print "## (b) TIME ", time.asctime(time.localtime(time.time()))

    ## then we split the file into lines
    allLines = wholeFile.split("\n")
    numLines = len(allLines)

    ## extract the row labels from lines 2 thru end ... 
    ## a) build geneList
    ## b) make sure that the specified featureName(s) exists
    tsvGeneList = []
    featureIndex = -1
    nFound = 0

    ## keep track of the first few names that match ...
    maxNames = 20
    namesFound = [0] * maxNames

    for ii in range(1,len(allLines)):
        aLine = allLines[ii].strip()
	lineTokens = aLine.split("\t")
	labelTokens = lineTokens[0].split(":")

	if ( aLine.startswith(geneDataType) ):
	    geneSymbol = labelTokens[2]
	    if ( geneSymbol != '' ):
	        tsvGeneList += [ geneSymbol ]

        if ( 1 ):
            curName = featureName
            if ( lineTokens[0] == curName ):
	        if ( featureIndex < 0 ):
	            featureIndex = ii - 1
	        nFound += 1
		if ( nFound <= maxNames ):
		    namesFound[nFound-1] = lineTokens[0]

    print "##     --> length of gene list : %d " % len(tsvGeneList)
    print "##"

    ## if we only found one feature that matched the prefix specified in
    ## the feature name list, then replace it with the complete feature name
    if ( 1 ):
        if ( nFound == 1 ):
	    aLine = allLines[featureIndex+1].strip()
	    lineTokens = aLine.split("\t")
            print "##     --> unique feature <%s> found at index %d :  %s " % \
	    	( featureName, featureIndex, lineTokens[0] )
	    featureName = lineTokens[0]
        elif ( nFound > 1 ):
            print " FATAL ERROR ... NOT ALLOWED ... "
            sys.exit(-1)
	    print "##     --> found %d features with <%s> " % ( nFound, featureName )
	    if ( nFound < maxNames ):
		print "##        ", namesFound[:nFound]
	else:
	    print "##        --> insufficient number of features found ... "
	    print "##            ", nFound, featureName
	    sys.exit(-1)

    elif ( sum(nFound) > 0 ):
        print " FATAL ERROR ... NOT ALLOWED ... "
	print "##     --> found %d features with <%s> " % ( nFound, featureName )
	if ( nFound < maxNames ):
	    print "##        ", namesFound[:nFound]

    else:
	print "##        --> insufficient number of features found ... "
	print "##            ", nFound, featureName
	sys.exit(-1)

    return ( tsvGeneList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getPathwayInfo ( pathwaysFile ):

    ## next we need to read the pathway definitions ...
    pwDict = readPathways ( pathwaysFile )
    pwList = pwDict.keys()
    pwList.sort()
    print "##     --> number of pathways : %d " % len(pwList)

    ## and form a gene list based on the pathways ...
    pwGeneList = []
    pwSum1 = 0
    pwSum2 = 0
    numDup = 0
    for aPW in pwList:
        ## print pwDict[aPW]
	pwLen = len(pwDict[aPW])
	pwSum1 += pwLen
	pwSum2 += ( pwLen * pwLen )
	for aGene in pwDict[aPW]:
	    if ( aGene not in pwGeneList ):
	        pwGeneList += [ aGene ]
	    else:
		numDup += 1
    pwAvg1 = float(pwSum1)/float(len(pwList))
    pwAvg2 = float(pwSum2)/float(len(pwList))
    pwSigma = math.sqrt ( pwAvg2  -  pwAvg1 * pwAvg1 )
    print "##     --> average # of genes in each pathway : %.1f  (%.1f) " % ( pwAvg1, pwSigma )
    print "##     --> length of pathway gene list : %d (%d) " % ( len(pwGeneList), numDup )
    if ( debugFlag ): print pwGeneList
    print "## "
    print "## (c) TIME ", time.asctime(time.localtime(time.time()))
    print "## "

    return ( pwDict, pwGeneList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def compareGeneLists ( tsvGeneList, pwGeneList, pwDict ):

    pwList = pwDict.keys()
    pwList.sort()

    ## NEW: now checking if any of the pathway genes are NOT in the tsvGeneList ???
    numNotFound = 0
    for aGene in pwGeneList:
	if ( aGene not in tsvGeneList ):
	    print "## gene <%s> in one or more pathways but not in feature matrix " % aGene
	    numNotFound += 1
    if ( numNotFound > 0 ):
        print "##     --> %d genes found in one or more pathways but not in feature matrix " % numNotFound
	pwGeneList = []
	for aPW in pwList:
	    newList = []
	    for aGene in pwDict[aPW]:
	        if ( aGene in tsvGeneList ):
		    newList += [ aGene ]
		    if ( aGene not in pwGeneList ):
		        pwGeneList += [ aGene ]
	    if ( newList != pwDict[aPW] ):
		oldLen = len(pwDict[aPW])
		del ( pwDict[aPW] )
		if ( len(newList) == 0 ):
		    print "##         eliminating pathway <%s> " % ( aPW )
		else:
	            print "##         replacing gene list for pathway <%s> (%d -> %d) " % ( aPW, oldLen, len(newList) )
		    kk = aPW.find("__")
		    newName = aPW[:kk] + "__" + "%d" % len(newList)
		    pwDict[newName] = newList
		    print "##             --> new pathway label: <%s> " % newName
        print "##     --> NEW length of pathway gene list : %d " % ( len(pwGeneList) )

    return ( pwGeneList )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
## outLines is a list, and one entry looks like this:
## [493.7, [' 493.7', 'RANDOM_PATHWAY_33329__72', '\n']]

def parseOutput ( pwScores, pwDict ):

    pwKeys = pwDict.keys()
    pwKeys.sort()

    maxScore = -999999
    minScore =  999999

    outLines = []
    for ii in range(len(pwScores)):
        curScore = pwScores[ii]
        if ( curScore > maxScore ): maxScore = curScore
        if ( curScore < minScore ): minScore = curScore
        curPW = pwKeys[ii]
        aLine = [ curScore, [ str(curScore), curPW ] ]
        outLines += [ aLine ]

    return ( outLines, maxScore, minScore )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def scoreOutput ( outLines, iMaxScore, iMinScore, pwDict ):

    iMaxScore = int ( iMaxScore + 0.5 )
    iMinScore = int ( iMinScore )

    ## no need to have too many discrete values ... just makes the counts matrix 
    ## too big and slows everything down ...
    min_sFactor = 10.
    ## min_sFactor =  2.
    sFactor = max ( float(iMaxScore/2001.), min_sFactor ) 
    iMaxScore = int ( float(iMaxScore/sFactor) + 0.5 )

    ## forcing iMinScore to zero ... after this it will not really be used ...
    iMinScore = 0
    print "## range of integer scores we will use : ", iMinScore, iMaxScore
    print "## using score scale factor : ", sFactor

    numOut = len(outLines)
    print "## numOut = ", numOut

    numReal = float(numOut)/float(numRandFactor+1)
    numRand = numOut - numReal
    print "## numReal = ", numReal
    print "## numRand = ", numRand

    print "## (i) TIME ", time.asctime(time.localtime(time.time()))

    ## NEW:
    ## we will build up a matrix of numHi/numLo counts as a function of 
    ## pathway size (n), and pathway score (s)

    ## also at this point forcing minLen to 0 ... will not really be used after this
    minLen = 0
    numN = int ( maxLen ) + 1
    numS = int ( iMaxScore + 1 ) + 1
    print "## size of countsHiLo matrix: %d x %d ... [%d,%d] and [%d,%d]" % \
        ( numN, numS, minLen, maxLen, iMinScore, iMaxScore )
    countsHiLo = [0] * numN
    for iN in range(numN):
        countsHiLo[iN] = [0] * numS
	for iS in range(numS):
	    countsHiLo[iN][iS] = [0,0]

    print "## (j) TIME ", time.asctime(time.localtime(time.time()))
    print "## now setting up countsHiLo matrix ... "

    ## set up a dictionary that maps from pathway name to pathway length so we
    ## don't have to figure that out repeatedly ...
    pwLenDict = {}
    for aPW in pwDict.keys():
        curPW = aPW
        kk = curPW.find("__")
        curLen = int ( curPW[kk+2:] )
        pwLenDict[curPW] = curLen

    ## we only need to loop once over all of the pathways that have been scored
    ## and then increment the appropriate counts 
    for iTuple in range(len(outLines)):
	keyVal = outLines[iTuple][0]
	tokenList = outLines[iTuple][1]
	curPW = tokenList[1]
	## if ( iTuple%1000 == 0 ): print iTuple, keyVal, tokenList, curPW
	
	if ( 1 ):

	    ## we will only consider random pathways
	    if ( curPW.find("RANDOM") >= 0 ):

                if ( 0 ):
	            kk = curPW.find("__")
	            rndLen = int ( curPW[kk+2:] )
                else:
                    rndLen = pwLenDict[curPW]

	        rndScore = float ( keyVal )
		rndScore = int ( (rndScore/sFactor) + 0.5 )

                if ( 0 ):
                    print "## random pathway ... %d %d %s " % ( rndLen, rndScore, curPW )
                    print "##     increment HI counts from (%d,0) to (%d,%d) " % ( rndLen, numN-1, rndScore )
                    print "##           and LO counts from (0,%d) to (%d,%d) " % ( rndScore+1, rndLen-1, numS-1 )

                ## ----------------------------------------- ##
                ## THIS IS THE CODE CURRENTLY BEING USED !!! ##
                ## ----------------------------------------- ##

                ## current score is (n,s) ranges are: 0 thru N-1 and 0 thru S-1
                ## THIS random pathway will be considered 'better' (HI) than ~real~ pathways
                ## that are longer and score worse ... and will be considered 'worse' (LO)
                ## than ~real~ pathways that are shorter and score better

		if ( 1 ):
		    ## first increment the HI counts ...
                    ##     for pathway lengths greater than or equal to (n, n+1, n+2, ... N-1)
                    ##     and scores less than or equal to             (0, 1, 2, ... s-1)
		    for iN in range(rndLen, numN):
		        for iS in range(0, rndScore+1):
			    countsHiLo[iN][iS][0] += 1
		    ## and then the LO counts ...
                    ##     for pathway lengths less than or equal to    (0, 1, 2, ... n)
                    ##     and scores greater than                      (s+1, s+2, s+3, ... S-1)
		    for iN in range(0, rndLen):
		        for iS in range(rndScore+1,numS):
			    countsHiLo[iN][iS][1] += 1

    print "## (k) TIME ", time.asctime(time.localtime(time.time()))
    print "## now computing estimated p values ... "

    ## and once we have the countsHiLo matrix we do one more pass to estimate the p-values
    estLogP = [0] * len(outLines)
    for iTuple in range(len(outLines)):
        keyVal = outLines[iTuple][0]
	tokenList = outLines[iTuple][1]
	curPW = tokenList[1]
	## if ( iTuple%1000 == 0 ): print iTuple, keyVal, tokenList, curPW

	if ( 1 ):
	    kk = curPW.find("__")
	    curLen = int ( curPW[kk+2:] )
	    curScore = float ( keyVal )
	    curScore = int ( (curScore/sFactor) + 0.5 )
	    numHi = countsHiLo[curLen][curScore][0]
	    numLo = countsHiLo[curLen][curScore][1]

            ## print "## --> curLen=%d  curScore=%d  numHi=%d  numLo=%d " % ( curLen, curScore, numHi, numLo )
            try:
		try:
                    tmpLogP = -1. * math.log10 ( float(numHi+1)/float(numHi+numLo+1) )
		except:
		    print " ERROR computing tmpLogP ??? ", numHi, numLo
		    sys.exit(-1)
		try:
                    estLogP[iTuple] = ( tmpLogP, numHi, numLo )
		except:
		    print " ERROR storing tuple ??? ", tmpLogP, numHi, numLo
		    print iTuple, len(estLogP)
		    print estLogP
		    sys.exit(-1)
		try:
                    ## print "         ", iTuple, curLen, curScore, tmpLogP
                    if ( 1 ):
                        if ( tmpLogP >= 1. ):
                            if ( (numHi+numLo) < numRandFactor ):
                                print "##             maybe too few counts for p-value estimate ??? ", (numHi+numLo), numHi, numLo
		except:
		    print " stupid stupid stupid error "
		    sys.exit(-1)
            except:
                print "## failed in attempt to estimate p value ??? ", numHi, numLo
                sys.exit(-1)

    return ( countsHiLo, estLogP )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def prettyPrintScores ( outLines, estLogP ):

    print "## "
    print "## (l) TIME ", time.asctime(time.localtime(time.time()))
    print "## "
    print "## RANKED and SCORED Pathways : "
    print "## "

    for iTuple in range(len(outLines)):
        keyVal = outLines[iTuple][0]
	tokenList = outLines[iTuple][1]
	curPW = tokenList[1]

	if ( 1 ):
	    try:
	        outLine = "%.2f\t%d\t%d\t" % ( estLogP[iTuple][0], estLogP[iTuple][1], estLogP[iTuple][2] )
	    except:
	        outLine = "-99\t-99\t-99\t" 
	    for aToken in tokenList:
	        if ( aToken == '\n' ):
		    doNothing = 1
	        elif ( aToken.endswith('\n') ):
	            outLine += "%s\t" % aToken[:-1]
	        else:
	            outLine += "%s\t" % aToken
	    print outLine

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# ok ... cleaning this function up entirely ...
#     pwDict is the pathway dictionary, including random pathways -- keys are
#         pathway names, and associated with each key is a list of gene symbols
#     pwpvData is the pairwise data dict, where the keys are gene symbols and
#         associated to each key is a tuple ( -log(p), rho, dist )

def goScorePathways ( pwDict, pwpvData ):

    pwKeys = pwDict.keys()
    pwKeys.sort()
    pwpvKeys = pwpvData.keys()

    ## print " pwDict ", len(pwDict), pwKeys[0], pwDict[pwKeys[0]]
    ## print " pwpvData ", len(pwpvData), pwpvKeys[0], pwpvData[pwpvKeys[0]]

    # we really just want a dictionary with the p-values and not those data triples ...
    pDict = {}
    for aKey in pwpvKeys:
        pVal = pwpvData[aKey][0]
        if ( pVal > 0. ):
            pDict[aKey] = pVal

    # and now we can score each pathway ...
    pwScores = [0] * len(pwKeys)
    for ii in range(len(pwKeys)):
        if ( 0 ):
            if ( ii%50000 == 0 ):
                print "## (z) TIME ", ii, time.asctime(time.localtime(time.time()))
        curPW = pwKeys[ii]
        for aGene in pwDict[curPW]:
            try:
                pwScores[ii] += pDict[aGene]
            except:
                doNothing=1

    print "## range of pathway scores : ", min(pwScores), max(pwScores)

    return ( pwScores )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
## this functions seeks to score/rank pathways (which can also be just arbitrary
## lists of genes) based on associations to a particular feature (or set of
## features)
##
## inputs required:
##	a TSV feature matrix
##	a corresponding pairwise output file
##	a pathways-definition file
##	a feature name of interest, eg C:SAMP:PAM50_call or B:GNAB:driverMut:
##	the gene-based data type (typically N:GEXP: but can be N:METH:)
##	the maximum genomic distance allowed betwen the two features in any 
##	    significant association -- this is typically used to require
##	    that the two features be close together ... if they can be
##	    any distance apart, then use -1 (NOTE that there is no way to 
##	    force them to be at least X distance apart)
##	an optional threshold on the p-values (-log(p)) >= 0
##	an optional correlation sign ('+' or '-')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='pathway-scoring')
    parser.add_argument('--tsvFile',  '-tsv', action='store', required=True)
    parser.add_argument('--pwpvFile', '-pw',  action='store', required=True)
    parser.add_argument('--pathways', '-P',   action='store', required=True)
    parser.add_argument('--featName', '-f',   action='store', required=True)
    parser.add_argument('--dataType', '-d',   action='store', default="N:GEXP:")
    parser.add_argument('--maxDist',  '-D',   action='store', default=-1, type=int)
    parser.add_argument('--pThresh',  '-T',   action='store', default= 0, type=float)
    parser.add_argument('--sign',     '-s',   action='store', default='x')
    parser.add_argument('--nRand',    '-N',   action='store', default=1000, type=int)

    args = parser.parse_args()

    tsvFilename  = args.tsvFile
    pwpvFilename = args.pwpvFile
    pathwaysFile = args.pathways
    featureNameString = args.featName

    geneDataType = args.dataType
    maxDist = args.maxDist
    minLogP = args.pThresh
    corrSign = args.sign
    numRandFactor = args.nRand

    if ( corrSign != '+' ):
        if ( corrSign != '-' ):
            corrSign = ''


    print "## RUNNING %s with : " % sys.argv[0]
    print "##                %s " % tsvFilename
    print "##                %s " % pwpvFilename
    print "##                %s " % pathwaysFile
    print "##                %s = geneDataType " % geneDataType
    print "##                %d = maxDist  " % maxDist
    print "##                %s = corrSign " % corrSign
    print "##                %d = numRandFactor " % numRandFactor

    ## the 'featureNameString' might be a semi-colon separated list ...
    if ( featureNameString.find(";") > 0 ):
        print " FATAL ERROR ... THIS IS NOT ALLOWED ... "
        print " <%s> " % featureNameString
        sys.exit(-1)
    else:
	featureName = featureNameString
    print "##                %s " % featureName
    print "## (a) TIME ", time.asctime(time.localtime(time.time()))

    ## ------------------------------------------------------------------------
    ## first we need some information from the feature matrix (TSV) ...
    tsvGeneList = getInfoFromTSV ( tsvFilename, featureName )
    ## print tsvGeneList[:5]
    ## print tsvGeneList[-5:]

    ## ------------------------------------------------------------------------
    ## next we need to read the pathway definitions and form a gene list ...
    ( pwDict, pwGeneList ) = getPathwayInfo ( pathwaysFile )
    ##  --> pwDict is a dictionary with 224 pathways, with names, like "PS1PATHWAY__46"
    ##      and each pathway is a list of gene symbols
    ##  --> pwGeneList is a list of ~2600 genes
    if ( 0 ):
        print len(pwDict)
        aKey = pwDict.keys()[0]
        print aKey
        print pwDict[aKey]
        print len(pwGeneList)
        print pwGeneList[:5]

    ## ------------------------------------------------------------------------
    ## check pwGeneList against tsvGeneList ... and remove gene symbols that
    ## are in the pwGeneList that we don't know anything about (ie are not in
    ## the tsvGeneList)
    pwGeneList = compareGeneLists ( tsvGeneList, pwGeneList, pwDict )

    print "## (d) TIME ", time.asctime(time.localtime(time.time()))

    ## ------------------------------------------------------------------------
    ## now we can read in all pairwise information that we have for these
    ## genes ...
    print "##     --> reading in pairwise (PWPV) data ... "
    pwpvData = getPairwisePvalues ( pwpvFilename, pwGeneList, featureName, \
                                    geneDataType, maxDist, corrSign, minLogP )
    if ( len(pwpvData) == 0 ):
        print "## ERROR ??? how do we not have any information here ??? "
	sys.exit(-1)
    print "##     --> got %d values ... " % len(pwpvData)
    print "## (f) TIME ", time.asctime(time.localtime(time.time()))

    ## when we get here, the keys in pwpvData are just the gene symbols
    ## and the data associdated with a key is a tuple: ( -log(p), rho, dist )
    keyList = pwpvData.keys()
    if ( debugFlag ):
        print keyList[:5]
        print pwpvData[keyList[0]]

    ## ------------------------------------------------------------------------
    ## so what *are* the top 20 genes and what is the maximum s20 score ???
    ## NOTE that by this point we have filtered OUT any genes that are not in the pwGeneList !!!
    topGenes = findTopGenes ( pwpvData, 20 )

    ## print " HERE (a) "

    ## report on pathway membership of the top 20 genes ...
    pwMembership ( pwDict, topGenes )

    ## print " HERE (b) "

    ## 15may13 ... or look at pathway membership of all associated genes ???
    pwMembership2 ( pwDict, pwpvData )

    ## print " HERE (c) "

    ## ------------------------------------------------------------------------
    ## finally we need to generate the "random" pathways ...
    ( pwDict, minLen, maxLen ) = addRandomPathways ( pwDict, numRandFactor )
    print "## range of pathway lengths : ", minLen, maxLen
    print "## (e) TIME ", time.asctime(time.localtime(time.time()))

    ## print " HERE (d) "

    ## ------------------------------------------------------------------------
    ## and now we can finally compute the scores for all of the pathways
    ## on the cluster ...
    pwScores = goScorePathways ( pwDict, pwpvData )
    if ( debugFlag ): print len(myOutput)

    ## next parse the output ...
    ( outLines, iMaxScore, iMinScore ) = parseOutput ( pwScores, pwDict )
    ## outLines is a list, and one entry looks like this:
    ## [493.7, [' 493.7', 'RANDOM_PATHWAY_33329__72', '\n']]

    ## and now use the 'real' and 'random' pathway scores to build
    ## a hi/lo counts matrix and estimate significance ...
    ( countsHiLo, estLogP ) = scoreOutput ( outLines, iMaxScore, iMinScore, pwDict )

    ## and finally pretty-print the output ...
    prettyPrintScores ( outLines, estLogP )

    print "## "
    print "## (m) TIME (DONE) ", time.asctime(time.localtime(time.time()))
    print "## "

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
