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

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def loadGeneMap ( mapFile ):

    print " in loadGeneMap ... ", mapFile

    fh = file ( mapFile, 'r' )

    allGenes = []
    geneMap = {}

    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')

        ## print len(tokenList), tokenList
        if ( len(tokenList) == 3 ):
            featName = tokenList[0]
            numGenes = int(tokenList[1])
            geneString = tokenList[2]
            geneList = geneString.split(',')
            if ( len(geneList) != numGenes ):
                print " ERROR ??? wrong number of genes ??? "
                print numGenes, len(geneList)
                print geneList
                sys.exit(-1)

            for aGene in geneList:
                if ( aGene not in allGenes ):
                    allGenes += [ aGene ]
                    geneMap[aGene] = [ featName ]
                else:
                    geneMap[aGene] += [ featName ]

    print " done in loadGeneMap "
    print len(geneMap), len(allGenes)

    return ( geneMap )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) == 4):
            inFile  = sys.argv[1]
            mapFile = sys.argv[2]
            outFile = sys.argv[3]
        else:
            print " "
            print " Usage: %s <input TSV file> <gene-map file> <output TSV file> " % sys.argv[0]
            print sys.argv
            print len(sys.argv)
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)


    print " "
    print " Running : %s %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])
    print " "
    print " "

    intGenes = [ "PIK3CA", "EGFR", "CSE1L", "NRAS", "MYCN", "MTAP" ]

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

    # next read in the gene-map output file
    geneMap = loadGeneMap ( mapFile )

    # and now we need to build up the gene-by-CN matrix ...
    numSamples = len(testD['colLabels'])
    geneCNmat = [0] * len(geneMap)
    for iGene in range(len(geneMap)):
        geneCNmat[iGene] = [0] * numSamples

    allGenes = geneMap.keys()
    allGenes.sort()

    numEasy = 0
    numHarder = 0

    for iGene in range(len(allGenes)):
        aGene = allGenes[iGene]
        if ( aGene in intGenes ):
            print " "
            print " interesting gene ... "
            print aGene, len(geneMap[aGene]), geneMap[aGene]

        ## first the easy case where there is just one feature for this gene
        if ( len(geneMap[aGene]) == 1 ):
            numEasy += 1
            featName = geneMap[aGene][0]
            if ( aGene in intGenes ): print featName
            try:
                iFeat = testD['rowLabels'].index(featName)
            except:
                print " ERROR ??? feature not found ??? "
                print featName
                print testD['rowLabels'][0:3]
                sys.exit(-1)
            ## print iFeat
            for iSamp in range(numSamples):
                geneCNmat[iGene][iSamp] = testD['dataMatrix'][iFeat][iSamp]

        ## next the more complicated case ...
        else:
            numHarder += 1
            iList = []
            for featName in geneMap[aGene]:
                try:
                    iFeat = testD['rowLabels'].index(featName)
                except:
                    print " ERROR ??? feature not found ??? "
                    print featName
                    print testD['rowLabels'][0:3]
                    sys.exit(-1)
                iList += [ iFeat ]
            ## print iList
            for iSamp in range(numSamples):
                valList = []
                for iFeat in iList:
                    curVal = testD['dataMatrix'][iFeat][iSamp]
                    if ( curVal == "NA" ):
                        doNothing = 1
                    elif ( curVal == NA_VALUE ):
                        doNothing = 1
                    else:
                        valList += [ curVal ]
                minVal = min ( valList )
                maxVal = max ( valList )
                if ( aGene in intGenes ): print iSamp, minVal, maxVal
                if ( abs(minVal) > abs(maxVal) ):
                    geneCNmat[iGene][iSamp] = minVal
                else:
                    geneCNmat[iGene][iSamp] = maxVal

    print " "
    print " numEasy=%d    numHarder=%d " % ( numEasy, numHarder )
    print " "
                    
    ## and now we can write out the matrix ...
    fhOut = file(outFile, 'w')

    ## first the header line:
    outLine = "Gene Symbol"
    for iSamp in range(numSamples):
        outLine += "\t%s" % testD['colLabels'][iSamp]
    fhOut.write("%s\n" % outLine )

    for iGene in range(len(allGenes)):
        aGene = allGenes[iGene]
        outLine = aGene
        for iSamp in range(numSamples):
            if ( geneCNmat[iGene][iSamp] == "NA" ):
                outLine += "\tNA"
            elif ( geneCNmat[iGene][iSamp] == NA_VALUE ):
                outLine += "\tNA"
            else:
                outLine += "\t%.3f" % geneCNmat[iGene][iSamp]
        fhOut.write("%s\n" % outLine )

    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
