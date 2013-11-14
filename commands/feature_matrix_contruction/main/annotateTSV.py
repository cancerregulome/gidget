#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

## these are system modules
import sys

## these are my local ones
import chrArms
import tsvIO

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def readGeneInfoFile ( geneInfoFilename ):

    geneInfoDict = {}
    synMapDict = {}

    try:
	fh = file ( infFilename, 'r' )
    except:
	print " ERROR opening gene_info file <%s> " % infFilename
	sys.exit(-1)

    for aLine in fh:
	aLine = aLine.strip()
	if ( aLine.startswith("#") ): continue
	if ( not aLine.startswith("9606") ): continue

	tokenList = aLine.split('\t')

	tax_id = tokenList[0]
	if ( tax_id != "9606" ): continue

	geneID = int ( tokenList[1] )
	symbol = tokenList[2].upper()
	locusTag = tokenList[3]
	synonyms = tokenList[4].upper()

	if ( synonyms == "-" ): continue

	symbol = symbol.upper()
        if ( symbol not in geneInfoDict.keys() ):
            geneInfoDict[symbol] = []

	synList = synonyms.split('|')
	for aSyn in synList:
	    aSyn = aSyn.upper()
	    if ( aSyn not in geneInfoDict[symbol] ):
	        geneInfoDict[symbol] += [ aSyn ]

	    if ( aSyn not in synMapDict.keys() ):
	        synMapDict[aSyn] = [ (symbol,geneID) ]
	    else:
		synMapDict[aSyn] += [ (symbol,geneID) ]

	## number of symbols with synonyms was 22558

    print " "
    print " --> finished reading gene_info file <%s> " % geneInfoFilename
    print "         %6d unique keys in geneInfoDict " % len(geneInfoDict)
    print "         %6d unique keys in synMapDict " % len(synMapDict)

    if ( 0 ):
        print " "
	print " synonyms with more than one assigned symbol ... ??? "
        for aSyn in synMapDict.keys():
            if ( len ( synMapDict[aSyn] ) > 1 ):
	        print aSyn, synMapDict[aSyn]
	print " "

    return ( geneInfoDict, synMapDict )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def readCytobandFile ( cybFilename ):

    cytoDict = {}

    try:
	fh = file ( cybFilename, 'r' )
    except:
	print " ERROR opening cytoband file <%s> " % cybFilename
	sys.exit(-1)

    for aLine in fh:
	aLine = aLine.strip()
	tokenList = aLine.split('\t')

	chrName = tokenList[0].lower()
	bndName = tokenList[3]
	iStart = int ( tokenList[1] )
	iStop  = int ( tokenList[2] )

	if ( chrName not in cytoDict.keys() ):
	    cytoDict[chrName] = []
	cytoDict[chrName] += [ ( bndName, iStart, iStop ) ]

    fh.close()

    if ( 0 ):
        allNames = cytoDict.keys()
        allNames.sort()
        for aName in allNames:
            maxP = -1
	    maxQ = -1
	    for aTuple in cytoDict[aName]:
	        if ( aTuple[0].startswith("p") ):
	            if ( maxP < aTuple[2] ):
		        maxP = aTuple[2]
	        elif ( aTuple[0].startswith("q") ):
	            if ( maxQ < aTuple[2] ):
		        maxQ = aTuple[2]
	    ## print aName, maxP, maxQ
	    print "arms_hg['%sp'] = ( %9d, %9d )" % ( aName[3:], 0, maxP )
	    print "arms_hg['%sq'] = ( %9d, %9d )" % ( aName[3:], maxP, maxQ )
        sys.exit(-1)

    return ( cytoDict )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def readRefGeneFile ( refGeneFilename ):

    refGeneDict = {}

    try:
	fh = file ( refGeneFilename, 'r' )
    except:
	print " ERROR opening refGene file <%s> " % refGeneFilename
	sys.exit(-1)

    for aLine in fh:
	aLine = aLine.strip()
	tokenList = aLine.split('\t')

	## this file has 16 columns
	##	[0]  - a numeric index of some sort
	##	[1]  - NM_*
	##	[2]  - chromosome (eg 'chr17')
	##	[3]  - strand (eg '-')
	##	[4]  - start position (eg 7571719)
	##	[5]  - stop position (eg 7590868)
	##	[6]  - another start of some sort
	##	[7]  - another stop
	##	[8]  - # of exons (?)
	##	[9]  - comma-delimited positions
	##	[10] - comma-delimited positions
	##	[11] - ?
	##	[12] - gene symbol (eg 'TP53')
	##	[13] - ?
	##	[14] - ?
	##	[15] - comma-delimited integers

	geneName = tokenList[12]

	## CHR17:7565097-7590863:-
	coordString = tokenList[2].upper() + ':' + tokenList[4] + '-' + tokenList[5] + ':' + tokenList[3]

	## if we already have this geneName, just make sure that the
	## coordinates cover the largest possible extent ...
	if ( geneName in refGeneDict.keys() ):

	    oldString = refGeneDict[geneName]
	    if ( oldString == coordString ):
	        continue

	    oldTokens = oldString.split(':')

	    if ( oldTokens[0] != tokenList[2].upper() ):
	        continue

	    ii = oldTokens[1].find('-')
	    oldStart = int ( oldTokens[1][:ii] )
	    oldStop  = int ( oldTokens[1][ii+1:] )

	    curStart = int ( tokenList[4] )
	    curStop  = int ( tokenList[5] )

	    updateFlag = 0
	    newStart = oldStart
	    newStop = oldStop

	    if ( curStart < oldStart ):
	        updateFlag = 1
		newStart = curStart
	    if ( curStop > oldStop ):
	        updateFlag = 1
		newStop = curStop

	    coordString = oldTokens[0] + ':' + str(newStart) + '-' + str(newStop) + ':' + oldTokens[2]
	    refGeneDict[geneName] = coordString

	    ## print "     --> updated <%s> to <%s> " % ( oldString, coordString )

 	else:
	    refGeneDict[geneName] = coordString

    fh.close()

    print " in readRefGeneFile ... "
    print "     length of refGeneDict w/ coords ..... ", len(refGeneDict), len(refGeneDict.keys())

    return ( refGeneDict )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def readGAF ( gafFilename ):

    geneCoordDict_bySymbol = {}
    geneCoordDict_byID = {}
    geneSymbol_byID = {}

    try:
        fh = file ( gafFilename, 'r' )
    except:
	print " ERROR opening GAF file <%s> " % gafFilename
	sys.exit(-1)

    for aLine in fh:
	aLine = aLine.strip()
	aLine = aLine.upper()

	if ( aLine.startswith("#") ): continue
	tokenList = aLine.split('\t')

	if ( len(tokenList) < 17 ): continue

	if ( not tokenList[16].startswith("CHR") ):
	    ## print " f17 does not start with CHR ??? "
	    ## print tokenList[16]
	    if ( tokenList[16].find("CHR") >= 0 ):
	        ## print "     but there is some CHR info somewhere ??? "
		## print tokenList[16]
		doNothing = 1
	    else:
	        ## print " --> SKIPPING "
	        continue

	## column 3 contains one of the following strings:
	##	AffySNP, componentExon, compositeExon, gene, junction, MAprobe, miRNA, pre-miRNA, transcript
	if ( tokenList[2] == "AFFYSNP" ): continue
	if ( tokenList[2] == "COMPONENTEXON" ): continue
	if ( tokenList[2] == "COMPOSITEEXON" ): continue
	if ( tokenList[2] == "JUNCTION" ): continue
	if ( tokenList[2] == "MAPROBE" ): continue
	if ( tokenList[2] == "TRANSCRIPT" ): continue

	geneToken = tokenList[1]
	geneTokenList = geneToken.split('|')
	geneName = geneTokenList[0].upper()
	if ( len(geneTokenList) == 2 ):
	    geneID = geneTokenList[1]
	else:
	    geneID = '?'

	if ( 0 ):
	    ## we're skipping entries of the form ?|791120 or T|6862
	    if ( geneName == '?' ): continue
	    if ( len(geneName) == 1 ): continue

	## what if there are multiple coordinates???
	coordToken = tokenList[16]
	coordTokenList = coordToken.split(';')
	if ( len(coordTokenList) > 1 ):
	    ## print " need to do something about this ... "
	    ## print coordTokenList
	    mergeCoord = mergeCoordinates ( coordTokenList )
	    if ( mergeCoord == "" ):
	        ## print " --> failed to get coordinates ... skipping ... "
		continue
	    coordToken = mergeCoord
	    ## print " --> changed to: ", coordToken

	## print " ready to add : ", geneName, geneID, coordToken

	if ( len(geneName) > 1 ):
	    if ( geneName in geneCoordDict_bySymbol.keys() ):
		doNothing = 1
	    else:
	        geneCoordDict_bySymbol[geneName] = coordToken

	if ( geneID != '?' ):
	    if ( geneID in geneCoordDict_byID.keys() ):
	        doNothing = 1
	    else:
	        geneCoordDict_byID[geneID] = coordToken

	## 19dec12 : now also creating the geneSymbol_byID dict ...
	if ( geneID != '?' ):
	    if ( geneID in geneSymbol_byID.keys() ):
		if ( geneName not in geneSymbol_byID[geneID] ):
		    print " this should never happen should it ??? ", geneID, geneName, geneSymbol_byID[geneID]
	            geneSymbol_byID[geneID] += [ geneName ]

		    ## HACK
		    if ( geneID == "378108" ):
		        geneSymbol_byID[geneID] = [ "TRIM74" ]
	    else:
	        geneSymbol_byID[geneID] = [ geneName ]


    fh.close()

    print " in readGAF ... "
    print "     length of geneCoordDict_bySymbol w/ coords ..... ", len(geneCoordDict_bySymbol), len(geneCoordDict_bySymbol.keys())
    print "     length of geneCoordDict_byID     w/ coords ..... ", len(geneCoordDict_byID), len(geneCoordDict_byID.keys())
    print "     length of geneSymbol_byID  ..................... ", len(geneSymbol_byID)

    print " "
    print " sanity-checking geneSymbol_byID dictionary ... "
    for geneID in geneSymbol_byID.keys():
        if ( len(geneSymbol_byID[geneID]) > 1 ):
	    print geneID, geneSymbol_byID[geneID]
    print " "
    print " "

    return ( geneCoordDict_bySymbol, geneCoordDict_byID, geneSymbol_byID )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def mergeCoordinates ( coordTokenList ):

    ## print " in mergeCoorodinates ... "
    ## print coordTokenList

    ## sometimes we seem to have a '?' instead of a proper coordinate string
    ## so get rid of that if it shows up ...
    tmpList = []
    for ii in range(len(coordTokenList)):
        if ( coordTokenList[ii].startswith("CHR") ):
	    tmpList += [ coordTokenList[ii] ]
    coordTokenList = tmpList
    ## print coordTokenList
    if ( len(coordTokenList) == 0 ):
	return ( "" )

    ## and now we can work with the corrected list ...
    for ii in range(len(coordTokenList)):

	posInfo = parseCoordinates ( coordTokenList[ii] )
	## print posInfo

	## make sure that the chrName is consistent ... strand also
	if ( ii == 0 ):

	    ## grab all of the information for the very first coordinate range
	    ## and keep it  ...
	    chrName = posInfo[0]
	    iStart = posInfo[1]
	    iStop = posInfo[2]
	    aStrand = posInfo[3]

	    ## meanwhile, if we are merging multiple coordinate ranges
	    ## that will be done using jStart and jStop
	    jStart = iStart
	    jStop  = iStop

	else:

	    if ( chrName != posInfo[0] ):
		## print " multiple chromosomes in mergeCoordinates ... "
		## print " --> keeping only the first "
		## print coordTokenList
		mergeCoord = chrName + ':' + str(iStart) + '-' + str(iStop) + ':' + aStrand
		return ( mergeCoord )

	    if ( aStrand != posInfo[3] ):
		## print " WARNING ... different strands ... but not halting ... "
		## print coordTokenList
		doNothing = 1

	jStart = min ( jStart, posInfo[1] )
	jStop = max ( jStop, posInfo[2] )

    mergeCoord = chrName + ':' + str(jStart) + '-' + str(jStop) + ':' + aStrand

    return ( mergeCoord )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def parseCoordinates ( coordInfo ):

    posInfo = []
    i1 = coordInfo.find(':')
    i2 = coordInfo.find('-',i1)
    i3 = coordInfo.find(':',i2)
    ## print coordInfo[:i1], coordInfo[i1+1:i2], coordInfo[i2+1:i3], coordInfo[i3+1:]
    try:
         posInfo = [ coordInfo[:i1], int(coordInfo[i1+1:i2]), int(coordInfo[i2+1:i3]), coordInfo[i3+1:] ]
    except:
        print coordInfo[:i1], coordInfo[i1+1:i2], coordInfo[i2+1:i3], coordInfo[i3+1:]
	sys.exit(-1)

    return ( posInfo )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function looks for the gene or genes that overlap the segment defined
