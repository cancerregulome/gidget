#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import sys

# these are my local ones
from env import gidgetConfigVars
import chrArms
import refData
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

global fhOut

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def geneSymbolLooksOK ( aGene ):

    if ( len(aGene) < 2 ): return ( 0 )
    try:
        # if the gene is simply an integer, skip it ...
        iG = int(aGene)
        return ( 0 )
    except:
        doNothing = 1

    if ( aGene.startswith("CTB-") ): return ( 0 )
    if ( aGene.startswith("CTD-") ): return ( 0 )
    if ( aGene.startswith("RP1-") ): return ( 0 )
    if ( aGene.startswith("RP3-") ): return ( 0 )
    if ( aGene.startswith("RP4-") ): return ( 0 )
    if ( aGene.startswith("RP5-") ): return ( 0 )
    if ( aGene.startswith("RP11-") ): return ( 0 )
    if ( aGene.startswith("RP13-") ): return ( 0 )
    if ( aGene.startswith("RNA5") ): return ( 0 )
    if ( aGene.startswith("RNU1-") ): return ( 0 )
    if ( aGene.startswith("RNU6-") ): return ( 0 )
    if ( aGene.startswith("RNU7-") ): return ( 0 )
    if ( aGene.startswith("LINC") ): return ( 0 )
    if ( aGene.startswith("MIMAT") ): return ( 0 )

    tokenList = aGene.split('.')
    try:
        iG = int(tokenList[0])
        return ( 0 )
    except:
        try:
            iG = int(tokenList[0][1:])
            return ( 0 )
        except:
            try:
                iG = int(tokenList[0][2:])
                return ( 0 )
            except:
                doNothing = 1

    tokenList = aGene.split('_')
    try:
        iG = int(tokenList[0])
        return ( 0 )
    except:
        try:
            iG = int(tokenList[0][1:])
            return ( 0 )
        except:
            try:
                iG = int(tokenList[0][2:])
                return ( 0 )
            except:
                doNothing = 1

    # print " geneSymbolLooksOK %s " % aGene
    return ( 1 )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function looks for the gene or genes that overlap the segment defined
# by the input 'curRowLabel' coordinates


def overlap ( curRowLabel, Gencode_geneCoordDict_bySymbol, \
              GAF_geneCoordDict_bySymbol, extra_bp):

    # print " in function overlap ", curRowLabel

    tokenList = curRowLabel.split(':')
    geneList = []

    if (tokenList[3] != ''):

        # first try to parse out genomic coordinates from
        # the current row label ... it is possible that
        # the row label does not have coordinates
        try:
            chrName = tokenList[3]
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

        # first for Gencode ...
        # print " looking thru Gencode info ... "
        for aGene in Gencode_geneCoordDict_bySymbol.keys():

            # if this gene is not even on the same chromosome we're done ...
            if (not Gencode_geneCoordDict_bySymbol[aGene].startswith(chrName + ':')):
                continue

            # but if it is, then we need to check start/stop
            posInfo = refData.parseCoordinates(Gencode_geneCoordDict_bySymbol[aGene])
            if (chrStop  < posInfo[1]): continue
            if (chrStart > posInfo[2]): continue
            # print posInfo

            # there seem to be some "bad" gene names ???
            if (aGene == '?'):
                continue

            if ( geneSymbolLooksOK(aGene) ):
                if ( aGene not in geneList ):
                    ## print " adding this gene ", aGene, curRowLabel, Gencode_geneCoordDict_bySymbol[aGene]
                    geneList += [aGene]

        # print " looking thru GAF info ... "

        # and then for GAF ...
        for aGene in GAF_geneCoordDict_bySymbol.keys():

            # if this gene is not even on the same chromosome we're done ...
            if (not GAF_geneCoordDict_bySymbol[aGene].startswith(chrName + ':')):
                continue

            # but if it is, then we need to check start/stop
            posInfo = refData.parseCoordinates(GAF_geneCoordDict_bySymbol[aGene])
            if (chrStop  < posInfo[1]): continue
            if (chrStart > posInfo[2]): continue
            # print posInfo

            # there seem to be some "bad" gene names ???
            if (aGene == '?'):
                continue

            if ( geneSymbolLooksOK(aGene) ):
                if ( aGene not in geneList ):
                    ## print " adding this gene ", aGene, curRowLabel, GAF_geneCoordDict_bySymbol[aGene]
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

