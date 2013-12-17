#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import sys

# these are my local ones
import chrArms
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

global fhOut

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
        symbol = tokenList[2].upper()
        locusTag = tokenList[3]
        synonyms = tokenList[4].upper()

        if (synonyms == "-"):
            continue

        symbol = symbol.upper()
        if (symbol not in geneInfoDict.keys()):
            geneInfoDict[symbol] = []

        synList = synonyms.split('|')
        for aSyn in synList:
            aSyn = aSyn.upper()
            if (aSyn not in geneInfoDict[symbol]):
                geneInfoDict[symbol] += [aSyn]

            if (aSyn not in synMapDict.keys()):
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
        for aSyn in synMapDict.keys():
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

        if (chrName not in cytoDict.keys()):
            cytoDict[chrName] = []
        cytoDict[chrName] += [(bndName, iStart, iStop)]

    fh.close()

    if (0):
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

        # CHR17:7565097-7590863:-
        coordString = tokenList[
            2].upper() + ':' + tokenList[4] + '-' + tokenList[5] + ':' + tokenList[3]

        # if we already have this geneName, just make sure that the
        # coordinates cover the largest possible extent ...
        if (geneName in refGeneDict.keys()):

            oldString = refGeneDict[geneName]
            if (oldString == coordString):
                continue

            oldTokens = oldString.split(':')

            if (oldTokens[0] != tokenList[2].upper()):
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
    print "     length of refGeneDict w/ coords ..... ", len(refGeneDict), len(refGeneDict.keys())

    return (refGeneDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readGAF(gafFilename):

    geneCoordDict_bySymbol = {}
    geneCoordDict_byID = {}

    try:
        fh = file(gafFilename, 'r')
    except:
        print " ERROR opening GAF file <%s> " % gafFilename
        sys.exit(-1)

    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()

        if (aLine.startswith("#")):
            continue
        tokenList = aLine.split('\t')

        if (len(tokenList) < 17):
            continue

        if (not tokenList[16].startswith("CHR")):
            # print " f17 does not start with CHR ??? "
            # print tokenList[16]
            if (tokenList[16].find("CHR") >= 0):
                # print "     but there is some CHR info somewhere ??? "
                # print tokenList[16]
                doNothing = 1
            else:
                # print " --> SKIPPING "
                continue

        # column 3 contains one of the following strings:
        ##      AffySNP, componentExon, compositeExon, gene, junction, MAprobe, miRNA, pre-miRNA, transcript
        if (tokenList[2] == "AFFYSNP"):
            continue
        if (tokenList[2] == "COMPONENTEXON"):
            continue
        if (tokenList[2] == "COMPOSITEEXON"):
            continue
        if (tokenList[2] == "JUNCTION"):
            continue
        if (tokenList[2] == "MAPROBE"):
            continue
        if (tokenList[2] == "TRANSCRIPT"):
            continue

        geneToken = tokenList[1]
        geneTokenList = geneToken.split('|')
        geneName = geneTokenList[0].upper()
        if (len(geneTokenList) == 2):
            geneID = geneTokenList[1]
        else:
            geneID = '?'

        if (0):
            # we're skipping entries of the form ?|791120 or T|6862
            if (geneName == '?'):
                continue
            if (len(geneName) == 1):
                continue

        # what if there are multiple coordinates???
        coordToken = tokenList[16]
        coordTokenList = coordToken.split(';')
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
            if (geneName in geneCoordDict_bySymbol.keys()):
                doNothing = 1
            else:
                geneCoordDict_bySymbol[geneName] = coordToken

        if (geneID != '?'):
            if (geneID in geneCoordDict_byID.keys()):
                doNothing = 1
            else:
                geneCoordDict_byID[geneID] = coordToken

    fh.close()

    print " in readGAF ... "
    print "     length of geneCoordDict_bySymbol w/ coords ..... ", len(geneCoordDict_bySymbol), len(geneCoordDict_bySymbol.keys())
    print "     length of geneCoordDict_byID     w/ coords ..... ", len(geneCoordDict_byID), len(geneCoordDict_byID.keys())
    print " "

    return (geneCoordDict_bySymbol, geneCoordDict_byID)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def mergeCoordinates(coordTokenList):

    # print " in mergeCoorodinates ... "
    # print coordTokenList

    # sometimes we seem to have a '?' instead of a proper coordinate string
    # so get rid of that if it shows up ...
    tmpList = []
    for ii in range(len(coordTokenList)):
        if (coordTokenList[ii].startswith("CHR")):
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
# this function looks for the gene or genes that overlap the segment defined
# by the input 'curRowLabel' coordinates


def overlap(curRowLabel, geneCoordDict_bySymbol, extra_bp):

    tokenList = curRowLabel.split(':')
    geneList = []

    if (tokenList[3] != ''):

        # first try to parse out genomic coordinates from
        # the current row label ... it is possible that
        # the row label does not have coordinates
        try:
            chrName = tokenList[3].upper()
            chrStart = int(tokenList[4])
            if (tokenList[5] != ''):
                chrStop = int(tokenList[5])
            else:
                chrStop = chrStart
            # print chrName, chrStart, chrStop
        except:
            return ([])

        chrStart -= extra_bp
        chrStop += extra_bp

        # if we get here, then we have coordinates so we now
        # loop over the genes in our geneCoordDict_bySymbol and look for
        # any that overlap ...
        for aGene in geneCoordDict_bySymbol.keys():

            # if this gene is not even on the same chromosome we're done ...
            if (not geneCoordDict_bySymbol[aGene].startswith(chrName + ':')):
                continue

            # but if it is, then we need to check start/stop
            posInfo = parseCoordinates(geneCoordDict_bySymbol[aGene])
            if (chrStop < posInfo[1]):
                continue
            if (chrStart > posInfo[2]):
                continue
            # print posInfo

            # there seem to be some "bad" gene names ???
            if (aGene == '?'):
                continue

            if (len(aGene) == 1):
                print " how is this happening ??? "
                print curRowLabel, aGene, geneCoordDict_bySymbol[aGene]
                sys.exit(-1)

            geneList += [aGene]

        if (len(geneList) > 0):
            if (0):
                if (len(geneList) > 1):
                    print " got multiple genes ... ", geneList, tokenList
            return (geneList)
        else:
            # print " in overlap ... nada? ", curRowLabel
            return ([])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def mapFeatures2Genes(dataD, geneInfoDict, synMapDict, geneCoordDict_bySymbol,
                      geneCoordDict_byID, refGeneDict, cytoDict, extra_bp):

    print " "
    print " in mapFeatures2Genes ... "

    # the geneCoordDict_bySymbol has keys that are gene names, eg 'AAGAB', 'TP53', etc
    # and the contents are the coordinates
    # print len(geneCoordDict_bySymbol)

    # similarly, the geneCoordDict_byID has keys that are gene IDs, eg '7157' or '8225',
    # etc and the contents are the coordinates

    # and the feature matrix has thousands of features x hundreds of patients
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in mapFeatures2Genes ??? bad data ??? "
        return (dataD)

    # outer loop over feature names ...
    print " "
    print " starting loop over %d feature names ... " % numRow

    # OUTER LOOP IS OVER ROWS ...
    for iRow in range(numRow):
        curLabel = rowLabels[iRow]

        if (iRow % 100 == 0):
            print " QQ ", iRow, curLabel

        # grab current feature type
        curType = curLabel[2:6].upper()

        # don't make any attempts at annotating CLIN or SAMP features ...
        if (curType == "CLIN" or curType == "SAMP"):
            continue

        haveName = 0
        haveCoord = 0
        haveValidCoord = 0

        tokenList = curLabel.split(':')
        if (tokenList[2] != ''):
            haveName = 1
        if (tokenList[3] != ''):
            haveCoord = 1

        # print " curType=<%s>  haveName=%d  haveCoord=%d " % ( curType,
        # haveName, haveCoord )

        # ------------
        # IF haveCoord
        if (haveCoord):

            if (tokenList[3].startswith("ch")):
                try:
                    iStart = int(tokenList[4])
                except:
                    iStart = -1
                if (tokenList[5] != ''):
                    try:
                        iStop = int(tokenList[5])
                    except:
                        iStop = -1
                else:
                    iStop = iStart
                if (iStart > 0 and iStop > 0):
                    haveValidCoord = 1

        # print " flags : ", haveName, haveCoord, haveValidCoord

        if (haveValidCoord):

            # here we want to add either a single gene name based on valid
            # coordinates, or else we add a cytoband label ...
            # print tokenList
            geneList = overlap(curLabel, geneCoordDict_bySymbol, extra_bp)
            # print geneList
            outLine = curLabel + "\t" + str(len(geneList)) + "\t"
            for aGene in geneList:
                outLine += aGene + ","
            if (outLine[-1] == ','):
                outLine = outLine[:-1]
            fhOut.write("%s\n" % outLine)

    # END OF OUTER LOOP OVER ROWS ...

    print " "
    print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 3):
            inFile = sys.argv[1]
            mapFile = sys.argv[2]
        elif (len(sys.argv) == 4):
            inFile = sys.argv[1]
            mapFile = sys.argv[2]
            extra_bp = int(sys.argv[3])
        else:
            print " "
            print " Usage: %s <input TSV file> <output mapping file> [extra bp] " % sys.argv[0]
            print sys.argv
            print len(sys.argv)
            print " "
            sys.exit(-1)

    # open the output file
    global fhOut
    fhOut = file(mapFile, 'w')

    # and get the coordinates for these genes ...
    gafFilename = "/titan/cancerregulome3/TCGA/GAF/GAF3.0/all.gaf"
    refGeneFilename = "/titan/cancerregulome3/TCGA/hg19/refGene.txt"
    cybFilename = "/titan/cancerregulome3/TCGA/hg19/cytoBand.hg19.txt"

    infFilename = "/titan/cancerregulome3/TCGA/ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info"

    print " "
    print " Running : %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print "           %s " % gafFilename
    print "           %s " % refGeneFilename
    print "           %s " % cybFilename
    print "           %s " % infFilename
    print " "
    print " "

    # read in the input feature matrix first, just in case there
    # actually isn't one yet available ...
    print " --> calling tsvIO.readTSV ... "
    testD = tsvIO.readTSV(inFile)
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
        if (len(testD['rowLabels']) == 0 or len(testD['colLabels']) == 0):
            print " EXITING ... no data "
            sys.exit(-1)
    except:
        print " --> invalid / missing input feature matrix "
        sys.exit(-1)

    # read in the gene_info file ...
    # this was turned off ... looking into turning it back on (1/7/13)
    if (1):
        print " --> calling readGeneInfoFile ... "
        (geneInfoDict, synMapDict) = readGeneInfoFile(infFilename)
    else:
        geneInfoDict = {}
        synMapDict = {}

    # then read in the GAF file ...
    print " --> calling readGAF ... "
    (geneCoordDict_bySymbol, geneCoordDict_byID) = readGAF(gafFilename)

    # also the refGene file ...
    print " --> calling readRefGeneFile ... "
    refGeneDict = readRefGeneFile(refGeneFilename)

    # then read in the cytoband file ...
    print " --> calling readCytobandFile ... "
    cytoDict = readCytobandFile(cybFilename)

    # and map the features to genes
    print " --> calling mapFeatures2Genes ... "
    annotD = mapFeatures2Genes(
        testD, geneInfoDict, synMapDict, geneCoordDict_bySymbol,
        geneCoordDict_byID, refGeneDict, cytoDict, extra_bp)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