# by the input 'curRowLabel' coordinates

def overlap ( curRowLabel, geneCoordDict_bySymbol ):

    tokenList = curRowLabel.split(':')
    geneList = []

    if ( tokenList[3] != '' ):

	## first try to parse out genomic coordinates from
	## the current row label ... it is possible that 
	## the row label does not have coordinates
	try:
            chrName = tokenList[3].upper()
	    chrStart = int ( tokenList[4] )
	    chrStop = int ( tokenList[5] )
	    ## print chrName, chrStart, chrStop
	except:
	    return ( [] )

	## if we get here, then we have coordinates so we now
	## loop over the genes in our geneCoordDict_bySymbol and look for 
	## any that overlap ...
	for aGene in geneCoordDict_bySymbol.keys():

	    ## if this gene is not even on the same chromosome we're done ...
	    if ( not geneCoordDict_bySymbol[aGene].startswith(chrName+':') ): continue

	    ## but if it is, then we need to check start/stop
	    posInfo = parseCoordinates ( geneCoordDict_bySymbol[aGene] )
	    if ( chrStop < posInfo[1] ): continue
	    if ( chrStart > posInfo[2] ): continue
	    ## print posInfo

	    ## there seem to be some "bad" gene names ???
	    if ( aGene == '?' ): continue

	    if ( len(aGene) == 1 ):
	        print " how is this happening ??? "
		print curRowLabel, aGene, geneCoordDict_bySymbol[aGene]
		sys.exit(-1)

	    geneList += [ aGene ]

	if ( len(geneList) > 0 ):
	    if ( 0 ):
	        if ( len(geneList) > 1 ):
		    print " got multiple genes ... ", geneList, tokenList
	    return ( geneList )
	else:
	    ## print " in overlap ... nada? ", curRowLabel
	    return ( [] )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def stripLastNameFromDir ( d1Name ):

    ii = len(d1Name) - 1
    while ( d1Name[ii] != '/' ): ii -= 1
    tumorType = d1Name[ii+1:]
    return ( tumorType )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def read_pairs_from_file ( SLpairsFile ):

    genePairs = []
    fh = file ( SLpairsFile )
    for aLine in fh:
        aLine = aLine.strip()
	aLine = aLine.upper()
	tokenList = aLine.split()
	if ( len(tokenList) != 2 ): continue
	if ( tokenList[0] == tokenList[1] ): continue

	if ( tokenList[0] < tokenList[1] ):
	    curPair = ( tokenList[0], tokenList[1] ) 
	else:
	    curPair = ( tokenList[1], tokenList[0] ) 

	if ( curPair not in genePairs ):
	    genePairs += [ curPair ]

    return ( genePairs )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lookAtDict ( pairAssocDict ):

    print " "
    print " "
    print " in lookAtDict ... ", len(pairAssocDict)

    keyList = pairAssocDict.keys()
    keyList.sort()
    ## print keyList[:5]
    ## print keyList[-5:]

    maxCount = 0
    maxKeys = []

    for aKey in keyList:
        ## print aKey, len(pairAssocDict[aKey])
	## print pairAssocDict[aKey]

	typeCounts = {}
	for aTuple in pairAssocDict[aKey]:
	    aType = ( aTuple[0], aTuple[1] )
	    if ( aType not in typeCounts.keys() ):
	        typeCounts[aType] = 0
	    typeCounts[aType] += 1
	curCount = len(pairAssocDict[aKey])

	if ( 0 ):
	    if ( curCount > 3 ):
	        print curCount, aKey, typeCounts

	## write out the number of types of associations, then pair, and then the typeCounts
	print len(typeCounts), aKey, typeCounts

	if ( curCount > maxCount ):
	    maxCount = curCount
	    maxKeys = [ aKey ]
	elif ( curCount == maxCount ):
	    maxKeys += [ aKey ]

    if ( 0 ):
	## so, at first I was looking at the number of associations, but that
	## really depends mostly on the # of different features and in particular
	## there could be a lot of GNAB or CNVR or METH features for one gene
	## and only one of each for another ...

        print " "
        print " keys with the most associations: ", maxCount
        for aKey in maxKeys:
	    typeCounts = {}
	    for aTuple in pairAssocDict[aKey]:
	        aType = ( aTuple[0], aTuple[1] )
	        if ( aType not in typeCounts.keys() ):
	            typeCounts[aType] = 0
	        typeCounts[aType] += 1
	    curCount = len(pairAssocDict[aKey])

	    print curCount, aKey, typeCounts

        print " "
        print " keys with at least %d associations: " % (maxCount/2)
        for aKey in keyList:
	    typeCounts = {}
	    for aTuple in pairAssocDict[aKey]:
	        aType = ( aTuple[0], aTuple[1] )
	        if ( aType not in typeCounts.keys() ):
	            typeCounts[aType] = 0
	        typeCounts[aType] += 1
	    curCount = len(pairAssocDict[aKey])

	    if ( curCount >= (maxCount/2) ):
	        print curCount, aKey, typeCounts


    print " "
    print " "
        

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def hasSpecialChar ( aName ):

    if ( aName.find(":") >= 0 ): return ( 1 )
    if ( aName.find("?") >= 0 ): return ( 1 )
    if ( aName.find("'") >= 0 ): return ( 1 )
    if ( aName.find("|") >= 0 ): return ( 1 )

    return ( 0 )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# curLabel : N:RPPA:ACACA:::::ACC1-R-C 