def mapFeatures2Genes ( dataD, geneInfoDict, synMapDict, \
    Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID, \
    GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID, \
    refGeneDict, cytoDict, featType, extra_bp ):

    print " "
    print " in mapFeatures2Genes ... "

    # the geneCoordDict_bySymbol has keys that are gene names, eg 'AAGAB', 'TP53', etc
    # and the contents are the coordinates
    # print len(geneCoordDict_bySymbol)

    # similarly, the geneCoordDict_byID has keys that are gene IDs, eg '7157' or '8225',
    # etc and the contents are the coordinates

    # and the geneSymbol_byID dict has keys that are gene IDs, eg '7157', and the 
    # contents are the gene symbols

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

    # we are going to keep track of how many features each gene
    # gets mapped to ...
    geneCounts = {}

    # outer loop over feature names ...
    print " "
    print " starting loop over %d feature names ... " % numRow

    # OUTER LOOP IS OVER ROWS ...
    for iRow in range(numRow):
        curLabel = rowLabels[iRow]

        if (iRow % 100 == 0):
            print " QQ %6d <%s> " % ( iRow, curLabel )

        # grab current feature type
        curType = curLabel[2:6]

        # only look at features of the type specified
        if (curType != featType): continue

        # don't make any attempts at annotating CLIN or SAMP features ...
        if (curType == "CLIN" or curType == "SAMP"): continue

        if ( 1 ):
            # also don't do anything with Gistic arm-level features
            if (curLabel.find("GisticArm") > 0): continue

        # sample feature names:
        # N:METH:C3orf39:chr3:43146780:::cg00008665_5pUTR_NShore
        # N:METH:WNT6:chr2:219738314:::cg00011225_Body_Island

        haveCoord = 0
        haveValidCoord = 0

        # figure out if we have a coordinate in this feature
        tokenList = curLabel.split(':')
        if (tokenList[3] != ''): haveCoord = 1

        # print " curType=<%s>  haveCoord=%d " % ( curType, haveCoord )

        # ------------
        # IF haveCoord
        if (haveCoord):

            # does it look like a 'valid' coordinate ???
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

        # print " flags : ", haveCoord, haveValidCoord

        if (haveValidCoord):

            # now we need to find which genes overlap this region ...
            geneList = overlap ( curLabel, Gencode_geneCoordDict_bySymbol, \
                                 GAF_geneCoordDict_bySymbol, extra_bp )
            # print geneList

            # write out the output line ...
            outLine = curLabel + "\t" + str(len(geneList)) + "\t"
            for aGene in geneList:
                outLine += aGene + ","
            if (outLine[-1] == ','):
                outLine = outLine[:-1]
            fhOut.write("%s\n" % outLine)

            # also keep track of how many features each gene is mapped to
            for aGene in geneList:
                if ( aGene in geneCounts ):
                    geneCounts[aGene] += 1
                else:
                    geneCounts[aGene] = 1
        

    # END OF OUTER LOOP OVER ROWS ...

    print " "
    print " "

    # now have a look at the geneCounts dictionary ...
    maxGeneCount = 0
    maxGeneSymbol = "NA"
    for aGene in geneCounts:
        if ( geneCounts[aGene] > maxGeneCount ):
            maxGeneCount = geneCounts[aGene]
            maxGeneSymbol = aGene

    print " "
    print " gene symbol mapped to the most features : ", maxGeneSymbol, maxGeneCount
    print " total number of symbols : ", len(geneCounts)
    print " "

    histCount = [0] * (maxGeneCount+1)
    for aGene in geneCounts:
        histCount[geneCounts[aGene]] += 1

    print " "
    for iCount in range(len(histCount)):
        if ( histCount[iCount] > 0 ):
            print " %4d  %6d " % ( iCount, histCount[iCount] )
        
    print " "
    print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 5):
            inFile = sys.argv[1]
            mapFile = sys.argv[2]
            featType = sys.argv[3]
            extra_bp = int ( sys.argv[4] )
        else:
            print " "
            print " Usage: %s <input TSV file> <output mapping file> <feature type> <dist bp> " % sys.argv[0]
            print sys.argv
            print len(sys.argv)
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    # open the output file
    global fhOut
    fhOut = file(mapFile, 'w')

    # and get the coordinates for these genes ...
    bioinformaticsReferencesDir = gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES']
    gafFilename = bioinformaticsReferencesDir + "/GAF/GAF3.0/all.gaf"
    gencodeFilename = bioinformaticsReferencesDir + "/gencode/gencode.v19.gene.gtf"
    refGeneFilename = bioinformaticsReferencesDir + "/hg19/refGene.txt"
    cybFilename = bioinformaticsReferencesDir + "/hg19/cytoBand.hg19.txt"

    infFilename = bioinformaticsReferencesDir + "/ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info"

    print " "
    print " Running : %s %s %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print "           %s " % gafFilename
    print "           %s " % gencodeFilename
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

    # read in the gene_info file ... or not ...
    if (0):
        print " --> calling readGeneInfoFile ... "
        (geneInfoDict, synMapDict) = refData.readGeneInfoFile(infFilename)
    else:
        geneInfoDict = {}
        synMapDict = {}

    # then read in the GAF file ... or GENCODE ...
    print " --> calling readGAF ... "
    (GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID) = refData.readGAF(gafFilename)

    print " --> and Gencode ... "
    (Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID) = refData.readGencode(gencodeFilename)

    # also the refGene file ...
    if ( 0 ):
        print " --> calling readRefGeneFile ... "
        refGeneDict = readRefGeneFile(refGeneFilename)
    else:
        refGeneDict = {}

    # then read in the cytoband file ...
    print " --> calling readCytobandFile ... "
    cytoDict = refData.readCytobandFile(cybFilename)

    # and map the features to genes
    print " --> calling mapFeatures2Genes ... "
    annotD = mapFeatures2Genes ( testD, geneInfoDict, synMapDict, \
        Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID, \
        GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID, \
        refGeneDict, cytoDict, featType, extra_bp )

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
