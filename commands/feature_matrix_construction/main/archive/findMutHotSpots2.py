# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

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
iPChange = -1
numC = 0
cThresh = 0


def getColumnIndices(mafFilename):

    global iHugo, iBarcode, iVarClass, iVarType, iPChange

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
                    iPChange = ii

        print " "
        print " "
        fh.close()

    if (iHugo < 0 or iBarcode < 0 or iVarClass < 0 or iVarType < 0 or iPChange < 0):
        print " ERROR in getColumnIndices ... failed to find one or more required columns "
        print iHugo, iBarcode, iVarClass, iVarType, iPChange
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

    global iHugo, iBarcode, iVarClass, iVarType, iPChange

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

    print len(geneList)
    print geneList

    return (geneList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getProteinChangefromAnnot(annotString):

    pChangeList = []

    # print annotString
    ii = annotString.find(":p.")
    while (ii >= 0):
        jj = annotString.find(",", ii)
        oneChange = annotString[ii + 1:jj]
        # print annotString, ii, jj, oneChange
        if (oneChange not in pChangeList):
            pChangeList += [oneChange]
        ii = annotString.find(":p.", jj)

    # print " returning ", pChangeList
    return (pChangeList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMutDictFromMaf(mafFilename, geneList):

    global iHugo, iBarcode, iVarClass, iVarType, iPChange

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

        barcode = tokenList[iBarcode]
        varClass = tokenList[iVarClass]
        varType = tokenList[iVarType]
        pChange1 = tokenList[iPChange]
        pChange2 = ''

        print hugoSymbol, barcode, varClass, varType, pChange1

        zChange = ''
        if (len(pChange2) > 0):
            if (len(pChange2) > 1):
                print " note: multiple pChange2 ", len(pChange2), pChange2
                # sys.exit(-1)
            if (pChange1 == ''):
                print " --> getting protein change from pChange2 "
                zChange = pChange2[0]
            else:
                if (pChange1 in pChange2):
                    print " --> pChange1 confirmed by pChange2 "
                    zChange = pChange1
                else:
                    print " --> using pChange1 instead of pChange2 "
                    zChange = pChange1
        else:
            if (pChange1 != ''):
                print " -->  using pChange1 (no pChange2) "
                zChange = pChange1
            else:
                print " --> no pChange1 or pChange2 information ", hugoSymbol, varClass, varType
                zChange = varClass + "_" + varType
                print "         --> using <%s> " % zChange

        if (zChange != ''):
            aKey = hugoSymbol + ":" + zChange
        else:
            aKey = hugoSymbol

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
## on /titan/cancerregulome7 TODO:FILE_LAYOUT:EXPLICIT
#
# all of the information is bundled into a dictionary called allClinDict
#

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print " Usage: %s <maf-filename> <tumor-type> " % sys.argv[0]
        sys.exit(-1)

    mafFilename = sys.argv[1]
    tumorType = sys.argv[2]

    print " "
    print " running parseMAF with <%s> <%s> " % (mafFilename, tumorType)

    getColumnIndices(mafFilename)

    countMutCalls(mafFilename)

    geneList = firstPassList(mafFilename)
    print " --> back from first pass, with %d genes in geneList " % (len(geneList))

    tumorList = getTumorBarcodes(mafFilename)
    print " --> %d tumor samples in MAF file " % (len(tumorList))
    tThresh = max(len(tumorList) / 25, 5)
    print " --> threshold will be %d " % (tThresh)

    mutDict = getMutDictFromMaf(mafFilename, geneList)
    print " --> back from getMutDict, with %d genes in dictionary " % (len(mutDict))

    maxCount = 0
    maxKey = "NA"
    for aKey in mutDict.keys():
        if (aKey.find(":") < 0):
            continue
        curCount = len(mutDict[aKey])
        if (curCount > maxCount):
            maxCount = curCount
            maxKey = aKey

    print " "
    print " "
    print " hottest hotspot : ", maxCount, maxKey
    print " "
    if (maxCount < tThresh):
        print " --> does not pass threshold, so no output based on this MAF "
        print " "
        sys.exit(-1)

    for aKey in mutDict.keys():
        if (aKey.find(":") < 0):
            continue
        if (len(mutDict[aKey]) >= tThresh):
            print len(mutDict[aKey]), aKey
    print " "
    print " "

    # example mutation feature:
    # B:GNAB:BRAF:chr7:140433813:140624564:-:y_n_somatic

    # now create an output feature for each of these frequent mutations ...
    tmpFilename = "Hotspot_mutations." + tumorType + ".forTSVmerge.tmp"
    outFilename = tmpFilename[:-4] + ".tsv"
    fh = file(tmpFilename, 'w')

    # the header row has all of the tumor barcodes ...
    outLine = "B:GNAB"
    for aTumor in tumorList:
        outLine += "\t%s" % fixBarcode(aTumor)
    fh.write("%s\n" % outLine)

    for aKey in mutDict.keys():
        if (aKey.find(":") < 0):
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
    cmdString = "python /users/sreynold/to_be_checked_in/TCGAfmp/main/annotateTSV.py %s hg19 %s" % (
        tmpFilename, outFilename)
    (status, output) = commands.getstatusoutput(cmdString)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