# curGene  : ACACA 
# posInfo  : CHR17:32516040-32841015:-

def annotateLabel ( curLabel, curGene, posString ):

    print " in annotateLabel ... "
    print curLabel
    print curGene
    print posString

    i1 = posString.find(":")
    i2 = posString.find("-",i1+1)
    i3 = posString.find(":",i1+1)

    chrName = posString[:i1].lower()
    if ( chrName.endswith('x') ):
        chrName = chrName[:-1] + "X"
    elif ( chrName.endswith('y') ):
        chrName = chrName[:-1] + "Y"

    iStart = int ( posString[i1+1:i2] )
    iStop = int ( posString[i2+1:i3] )
    aStrand = posString[-1]

    ## print chrName, iStart, iStop, aStrand

    if ( 0 ):
        ## before, we were assuming that the gene name did not change ...
	i1 = curLabel.find(":",7)
	newLabel = curLabel[:i1] + ":" + chrName + ":" + str(iStart) + ":" + str(iStop) + ":" + aStrand + curLabel[(i1+4):]
    else:
	## but now we are allowing for the incoming curGene to be a new symbol ...
	## print curLabel
	tokenList = curLabel.split(':')
	newLabel = tokenList[0] 
	newLabel += ":" + tokenList[1] 
	newLabel += ":" + curGene 
	newLabel += ":" + chrName + ":" + str(iStart) + ":" + str(iStop) + ":" + aStrand
	if ( len(tokenList) > 7 ):
	    newLabel += ":" + tokenList[7]
	## print newLabel
	if ( len(tokenList) > 8 ):
	    print " ERROR ??? too many tokens ??? "
	    print curLabel
	    print len(tokenList), tokenList
	    print newLabel
	    sys.exit(-1)

    print " --> newLabel : ", newLabel
    return ( newLabel )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getCytobandLabel ( curLabel, cytoDict ):

    tokenList = curLabel.split(':')
    chrName = tokenList[3].lower()
    if ( not chrName.startswith("chr") ): 
	print " chrName does not start with chr ??? ", chrName
	sys.exit(-1)
        return ( "" )

    try:
	iStart = int ( tokenList[4] )
	if ( tokenList[5] != '' ):
	    iStop  = int ( tokenList[5] )
	else:
	    iStop = iStart

	## print chrName, iStart, iStop
	## print cytoDict[chrName]

	tList = []
	oList = []
	for aTuple in cytoDict[chrName]:
	    if ( aTuple[1] > iStop  ): continue
	    if ( aTuple[2] < iStart ): continue
	    tList += [ aTuple[0] ]

	    oLap = min(aTuple[2],iStop) - max(aTuple[1],iStart) + 1
	    oList += [ oLap ]
	
    except:
	print " failed to find cytoband ??? ", curLabel
	print cytoDict.keys()
	print cytoDict[chrName]
	sys.exit(-1)
        return ( "" )

    if ( 0 ):
        print " "
        print " curLabel : ", curLabel
        print " tList : ", tList
        print " oList : ", oList

    if ( len(tList) == 0 ):
        print " why didn't we find any cytobands ??? "
	print cytoDict.keys()
	print cytoDict[chrName]
	return ( "" )

    ## print len(tList), tList, oList
    if ( len(tList) == 1 ): 
	cbName = tList[0]
        if ( chrName.startswith("chr") ):
	    ## tack on the chromosome # before returning ...
            cbName = chrName[3:].upper() + cbName
	    return ( cbName )
	else:
	    print " ERROR ??? ", chrName, cbName
	    sys.exit(-1)

    ## if we have more than one label, then we need to find the 
    ## shortest common substring ...
    cbName = ""
    minLen = len(tList[0])
    for aName in tList:
        if ( minLen > len(aName) ):
	    minLen = len(aName)
    done = 0
    ii = 0
    while not done:
	sameFlag = 1
	for aName in tList:
	    if ( aName[ii] != tList[0][ii] ):
	        sameFlag = 0
		done = 1
	if ( sameFlag ):
	    cbName += aName[ii]
	ii += 1
	if ( ii >= minLen ):
	    done = 1

    if ( len(cbName) > 1 ):
        if ( cbName[-1] == '.' ):
            cbName = cbName[:-1]

    ## print " --> cbName : ", cbName
    if ( len(cbName) < 3 ):
        ## or if that didn't work well, then choose the one 
	## cytoband with the largest overlap ...
	## FIXME: OR, we could just go down to 'p' or 'q' ???
	maxOlap = 0
	for ii in range(len(tList)):
	    if ( maxOlap < oList[ii] ):
	        maxOlap = oList[ii]
		cbName = tList[ii]
	## print cbName, maxOlap

    if ( chrName.startswith("chr") ):
	## tack on the chromosome # before returning ...
        cbName = chrName[3:].upper() + cbName
	return ( cbName )
    else:
	print " ERROR ??? ", chrName, cbName
	sys.exit(-1)
	
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def hackMicroRNAname ( oldName ):

    if ( not oldName.startswith("HSA-MIR-") ):
        return ( oldName )

    newName = "HSA-MIR-"
    i1 = 8
    i2 = oldName.find("-",i1)
    if ( i2 < 0 ): i2 = len(oldName)
    try:
        iNum = int ( oldName[i1:i2] )
    except:
	return ( oldName )

    newName = newName + ( "%d" % iNum ) + "A" 
    if ( i2 < len(oldName) ):
        newName = newName + oldName[i2:]

    print " in hackMicroRNAname ... <%s> <%s> " % ( oldName, newName )
    return ( newName )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def chooseBestName ( curGene, curID, curType, geneInfoDict, synMapDict, geneCoordDict_bySymbol, geneCoordDict_byID ):

    ## we are missing a few dozen microRNAs ...
    if ( curType == "MIRN" ):
        if ( curGene not in geneCoordDict_bySymbol.keys() ):
	    print " MIRN <%s> not found " % curGene
	    tstGene = hackMicroRNAname ( curGene )
	    if ( tstGene in geneCoordDict_bySymbol.keys() ):
	        print "     --> returning <%s> " % tstGene
	        return ( tstGene )
	    else:
		print "     --> still not found ... oh well ... "
		return ( curGene )

    ## this approach does not seem to be a good idea ... it is resulting
    ## in duplicate feature names, for example, the RNAseq data has 
    ## the gene ABCD1 and then later has AMN which seems to be a synonym
    ## for ABCD1 ... so at this point we are ONLY changing the MIRN names
    if ( 0 ):
        return ( curGene )

    ## ---- obsolete ---- ##
    ## trying to reinstate this in Jan 2013 ##

    ## we default to the current gene name ... but it might get changed ...
    newGene = curGene

    ## for now, we will not change the names of microRNAs ... 
    if ( curType == "MIRN" ):
	return ( newGene )

    ## if this gene appears to be an "official" gene symbol, then keep it ...
    if ( curGene in geneInfoDict.keys() ):
        return ( curGene )

    ## otherwise go looking in the synonyms ...
    if ( curGene in synMapDict.keys() ):
        print " QQ  this gene name appears to be a synonym ??? ", curGene, curID
	print curGene, synMapDict[curGene]
	if ( len(synMapDict[curGene]) == 1 ):
	    aTuple = synMapDict[curGene][0]
	    aGene = aTuple[0]
	    aID = aTuple[1]
	    if ( str(aID) == str(curID) ):
	        print " QQ  --> changing name to <%s> " % synMapDict[curGene][0][0]
	        newGene = synMapDict[curGene][0][0]
	        if ( newGene not in geneCoordDict_bySymbol.keys() ):
	            print " QQ  BUT the new name is not in the GAF file ??? "
		    if ( curGene in geneCoordDict_bySymbol.keys() ):
		        print " QQ  --> so changing back ... "
		        newGene = curGene
		    else:
		        print " QQ  --> but neither is the old one, so going with new "
		        doNothing = 1
	    else:
		print " QQ  --> but the ID of the only associated gene does not match ??? <%s> <%s> <%s> <%s> " % \
				( curGene, curID, aGene, aID )
		print " QQ      <%s> <%s> " % ( str(aID), str(curID) )
		doNothing = 1

	else:

	    ## first see if we can find a matching ID ...
	    foundMatchingID = 0
	    for aTuple in synMapDict[curGene]:
	        aGene = aTuple[0]
		aID = aTuple[1]
		if ( str(aID) == str(curID) ):
		    newGene = aGene
		    print " QQ  found matching ID !!! ", aTuple
		    foundMatchingID = 1

	    if ( not foundMatchingID ):
	        print " QQ  now what ??? ", synMapDict[curGene]
	        lowNum = 999999999
	        lowGene = ''
	        for aTuple in synMapDict[curGene]:
	            aGene = aTuple[0]
		    if ( aGene in geneCoordDict_bySymbol.keys() ):
		        print " QQ  this one is in the GAF file ... ", aTuple
		        if ( aTuple[1] < lowNum ):
		            lowNum = aTuple[1]
			    lowGene = aTuple[0]
	        print " QQ  --> going with this one: ", lowGene
	        newGene = lowGene
	        ## sys.exit(-1)

    return ( newGene )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def annotateFeatures ( dataD, geneInfoDict, synMapDict, geneCoordDict_bySymbol, 
		       geneCoordDict_byID, geneSymbol_byID, refGeneDict, cytoDict, 
                       nameChangeFlag ):

    print " "
    print " in annotateFeatures ... "

    ## the geneCoordDict_bySymbol has keys that are gene names, eg 'AAGAB', 'TP53', etc
    ## and the contents are the coordinates
    ## print len(geneCoordDict_bySymbol)

    ## similarly, the geneCoordDict_byID has keys that are gene IDs, eg '7157' or '8225', 
    ## etc and the contents are the coordinates

    ## the new addition here (19dec12) is the geneSymbol_byID which may be used to
    ## 'update' the gene symbol if it appears to be out of date ...
    
    ## and the feature matrix has thousands of features x hundreds of patients
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % ( numRow, numCol )
        ## print rowLabels[:5]
        ## print rowLabels[-5:]
    except:
	print " ERROR in annotateFeatures ??? bad data ??? "
	return ( dataD )

    ## first create a loop of all of the gene names (for GEXP features)
    curGeneSymbols = []
    dupList = []
    numDup = 0
    for iRow in range(numRow):
        curLabel = rowLabels[iRow]
	curType = curLabel[2:6]
	if ( curType == "GEXP" ):
	    curLabel = curLabel.upper()
	    tokenList = curLabel.split(':')
	    curGene = tokenList[2]
	    if ( curGene not in curGeneSymbols ):
	        curGeneSymbols += [ curGene ]
	    else:
	        print " how can this be ??? duplicate gene labels ??? ", curGene
                ## sys.exit(-1)
		numDup += 1
		dupList += [ curGene ]

    if ( numDup > 0 ):
        print " "
	print " WARNING !!! DUPLICATE gene symbols coming in !!! "
	print " "

    ## we want to loop over all of the feature names and attempt to add either
    ## gene names or coordinates as appropriate ...

    print " "
    print " starting loop over %d feature names ... " % numRow

    newRowLabels = []
    usedGeneSymbols = []

    addGene = {}
    addCyto = {}

    ## OUTER LOOP IS OVER ROWS ...
    for iRow in range(numRow):
	curLabel = rowLabels[iRow]

	print " "
	print " "
	print " QQ ", iRow, curLabel

	## we'll start by setting the newLabel to the curLabel ...
	newLabel = curLabel

	curType = curLabel[2:6].upper()

	## don't make any attempts at annotating CLIN or SAMP features ...
	if ( curType=="CLIN"  or  curType=="SAMP" ):
	    newRowLabels += [ newLabel ]
	    continue

	haveName = 0
	haveCoord = 0
	haveValidCoord = 0
	haveExtraName = 0

	tokenList = curLabel.split(':')
	if ( tokenList[2] != '' ): haveName = 1
	if ( tokenList[3] != '' ): haveCoord = 1
	if ( len(tokenList) > 7 ):
	    if ( tokenList[7] != '' ): haveExtraName = 1

        print " curType=<%s>  haveName=%d  haveCoord=%d  haveExtraName=%d " % \
                ( curType, haveName, haveCoord, haveExtraName )

	## ------------
	## IF haveCoord
	if ( haveCoord ):

	    if ( tokenList[3].startswith("ch") ):
	        try:
		    iStart = int ( tokenList[4] )
		except:
		    iStart = -1
	        if ( tokenList[5] != '' ):
	            try:
		        iStop = int ( tokenList[5] )
		    except:
		        iStop = -1
	        else:
	            iStop = iStart
	        if ( iStart>0 and iStop>0 ):
	            haveValidCoord = 1

	print " flags : ", haveName, haveCoord, haveValidCoord

	## if we have a name, check that it is the "correct" name,
	## and change it if necessary ... (note that most of 'chooseBestName'
	## is currently being bypassed 19dec12)
	##	--> actually on 07jan13 have been trying to reinstate ...

	## ------------
	## IF haveName
	if ( haveName ):
	    curGene = tokenList[2].upper()
	    curID = tokenList[7].upper()

	    newGene = chooseBestName ( curGene, curID, curType, geneInfoDict, synMapDict, geneCoordDict_bySymbol, geneCoordDict_byID )

            if ( nameChangeFlag == "YES" ):
	        if ( newGene != curGene ):
		    ## do NOT change to this "new" name if this name seems to already be in use ...
	            if ( (newGene in curGeneSymbols) or (newGene in usedGeneSymbols) or (newGene == "") ):
		        print " --> NOT changing name from <%s> to <%s> " % ( curGene, newGene )
		    else:
	                print " --> changing name from <%s> to <%s> " % ( curGene, newGene )
	                curGene = newGene

	    ## keep track of 'used' gene symbols ...
            if ( curGene not in usedGeneSymbols ): usedGeneSymbols += [ curGene ]

	gotItFlag = 0

	## ------------------------------------
	## IF haveName=TRUE and haveCoord=FALSE
	if ( haveName and not haveCoord ):

	    ## here we want to add coordinates based on a gene name
	    if ( curGene in geneCoordDict_bySymbol.keys() ):
	        print " found a gene ... ", curLabel, curGene, geneCoordDict_bySymbol[curGene]
		newLabel = annotateLabel ( curLabel, curGene, geneCoordDict_bySymbol[curGene] )
		print " addGene : ", tokenList, " --> ", newLabel
		gotItFlag = 1
		## keep track of how often we add a gene label ...
		if ( curType not in addGene.keys() ):
		    addGene[curType] = 1
		else:
		    addGene[curType] += 1

	    if ( not gotItFlag ):
		print "     this gene is not in GAF by gene symbol ??? ", curGene
		if ( haveExtraName ):
		    geneID = tokenList[7]
		    if ( geneID in geneCoordDict_byID.keys() ):
		        print " found by ID ... ", curLabel, curGene, geneID, geneCoordDict_byID[geneID]
			newGene = geneSymbol_byID[geneID][0]
			if ( newGene != curGene ):
			    print " --> changing name from <%s> to <%s> " % ( curGene, newGene )
			    curGene = newGene
			    ## sys.exit(-1)
			newLabel = annotateLabel ( curLabel, curGene, geneCoordDict_byID[geneID] )
			print " addGene : ", tokenList, " --> ", newLabel
			gotItFlag = 1
			if ( curType not in addGene.keys() ):
			    addGene[curType] = 1
			else:
			    addGene[curType] += 1

	    if ( not gotItFlag ):
		print "     this gene is not in GAF by gene ID (or no gene ID available) ??? ", tokenList
		if ( curGene in refGeneDict.keys() ):
		    print "         finally, found in refGene ... ", curLabel, curGene, refGeneDict[curGene]
		    newLabel = annotateLabel ( curLabel, curGene, refGeneDict[curGene] )
		    print " addGene : ", tokenList, " --> ", newLabel
		    ## keep track of how often we add a gene label ...
		    if ( curType not in addGene.keys() ):
		        addGene[curType] = 1
		    else:
		        addGene[curType] += 1
		else:
		    print "         and also not in refGene ... "

	## -----------------------------------------
	## IF haveName=FALSE and haveValidCoord=TRUE
	elif ( not haveName and haveValidCoord ):

	    ## here we want to add either a single gene name based on valid 
	    ## coordinates, or else we add a cytoband label ...
	    ## print tokenList
	    geneList = overlap ( curLabel, geneCoordDict_bySymbol )
	    ## print geneList

	    if ( len(geneList) != 1 ):

		## if there are several (or zero) genes in this segment, then we 
		## annotate based on cytoband instead ...
		## print curLabel
		## print geneList
		curCytoband = getCytobandLabel ( curLabel, cytoDict )
		newLabel = curLabel[:7] + curCytoband + curLabel[7:]
		print " addCyto : ", tokenList, " --> ", newLabel
		## print newLabel
		## keep track of how often we add a gene label ...
		if ( curType not in addCyto.keys() ):
		    addCyto[curType] = 1
		else:
		    addCyto[curType] += 1

	    else:

		## if there is just one gene, then use that
		if ( hasSpecialChar(geneList[0]) ):
		    print " need to fix this gene name : ", geneList[0]
		    sys.exit(-1)
	        newLabel = curLabel[:7] + geneList[0] + curLabel[7:]
		print " addGene : ", tokenList, " --> ", newLabel
		## print newLabel
		## keep track of how often we add a gene label ...
		if ( curType not in addGene.keys() ):
		    addGene[curType] = 1
		else:
		    addGene[curType] += 1

	newRowLabels += [ newLabel ]

	## END OF BLOCK of SEVERAL IF STATEMENTS 
	## -------------------------------------

    ## END OF OUTER LOOP OVER ROWS ...

    print " "
    print " "

    ## before we assign the new row labels, make sure that they
    ## are unique !!
    numIdent = 0
    for ii in range(len(newRowLabels)):
        for jj in range(ii+1,len(newRowLabels)):
	    if ( newRowLabels[ii].upper() == newRowLabels[jj].upper() ):
	        print " WARNING !!! identical labels ??? tacking on dup "
		print ii, newRowLabels[ii]
		print jj, newRowLabels[jj]
		if ( newRowLabels[jj][-1] == ":" ):
		    newRowLabels[jj] += "dup"
		else:
		    newRowLabels[jj] += "_dup"
		print "     --> ", jj, newRowLabels[jj]
		numIdent += 1
    if ( 0 ):
        if ( numIdent > 0 ):
            sys.exit(-1)

    print " "
    print " "

    if ( len(newRowLabels) == len(rowLabels) ):
        print " --> seem to have all the new labels ... ", len(newRowLabels), len(rowLabels)
	print "     addGene : ", addGene
	print "     addCyto : ", addCyto
        ## assign the new labels ...
        dataD['rowLabels'] = newRowLabels
        return ( dataD )

    else:
	print "     ERROR ??? wrong number of labels ??? "
	print len(newRowLabels), len(rowLabels)
	sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if ( 1 ):
        if ( len(sys.argv) >= 4 ):
	    inFile = sys.argv[1]
	    build = sys.argv[2]
	    outFile = sys.argv[3]
            if ( len(sys.argv) >= 5 ):
                nameChangeFlag = sys.argv[4].upper()
            else:
                nameChangeFlag = "YES"
	else:
	    print " "
	    print " Usage: %s <input TSV file> <hg18 or hg19> <output TSV file> [nameChangeFlag=NO/YES] "
            print "        note that nameChangeFlag will default to YES "
	    print " "
	    sys.exit(-1)
	    tumorType = 'gbm'

    ## default the nameChangeFlag to YES ...
    if ( nameChangeFlag == "Y" ):
        nameChangeFlag = "YES"
    if ( nameChangeFlag != "YES" ):
        nameChangeFlag = "NO"

    ## and get the coordinates for these genes ...
    if ( build == 'hg18' ):
        gafFilename = "/titan/cancerregulome3/TCGA/GAF/Feb2011/GAF.hg18.Feb2011/GAF_bundle/outputs/TCGA.hg18.Feb2011.gaf"
	cybFilename = "/titan/cancerregulome3/TCGA/hg18/cytoBand.hg18.txt"
    elif ( build == 'hg19' ):
	gafFilename = "/titan/cancerregulome3/TCGA/GAF/GAF3.0/all.gaf"
	refGeneFilename = "/titan/cancerregulome3/TCGA/hg19/refGene.txt"
	cybFilename = "/titan/cancerregulome3/TCGA/hg19/cytoBand.hg19.txt"
    else:
	print " ERROR ... genome build must be either hg18 or hg19 "

    infFilename = "/titan/cancerregulome3/TCGA/ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info"

    print " "
    print " Running : %s %s %s %s " % ( sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3] )
    print "           %s " % gafFilename
    print "           %s " % refGeneFilename
    print "           %s " % cybFilename
    print "           %s " % infFilename
    print " "
    print " "

    ## read in the input feature matrix first, just in case there
    ## actually isn't one yet available ...
    print " --> calling tsvIO.readTSV ... "
    testD = tsvIO.readTSV ( inFile )
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
	if ( len(testD['rowLabels'])==0  or  len(testD['colLabels'])==0 ):
	    print " EXITING ... no data "
	    sys.exit(-1)
    except:
	print " --> invalid / missing input feature matrix "
	sys.exit(-1)

    ## read in the gene_info file ...
    ## this was turned off ... looking into turning it back on (1/7/13)
    if ( 1 ):
        print " --> calling readGeneInfoFile ... "
        ( geneInfoDict, synMapDict ) = readGeneInfoFile ( infFilename )
    else:
        geneInfoDict = {}
	synMapDict = {}

    ## then read in the GAF file ...
    print " --> calling readGAF ... "
    ( geneCoordDict_bySymbol, geneCoordDict_byID, geneSymbol_byID ) = readGAF ( gafFilename )

    ## also the refGene file ...
    print " --> calling readRefGeneFile ... "
    refGeneDict = readRefGeneFile ( refGeneFilename )

    ## then read in the cytoband file ...
    print " --> calling readCytobandFile ... "
    cytoDict = readCytobandFile ( cybFilename )

    ## and annotate the features
    print " --> calling annotateFeatures ... "
    annotD = annotateFeatures ( testD, geneInfoDict, synMapDict, geneCoordDict_bySymbol, geneCoordDict_byID, geneSymbol_byID, refGeneDict, cytoDict, nameChangeFlag )

    ## check that the feature names are still unique ...
    print " --> verify that the feature names are unique ... "
    newLabels = tsvIO.uniqueFeatureLabels ( annotD['rowLabels'], annotD['dataMatrix'] )
    for ii in range(len(newLabels)):
        if ( not ( newLabels[ii] == annotD['rowLabels'][ii] ) ):
	    print " "
	    print " BAILING !!! ", newLabels[ii], annotD['rowLabels'][ii]
	    print " "
	    sys.exit(-1)

    ## and write the matrix back out
    print " --> calling tsvIO.writeTSV_dataMatrix ... "
    tsvIO.writeTSV_dataMatrix ( annotD, 0, 0, outFile )

    print " "
    print " DONE "
    print " "
    
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
