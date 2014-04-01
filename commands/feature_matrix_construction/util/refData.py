# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import sys

# these are my local ones
import chrArms
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readGeneInfoFile(geneInfoFilename):

    geneInfoDict = {}
    synMapDict = {}

    try:
        fh = file(infFilename, 'r')
    except:
        print " ERROR opening gene_info file <%s> " % infFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()
        if (aLine.startswith("#")):
            continue
        if (not aLine.startswith("9606")):
            continue

        tokenList = aLine.split('\t')

        tax_id = tokenList[0]
        if (tax_id != "9606"):
            continue

        geneID = int(tokenList[1])
        symbol = tokenList[2]
        locusTag = tokenList[3]
        synonyms = tokenList[4]

        if (synonyms == "-"):
            continue

        if (symbol not in geneInfoDict):
            geneInfoDict[symbol] = []

        synList = synonyms.split('|')
        for aSyn in synList:
            if (aSyn not in geneInfoDict[symbol]):
                geneInfoDict[symbol] += [aSyn]

            if (aSyn not in synMapDict):
                synMapDict[aSyn] = [(symbol, geneID)]
            else:
                synMapDict[aSyn] += [(symbol, geneID)]

        # number of symbols with synonyms was 22558

    print " "
    print " --> finished reading gene_info file <%s> " % geneInfoFilename
    print "         %6d unique keys in geneInfoDict " % len(geneInfoDict)
    print "         %6d unique keys in synMapDict " % len(synMapDict)

    if (0):
        print " "
        print " synonyms with more than one assigned symbol ... ??? "
        for aSyn in synMapDict:
            if (len(synMapDict[aSyn]) > 1):
                print aSyn, synMapDict[aSyn]
        print " "

    return (geneInfoDict, synMapDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readCytobandFile(cybFilename):

    cytoDict = {}

    try:
        fh = file(cybFilename, 'r')
    except:
        print " ERROR opening cytoband file <%s> " % cybFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')

        chrName = tokenList[0].lower()
        bndName = tokenList[3]
        iStart = int(tokenList[1])
        iStop = int(tokenList[2])

        if (chrName not in cytoDict):
            cytoDict[chrName] = []
        cytoDict[chrName] += [(bndName, iStart, iStop)]

    fh.close()

    if (0):
        ## this is just a block that will print stuff out and
        ## exit in case we need/want that briefly
        allNames = cytoDict.keys()
        allNames.sort()
        for aName in allNames:
            maxP = -1
            maxQ = -1
            for aTuple in cytoDict[aName]:
                if (aTuple[0].startswith("p")):
                    if (maxP < aTuple[2]):
                        maxP = aTuple[2]
                elif (aTuple[0].startswith("q")):
                    if (maxQ < aTuple[2]):
                        maxQ = aTuple[2]
            # print aName, maxP, maxQ
            print "arms_hg['%sp'] = ( %9d, %9d )" % (aName[3:], 0, maxP)
            print "arms_hg['%sq'] = ( %9d, %9d )" % (aName[3:], maxP, maxQ)
        sys.exit(-1)

    return (cytoDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readRefGeneFile(refGeneFilename):

    refGeneDict = {}

    try:
        fh = file(refGeneFilename, 'r')
    except:
        print " ERROR opening refGene file <%s> " % refGeneFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')

        # this file has 16 columns
        # [0]  - a numeric index of some sort
        # [1]  - NM_*
        # [2]  - chromosome (eg 'chr17')
        # [3]  - strand (eg '-')
        # [4]  - start position (eg 7571719)
        # [5]  - stop position (eg 7590868)
        # [6]  - another start of some sort
        # [7]  - another stop
        # [8]  - # of exons (?)
        # [9]  - comma-delimited positions
        # [10] - comma-delimited positions
        # [11] - ?
        # [12] - gene symbol (eg 'TP53')
        # [13] - ?
        # [14] - ?
        # [15] - comma-delimited integers

        geneName = tokenList[12]

        # chr17:7565097-7590863:-
        coordString = tokenList[2] + ':' + tokenList[4] + '-' + tokenList[5] + ':' + tokenList[3]

        # if we already have this geneName, just make sure that the
        # coordinates cover the largest possible extent ...
        if (geneName in refGeneDict):

            oldString = refGeneDict[geneName]
            if (oldString == coordString):
                continue

            oldTokens = oldString.split(':')

            if (oldTokens[0] != tokenList[2]):
                continue

            ii = oldTokens[1].find('-')
            oldStart = int(oldTokens[1][:ii])
            oldStop = int(oldTokens[1][ii + 1:])

            curStart = int(tokenList[4])
            curStop = int(tokenList[5])

            updateFlag = 0
            newStart = oldStart
            newStop = oldStop

            if (curStart < oldStart):
                updateFlag = 1
                newStart = curStart
            if (curStop > oldStop):
                updateFlag = 1
                newStop = curStop

            coordString = oldTokens[0] + ':' + \
                str(newStart) + '-' + str(newStop) + ':' + oldTokens[2]
            refGeneDict[geneName] = coordString

            # print "     --> updated <%s> to <%s> " % ( oldString, coordString
            # )

        else:
            refGeneDict[geneName] = coordString

    fh.close()

    print " in readRefGeneFile ... "
    print "     length of refGeneDict w/ coords ..... ", len(refGeneDict), len(refGeneDict)

    return (refGeneDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makeAttributeDict ( aToken ):

    attrDict = {}
    if ( len(aToken) == 0 ): return ( attrDict )

    attrList = aToken.split(';')
    for a in attrList:
        b = a.strip()
        c = b.split(' ')
        try:
            if ( c[1][ 0] == '"' ): c[1] = c[1][1:]
            if ( c[1][-1] == '"' ): c[1] = c[1][:-1]
            attrDict[c[0]] = c[1]
        except:
            doNothing = 1

    return ( attrDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function is based on the readGAF function below, with edits made
# as needed to parse the Gencode GTF format


def readGencode(gencodeFilename):

    Gencode_geneCoordDict_bySymbol = {}
    Gencode_geneCoordDict_byID = {}
    Gencode_geneSymbol_byID = {}

    try:
        fh = file(gencodeFilename, 'r')
    except:
        print " ERROR opening GENCODE file <%s> " % gencodeFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()

        if (aLine.startswith("#")):
            continue
        tokenList = aLine.split('\t')

        if (len(tokenList) < 9):
            continue

        ## tokenList[0] 'chr17'
        ## tokenList[1] 'HAVANA'
        ## tokenList[2] 'gene'
        ## tokenList[3] '7565097'
        ## tokenList[4] '7590856'
        ## tokenList[5] '.'
        ## tokenList[6] '-'
        ## tokenList[7] '.'
        ## tokenList[8] 'gene_id "ENSG00000141510.11"; transcript_id "ENSG00000141510.11"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "TP53"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "TP53"; level 2; havana_gene "OTTHUMG00000162125.4";'

        attrDict = makeAttributeDict ( tokenList[8] )

        try:
            geneName = attrDict['gene_name']
            geneID = attrDict['gene_id']
            ## create the coordToken, eg: chr17:7565097-7590856:-
            coordToken = tokenList[0] + ':' + tokenList[3] + '-' + tokenList[4] + ':' + tokenList[6]
        except:
            continue

        # print " ready to add : ", geneName, geneID, coordToken

        if (len(geneName) > 1):
            if (geneName in Gencode_geneCoordDict_bySymbol):
                doNothing = 1
            else:
                Gencode_geneCoordDict_bySymbol[geneName] = coordToken

        if (geneID != '?'):
            if (geneID in Gencode_geneCoordDict_byID):
                doNothing = 1
            else:
                Gencode_geneCoordDict_byID[geneID] = coordToken

        # also create the Gencode_geneSymbol_byID dict ...
        if (geneID != '?'):
            if (geneID in Gencode_geneSymbol_byID):
                if (geneName not in Gencode_geneSymbol_byID[geneID]):
                    print " this should never happen should it ??? ", geneID, geneName, Gencode_geneSymbol_byID[geneID]
                    Gencode_geneSymbol_byID[geneID] += [geneName]

                    # HACK
                    if (geneID == "378108"):
                        Gencode_geneSymbol_byID[geneID] = ["TRIM74"]
            else:
                Gencode_geneSymbol_byID[geneID] = [geneName]

    fh.close()

    print " in readGencode ... "
    print "     length of Gencode_geneCoordDict_bySymbol w/ coords ..... ", len(Gencode_geneCoordDict_bySymbol), len(Gencode_geneCoordDict_bySymbol)
    print "     length of Gencode_geneCoordDict_byID     w/ coords ..... ", len(Gencode_geneCoordDict_byID), len(Gencode_geneCoordDict_byID)
    print "     length of Gencode_geneSymbol_byID  ..................... ", len(Gencode_geneSymbol_byID)

    print " "
    print " sanity-checking Gencode_geneSymbol_byID dictionary ... "
    for geneID in Gencode_geneSymbol_byID:
        if (len(Gencode_geneSymbol_byID[geneID]) > 1):
            print geneID, Gencode_geneSymbol_byID[geneID]
    print " "
    print " "

    return (Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readGAF(gafFilename):

    GAF_geneCoordDict_bySymbol = {}
    GAF_geneCoordDict_byID = {}
    GAF_geneSymbol_byID = {}

    try:
        fh = file(gafFilename, 'r')
    except:
        print " ERROR opening GAF file <%s> " % gafFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()

        if (aLine.startswith("#")):
            continue
        tokenList = aLine.split('\t')
        # print len(tokenList), tokenList

        if (len(tokenList) < 17):
            continue

        ## print " "
        ## print tokenList

        # print tokenList[16]
        # print tokenList[2]

        if (not tokenList[16].startswith("chr")):
            # print " f17 does not start with chr ??? "
            # print tokenList[16]
            if (tokenList[16].find("chr") >= 0):
                # print "     but there is some chr info somewhere ??? "
                # print tokenList[16]
                doNothing = 1
            else:
                # print " --> SKIPPING "
                continue

        # column 3 contains one of the following strings:
        ##	AffySNP, componentExon, compositeExon, gene, junction, MAprobe, miRNA, pre-miRNA, transcript
        ## print tokenList[2]
        if (tokenList[2].upper() == "AFFYSNP"): continue
        if (tokenList[2].upper() == "COMPONENTEXON"): continue
        if (tokenList[2].upper() == "COMPOSITEEXON"): continue
        if (tokenList[2].upper() == "JUNCTION"): continue
        if (tokenList[2].upper() == "MAPROBE"): continue
        if (tokenList[2].upper() == "TRANSCRIPT"): continue

        geneToken = tokenList[1]
        geneTokenList = geneToken.split('|')
        geneName = geneTokenList[0]
        if (len(geneTokenList) == 2):
            geneID = geneTokenList[1]
            if ( geneID.startswith("MIMAT") ):
                if ( geneID[-2] == "_" ): geneID = geneID[:-2]
        else:
            geneID = '?'

        ## for a miRNA, we are getting at this point:
        ##      geneToken = hsa-let-7a-2-3p|MIMAT0010195_1
        ##      geneTokenList = ['hsa-let-7a-2-3p', 'MIMAT0010195_1']
        ##      geneName = hsa-let-7a-2-3p
        ##      geneID = MIMAT0010195_1
        # print geneToken, geneTokenList, geneName, geneID

        if (0):
            # we're skipping entries of the form ?|791120 or T|6862
            if (geneName == '?'):
                continue
            if (len(geneName) == 1):
                continue

        # what if there are multiple coordinates???
        coordToken = tokenList[16]
        coordTokenList = coordToken.split(';')
        ## print coordToken, coordTokenList
        if (len(coordTokenList) > 1):
            # print " need to do something about this ... "
            # print coordTokenList
            mergeCoord = mergeCoordinates(coordTokenList)
            if (mergeCoord == ""):
                # print " --> failed to get coordinates ... skipping ... "
                continue
            coordToken = mergeCoord
            # print " --> changed to: ", coordToken

        # print " ready to add : ", geneName, geneID, coordToken

        if (len(geneName) > 1):
            if (geneName in GAF_geneCoordDict_bySymbol):
                doNothing = 1
            else:
                GAF_geneCoordDict_bySymbol[geneName] = coordToken
                # print " adding ", geneName, coordToken

        if (geneID != '?'):
            if (geneID in GAF_geneCoordDict_byID):
                doNothing = 1
            else:
                GAF_geneCoordDict_byID[geneID] = coordToken
                # print " adding ", geneID, coordToken

        # 19dec12 : now also creating the GAF_geneSymbol_byID dict ...
        if (geneID != '?'):
            if (geneID in GAF_geneSymbol_byID):
                if (geneName not in GAF_geneSymbol_byID[geneID]):
                    print " this should never happen should it ??? ", geneID, geneName, GAF_geneSymbol_byID[geneID]
                    GAF_geneSymbol_byID[geneID] += [geneName]

                    # HACK
                    if (geneID == "378108"):
                        GAF_geneSymbol_byID[geneID] = ["TRIM74"]
            else:
                GAF_geneSymbol_byID[geneID] = [geneName]

            # print geneID, geneName, GAF_geneSymbol_byID[geneID]

    fh.close()

    print " in readGAF ... "
    print "     length of GAF_geneCoordDict_bySymbol w/ coords ..... ", len(GAF_geneCoordDict_bySymbol), len(GAF_geneCoordDict_bySymbol)
    print "     length of GAF_geneCoordDict_byID     w/ coords ..... ", len(GAF_geneCoordDict_byID), len(GAF_geneCoordDict_byID)
    print "     length of GAF_geneSymbol_byID  ..................... ", len(GAF_geneSymbol_byID)

    print " "
    print " sanity-checking GAF_geneSymbol_byID dictionary ... "
    for geneID in GAF_geneSymbol_byID:
        if (len(GAF_geneSymbol_byID[geneID]) > 1):
            print geneID, GAF_geneSymbol_byID[geneID]
    print " "
    print " "

    return (GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def mergeCoordinates(coordTokenList):

    # print " in mergeCoorodinates ... "
    # print coordTokenList

    # sometimes we seem to have a '?' instead of a proper coordinate string
    # so get rid of that if it shows up ...
    tmpList = []
    for ii in range(len(coordTokenList)):
        if (coordTokenList[ii].startswith("chr")):
            tmpList += [coordTokenList[ii]]
    coordTokenList = tmpList
    # print coordTokenList
    if (len(coordTokenList) == 0):
        return ("")

    # and now we can work with the corrected list ...
    for ii in range(len(coordTokenList)):

        posInfo = parseCoordinates(coordTokenList[ii])
        # print posInfo

        # make sure that the chrName is consistent ... strand also
        if (ii == 0):

            # grab all of the information for the very first coordinate range
            # and keep it  ...
            chrName = posInfo[0]
            iStart = posInfo[1]
            iStop = posInfo[2]
            aStrand = posInfo[3]

            # meanwhile, if we are merging multiple coordinate ranges
            # that will be done using jStart and jStop
            jStart = iStart
            jStop = iStop

        else:

            if (chrName != posInfo[0]):
                # print " multiple chromosomes in mergeCoordinates ... "
                # print " --> keeping only the first "
                # print coordTokenList
                mergeCoord = chrName + ':' + \
                    str(iStart) + '-' + str(iStop) + ':' + aStrand
                return (mergeCoord)

            if (aStrand != posInfo[3]):
                # print " WARNING ... different strands ... but not halting ... "
                # print coordTokenList
                doNothing = 1

        jStart = min(jStart, posInfo[1])
        jStop = max(jStop, posInfo[2])

    mergeCoord = chrName + ':' + str(jStart) + '-' + str(jStop) + ':' + aStrand

    return (mergeCoord)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseCoordinates(coordInfo):

    posInfo = []
    i1 = coordInfo.find(':')
    i2 = coordInfo.find('-', i1)
    i3 = coordInfo.find(':', i2)
    # print coordInfo[:i1], coordInfo[i1+1:i2], coordInfo[i2+1:i3],
    # coordInfo[i3+1:]
    try:
        posInfo = [coordInfo[:i1],
                   int(coordInfo[i1 + 1:i2]), int(coordInfo[i2 + 1:i3]), coordInfo[i3 + 1:]]
    except:
        print coordInfo[:i1], coordInfo[i1 + 1:i2], coordInfo[i2 + 1:i3], coordInfo[i3 + 1:]
        sys.exit(-1)

    return (posInfo)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
