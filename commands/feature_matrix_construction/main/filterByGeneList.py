# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import miscMath
import miscMatrix
import miscTCGA
import plotMatrix
import tsvIO

import numpy
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readGeneListFromFile(geneFile):

    fh = file(geneFile)

    geneList = []

    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()
        tokenList = aLine.split('\t')
        if (len(tokenList) > 0):
            geneList += [tokenList[0]]

    fh.close()

    return (geneList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def gene_in_list(geneName, geneList):

    geneName = geneName.upper()

    # first, look for a perfect match
    if (geneName in geneList):
        return (1)

    else:

        if (1):
            # do not allow partial matches ...
            return (0)

        # second, settle for a partial match
        for aGene in geneList:
            if (geneName.find(aGene) >= 0):
                return (1)
            if (aGene.find(geneName) >= 0):
                return (1)
        return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) < 4 or len(sys.argv) > 5):
            print " Usage : %s <input file> <output file> <gene-list file> [min-nonZero-count] " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        inFile = sys.argv[1]
        outFile = sys.argv[2]
        geneFile = sys.argv[3]
        if (len(sys.argv) > 4):
            minNZC = int(sys.argv[4])
        else:
            minNZC = 1

    print " "
    print " "
    print " ********************* "
    print " in filterByGeneList : "
    print " ***************************************************************** "
    print " calling readTSV ... ", inFile
    testD = tsvIO.readTSV(inFile)
    tsvIO.lookAtDataD(testD)

    print " "
    print " "

    print " reading gene list from ", geneFile
    geneList = readGeneListFromFile(geneFile)
    print " --> have %d genes in list " % len(geneList)
    print geneList[:5]
    print geneList[-5:]
    print " "
    print " "

    rowLabels = testD['rowLabels']
    colLabels = testD['colLabels']
    dataMatrix = testD['dataMatrix']

    numRow = len(rowLabels)
    numCol = len(colLabels)

    print numRow, rowLabels[:5]
    print numCol, colLabels[:5]
    print " "
    print " "

    rmRowList = []
    nzHist = [0] * (numCol + 3)
    for iRow in range(numRow):

        if (iRow % 10000 == 0):
            print iRow, numRow

        rowName = rowLabels[iRow]
        tokenList = rowName.split(':')
        # print rowName, tokenList

        geneName = tokenList[2]
        ii = geneName.find('_')
        if (ii > 0):
            geneName = geneName[:ii]
        # print " looking for gene <%s> " % geneName

        if (not gene_in_list(geneName, geneList)):
            rmRowList += [iRow]
        else:
            numNZ = 0
            for iCol in range(numCol):
                if (dataMatrix[iRow][iCol] != 0):
                    numNZ += 1
            nzHist[numNZ] += 1
            if (numNZ < minNZC):
                rmRowList += [iRow]

    print " --> number of rows to be skipped : %d out of %d " % (len(rmRowList), numRow)
    print "     number of rows remaining : %d " % (numRow - len(rmRowList))

    print " "
    print " histogram of NZ counts : "
    for ii in range(len(nzHist)):
        if (nzHist[ii] > 0):
            print " %4d  %12d " % (ii, nzHist[ii])
    print " "
    print " "

    newD = tsvIO.filter_dataMatrix(testD, rmRowList, [])
    tsvIO.lookAtDataD(newD)

    if (newD['dataType'] == ""):
        newD['dataType'] = "B:GNAB"

    colLabels = newD['colLabels']
    for ii in range(len(colLabels)):
        aLabel = colLabels[ii]
        if (aLabel.find("TUMOR") > 0):
            print " ERROR ??? how did this get here ??? ", aLabel
            sys.exit(-1)

    print " "
    print " ready to write output file ... ", outFile
    tsvIO.writeTSV_dataMatrix(newD, 0, 0, outFile)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
