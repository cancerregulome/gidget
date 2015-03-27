# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars
import arffIO
import miscClin
import miscTCGA
import tsvIO

# these are system modules
from datetime import datetime
from xml.dom import minidom
from xml.dom import Node

import commands
import os
import path
import string
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# TODO: figure out where the 'proper' columns are?
# Hugo_Symbol
# Tumor_Sample_Barcode
# Protein_Change
# Annotations

iHugo = -1
iBarcode = -1
iVarClass = -1
iVarType = -1
iPChangeA = -1
iPChangeB = -1
numC = 0
cThresh = 0


def getColumnIndices(mafFilename):

    global iHugo, iBarcode, iVarClass, iVarType, iPChangeA, iPChangeB

    if (1):
        print " "
        print " "
        fh = file(mafFilename, 'r')
        aLine = "#"
        while aLine.startswith("#"):
            aLine = fh.readline()
        bLine = fh.readline()

        aLine = aLine.strip()
        bLine = bLine.strip()

        aTokens = aLine.split('\t')
        bTokens = bLine.split('\t')

        for ii in range(max(len(aTokens), len(bTokens))):
            outLine = " %3d " % ii
            if (ii < len(aTokens)):
                outLine += " \t %s " % aTokens[ii]
            else:
                outLine += " \t  "
            if (ii < len(bTokens)):
                outLine += " \t %s " % bTokens[ii]
            else:
                outLine += " \t  "
            print outLine

            if (ii < len(aTokens)):
                if (aTokens[ii] == "Hugo_Symbol"):
                    iHugo = ii
                if (aTokens[ii] == "Tumor_Sample_Barcode"):
                    iBarcode = ii
                if (aTokens[ii] == "Variant_Classification"):
                    iVarClass = ii
                if (aTokens[ii] == "Variant_Type"):
                    iVarType = ii

                if (aTokens[ii] == "Protein_Change"):
                    iPChangeA = ii
                if (aTokens[ii] == "amino_acid_change_WU"):
                    iPChangeA = ii
                if (aTokens[ii] == "amino_acid_change"):
                    iPChangeA = ii
                if (aTokens[ii] == "AAChange"):
                    iPChangeA = ii
                if (aTokens[ii] == "Mutation Annotation (uniprot isoform1)"):
                    iPChangeA = ii
                if (aTokens[ii] == "Mutation Annotation (Others)"):
                    iPChangeB = ii
                

        print " "
        print " "
        fh.close()

    if (iHugo < 0 or iBarcode < 0 or iVarClass < 0 or iVarType < 0 or (iPChangeA+iPChangeB) < 0):
        print " ERROR in getColumnIndices ... failed to find one or more required columns "
        print mafFilename
        print iHugo, iBarcode, iVarClass, iVarType, iPChangeA, iPChangeB
        print aTokens
        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def countMutCalls(mafFilename):
    global numC, cThresh
    fh = file(mafFilename, 'r')
    for aLine in fh:
        if (aLine.startswith("#")):
            continue
        numC += 1
    fh.close()

    numC -= 1
    cThresh = max(numC / 8000, 5)
    print " numC=%d    threshold=%d " % (numC, cThresh)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def fixBarcode(aBarcode):

    # examples of 'good' and 'bad' barcodes:
    # TCGA-B7-5816-01A-21D-1600-08
    # 0123456789012345678901234567
    # STAD-TCGA-B7-5816-Tumor-SM-1V6U3

    if (aBarcode.startswith("TCGA")):
        if (aBarcode[4] == "-"):
            if (aBarcode[7] == "-"):
                if (len(aBarcode) > 12):
                    if (aBarcode[12] == "-"):
                        if (len(aBarcode) > 16):
                            if (aBarcode[16] == "-"):
                                return (aBarcode)
                        else:
                            return (aBarcode)
                else:
                    return (aBarcode)

    elif (aBarcode.find("TCGA-") > 0):
        ii = aBarcode.find("TCGA-")
        aBarcode = aBarcode[ii:]

        if (aBarcode.find("Tumor") > 0):
            ii = aBarcode.find("-Tumor")
            aBarcode = aBarcode[:ii] + "-01"

        return (aBarcode)

    # we should not get here ...
    print " ERROR in fixBarcode ??? "
    print aBarcode
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def firstPassList(mafFilename):

    global iHugo, iBarcode, iVarClass, iVarType, iPChangeA, iPChangeB

    try:
        fh = file(mafFilename)
    except:
        print " ERROR opening MAF file <%s> " % mafFilename
        sys.exit(-1)

    mutDict = {}

    iLine = 0
    for aLine in fh:

        aLine = aLine.strip()
        if (aLine.startswith("#")):
            continue

        tokenList = aLine.split('\t')

        if (0):
            print iLine, len(tokenList)
            print tokenList
            for ii in range(50):
                print ii, tokenList[ii]
            print " "

        if (tokenList[iHugo] == "Hugo_Symbol"):
            continue
        hugoSymbol = tokenList[iHugo]

        if (hugoSymbol.startswith("abPart")):
            continue
        if (hugoSymbol.lower() == "unknown"):
            continue

        aKey = hugoSymbol
        if (aKey not in mutDict.keys()):
            mutDict[aKey] = 0
        mutDict[aKey] += 1

        iLine += 1
        if (iLine % 5000 == 0):
            print iLine, len(mutDict), " ( first pass ) "

    fh.close()

    geneList = []
    for aKey in mutDict.keys():
        if (mutDict[aKey] >= cThresh):
            geneList += [aKey]

    print " length of geneList : ", len(geneList)
    ## print geneList

    return (geneList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getProteinChangefromAnnot(annotString):

    pChangeList = []

    ## print " in getProteinChangefromAnnot ... <%s> " % annotString

    ii = annotString.find(":p.")
    while (ii >= 0):
        jj = annotString.find(",", ii)
        oneChange = annotString[ii+3:jj]
        # print annotString, ii, jj, oneChange
        if (oneChange not in pChangeList):
            pChangeList += [oneChange]
        ii = annotString.find(":p.", jj)

    if ( len(pChangeList) == 0 ):
        print " what to do now ??? NO protein changes ??? !!! ", pChangeList
        sys.exit(-1)

    if ( len(pChangeList) > 1 ):
        ## print " WARNING !!! multiple protein changes ??? !!! ", pChangeList

        if ( 0 ):
            iMin = 999999
            for aChange in pChangeList:
                iPos = int ( aChange[1:-1] )
                if ( iPos < iMin ):
                    iMin = iPos
                    keepChange = aChange
            ## print " --> (A) choosing this one : ", keepChange
            pChangeList = [ keepChange ]

        if ( 1 ):
            keepChange = pChangeList[0]
            ## print " --> (B) choosing this one : ", keepChange
            pChangeList = [ keepChange ]

    # print " returning ", pChangeList
    return (pChangeList[0])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def stripAfterComma ( aString ):

    ii = aString.find(",")
    if ( ii > 0 ): aString = aString[:ii]
    ## print aString

    return ( aString )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getProteinChange ( pChangeString ):

    if ( pChangeString == '' ): return ( '' )
    if ( pChangeString == '---' ): return ( '' )

    ## print " in getProteinChange ... ", pChangeString

    ## first, let's see if it's simply something like V600E
    iString = pChangeString[1:-1]
    ## print "       a ", iString
    try:
        iPos = int ( iString )
        ## print "         b returning ", pChangeString
        return ( pChangeString )

    except:
        ## no, evidently it was not just V600E ...

        ## next check to see if it starts with "p."
        if ( pChangeString.startswith("p.") ):
            ## print "         c ", pChangeString
            pChangeString = pChangeString[2:]
            ## print "         d ", pChangeString

            ## strip after comma ... (if it looks like "p.R524K,stuff")
            pChangeString = stripAfterComma ( pChangeString )

            ## it might end with fs, eg p.K2293fs
            if ( pChangeString.endswith("fs") ):
                iString = pChangeString[1:-2]
                ## print "            i   ", iString

            ## or it might end with del, eg p.E921del
            elif ( pChangeString.endswith("del") ):
                iString = pChangeString[1:-3]
                ## print "            iv  ", iString

            ## or it might look like p.R524_splice instead ...
            elif ( pChangeString.find("_") > 1 ):
                ii = pChangeString.find("_")
                iString = pChangeString[1:ii]
                ## print "            ii  ", iString

            ## otherwise, hopefully it's just p.R524
            else:
                iString = pChangeString[1:-1]
                ## print "            iii ", iString

            ## print "         f ", iString

            ## did we get an integer position ???
            try:
                iPos = int ( iString )
                ## print "         e returning ", pChangeString
                return ( pChangeString )
            except:
                print " (a) TOTAL FAILURE after all that ??? ", pChangeString
                return ( '' )
                sys.exit(-1)

        ## or if it looks like PLEKHG5:uc001ano.1:exon20:c.G2331A:p.E777E,p.E783E
        elif ( pChangeString.find(":p.") >= 0 ):
            pChange = getProteinChangefromAnnot ( pChangeString )
            if ( pChange != '' ):
                ## print "         d returning ", pChange
                return ( pChange )
            else:
                print " (b) TOTAL FAILURE ??? after all that ", pChangeString
                return ( '' )
                sys.exit(-1)

    print " got nothing ... bailing out of getProteinChange ... ", pChangeString
    return ( '' )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def isTruePointMutation ( aKey ):

    if ( aKey == '' ): return ( 0 )

    bKey = aKey.lower()
    if ( bKey.find("3utr") >= 0 ): return ( 0 )
    if ( bKey.find("5utr") >= 0 ): return ( 0 )
    if ( bKey.find("3'utr") >= 0 ): return ( 0 )
    if ( bKey.find("5'utr") >= 0 ): return ( 0 )
    if ( bKey.find("intron") >= 0 ): return ( 0 )

    return ( 1 )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getMutDictFromMaf(mafFilename, geneList):

    global iHugo, iBarcode, iVarClass, iVarType, iPChangeA, iPChangeB

    try:
        fh = file(mafFilename)
    except:
        print " ERROR opening MAF file <%s> " % mafFilename
        sys.exit(-1)

    mutDict = {}

    iLine = 0
    for aLine in fh:

        aLine = aLine.strip()
        if (aLine.startswith("#")):
            continue

        tokenList = aLine.split('\t')

        if (0):
            print iLine, len(tokenList)
            print tokenList
            for ii in range(50):
                print ii, tokenList[ii]
            print " "

        if (tokenList[iHugo] == "Hugo_Symbol"):
            continue
        hugoSymbol = tokenList[iHugo]
        iLine += 1

        if (hugoSymbol not in geneList):
            continue

        try:
            barcode = tokenList[iBarcode]
            varClass = tokenList[iVarClass]
            varType = tokenList[iVarType]
            pChangeA = tokenList[iPChangeA]
            pChangeB = tokenList[iPChangeB]
        except:
            continue

        ## print " pChangeA : <%s> " % pChangeA
        ## print " pChangeB : <%s> " % pChangeB

        # parse out the protein change ...
        zChangeA = getProteinChange ( pChangeA )
        zChangeB = getProteinChange ( pChangeB )
        ## print zChangeA, zChangeB

        ## prioritize the "A" change over the "B" change ...
        zChange = ''
        if ( zChangeB == '' ): 
            zChange = zChangeA
        elif ( zChangeA == '' ): 
            zChange = zChangeB

        if ( 0 ):
            # print hugoSymbol, barcode, varClass, varType, pChangeA
            if ( zChange == '' ):
                # print " --> no pChangeA or pChangeB information ", hugoSymbol, varClass, varType
                zChange = varClass + "_" + varType
                # print "         --> using <%s> " % zChange

        ## print zChange

        ## but now we are going to toss out some types of mutations that 
        ## are really not point mutations and therefore cannot correspond 
        ## to a "hot point"
        if ( isTruePointMutation ( zChange ) ):
            aKey = hugoSymbol + ":" + zChange
            ## print aKey
            if (aKey not in mutDict.keys()):
                mutDict[aKey] = []
            mutDict[aKey] += [barcode]

        if (iLine % 5000 == 0):
            print iLine, len(mutDict), " ( third pass ) "

    fh.close()

    return (mutDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getTumorBarcodes(mafFilename):

    global iHugo, iBarcode, iPChange

    try:
        fh = file(mafFilename)
    except:
        print " ERROR opening MAF file <%s> " % mafFilename
        sys.exit(-1)

    barcodeList = []

    iLine = 0
    for aLine in fh:

        aLine = aLine.strip()
        if (aLine.startswith("#")):
            continue

        tokenList = aLine.split('\t')

        if (0):
            print iLine, len(tokenList)
            print tokenList
            for ii in range(50):
                print ii, tokenList[ii]
            print " "

        if (tokenList[iHugo] == "Hugo_Symbol"):
            continue
        hugoSymbol = tokenList[iHugo]
        iLine += 1

        barcode = tokenList[iBarcode]
        if (barcode not in barcodeList):
            barcodeList += [barcode]

        if (iLine % 5000 == 0):
            print iLine, len(barcodeList), " ( second pass ) "

    fh.close()

    return (barcodeList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#
# this program loops over the tumor types in the cancerDirNames list and
# looks for all available *clinical*.xml files in the current "dcc-snapshot"
#
# all of the information is bundled into a dictionary called allClinDict
#

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print " "
        print " Usage: %s <maf-filename> <output-filename> " % sys.argv[0]
        print " "
        print " Note: this should be able to work with raw MAF files, or with the " 
        print "       *.maf.ncm and *.maf.ncm.with_uniprot outputs from the MAF pipeline "
        print " "
        print "       also, the output file is ready to be placed in the aux directory "
        print "       as a *.forTSVmerge.tsv file, so you might want to include that "
        print "       suffix in the output-filename on the command line "
        print " "
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    mafFilename = sys.argv[1]
    outFilename = sys.argv[2]

    print " "
    print " running %s with <%s> <%s> " % (sys.argv[0], mafFilename, outFilename)

    getColumnIndices(mafFilename)

    countMutCalls(mafFilename)

    geneList = firstPassList(mafFilename)
    print " --> back from first pass, with %d genes in geneList " % (len(geneList))

    tumorList = getTumorBarcodes(mafFilename)
    print " --> %d tumor samples in MAF file " % (len(tumorList))
    tThresh = max(len(tumorList) / 25, 5)
    tThresh = max(len(tumorList) / 50, 3)
    print " --> threshold will be %d " % (tThresh)

    mutDict = getMutDictFromMaf(mafFilename, geneList)
    print " --> back from getMutDict, with %d genes in dictionary " % (len(mutDict))

    maxCount = 0
    maxKey = "NA"
    for aKey in mutDict.keys():
        if (aKey.find(":") < 0):
            continue
        if (aKey.find("RNA_") >= 0):
            continue
        if (aKey.find("NULL") >= 0):
            continue
        curCount = len(mutDict[aKey])
        if (curCount > maxCount):
            maxCount = curCount
            maxKey = aKey

    print " "
    print " "
    if (maxCount >= tThresh):
        print " hottest point : ", maxCount, maxKey, 100. * (float(maxCount) / float(len(tumorList)))
    else:
        print " --> does not pass threshold, so no output based on this MAF "
        print " "
        sys.exit(-1)

    ## look through and see how many "hot" spots we have ... maybe we need
    ## to set the threshold a bit higher if there are too many ...
    print " walking through mutDict ... "
    print len(mutDict)
    tmpKeys = mutDict.keys()
    print tmpKeys[:5], tmpKeys[-5:]
    cumHist = [0] * (maxCount + 3)
    for aKey in mutDict.keys():
        if (aKey.find(":") < 0): continue
        if (aKey.find("RNA_") >= 0): continue
        if (aKey.find("NULL") >= 0): continue
        if (len(mutDict[aKey]) >= tThresh):
            nCount = len(mutDict[aKey])
            for iCount in range(nCount+1):
                cumHist[iCount] += 1

    print " "
    print " cumHist : "
    for iCount in range(len(cumHist)):
        print " %3d  %6d " % ( iCount, cumHist[iCount] )

    ## now we walk along this cumulative histogram and keep track
    ## of when we have more than maxN hot-points ...
    maxN = 20
    maxN = 50
    for iCount in range(len(cumHist)):
        jCount = len(cumHist) - 1 - iCount
        if ( cumHist[jCount] < maxN ):
            zThresh = jCount 

    if ( zThresh > tThresh ):
        print " --> resetting threshold from %d to %d " % ( tThresh, zThresh )
        tThresh = zThresh
    else:
        print "     ( no need to reset threshold ) "

    print " "
    print " "

    for aKey in mutDict.keys():
        if (aKey.find(":") < 0): continue
        if (aKey.find("RNA_") >= 0): continue
        if (aKey.find("NULL") >= 0): continue
        if (len(mutDict[aKey]) >= tThresh):
            nCount = len(mutDict[aKey])
            xPct = 100. * (float(nCount) / float(len(tumorList)))
            print "%s\t%d\t%.1f\tHotPoint" % (aKey, nCount, xPct)
    print " "
    print " "

    # example mutation feature:
    # B:GNAB:BRAF:chr7:140433813:140624564:-:y_n_somatic

    # now create an output feature for each of these frequent mutations ...
    tmpFilename = outFilename + ".tmp"
    fh = file(tmpFilename, 'w')

    # the header row has all of the tumor barcodes ...
    outLine = "B:GNAB"
    for aTumor in tumorList:
        outLine += "\t%s" % fixBarcode(aTumor)
    fh.write("%s\n" % outLine)

    for aKey in mutDict.keys():
        if (aKey.find(":") < 0):
            continue
        if (aKey.find("RNA_") >= 0):
            continue
        if (aKey.find("NULL") >= 0):
            continue
        keyTokens = aKey.split(":")
        if (len(mutDict[aKey]) >= tThresh):
            if (keyTokens[1].startswith("p.")):
                outLine = "B:GNAB:" + keyTokens[0] + ":::::" + keyTokens[1][2:]
            else:
                outLine = "B:GNAB:" + keyTokens[0] + ":::::" + keyTokens[1]
            for aTumor in tumorList:
                if (aTumor in mutDict[aKey]):
                    outLine += "\t1"
                else:
                    outLine += "\t0"
            fh.write("%s\n" % outLine)

    fh.close()

    print " annotating output file ... "
    cmdString = "python %s/main/annotateTSV.py %s hg19 %s" % ( gidgetConfigVars['TCGAFMP_ROOT_DIR'], tmpFilename, outFilename )
    print cmdString
    (status, output) = commands.getstatusoutput(cmdString)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
