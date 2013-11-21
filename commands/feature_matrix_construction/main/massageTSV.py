# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import miscMath
import miscMatrix
import miscTCGA
import plotMatrix
import tsvIO

import itertools
import numpy
import random
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) < 3):
            print " Usage : %s <input file> <output file> " % sys.argv[0]
            sys.exit(-1)
        inFile = sys.argv[1]
        outFile = sys.argv[2]

    print " ------------------------------------------- "
    print " input file  : ", inFile
    print " output file : ", outFile
    fhIn = file(inFile,  'r')
    fhOut = file(outFile, 'w')

    dataDict = {}

    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)
    if (numTokens < 2):
        print " ERROR ... no information available ??? "
        sys.exit(-1)
    print " header tokens : ", numTokens, hdrTokens

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1
            continue

        barcode = tokenList[0]
        if (len(barcode) >= 15):
            barcode = barcode[:15]

        if (barcode in dataDict.keys()):
            dataDict[barcode] += [(tokenList[1:])]
        else:
            dataDict[barcode] = [(tokenList[1:])]

    fhIn.close()

    # now we have to go back and make sure we have only *one* set of inputs
    # per patient/sample ...

    numOut = numTokens - 1
    intFlags = [1] * numOut
    ynFlags = [1] * numOut
    allNAs = [1] * numOut
    for aBarcode in dataDict.keys():
        numVec = len(dataDict[aBarcode])
        for iVec in range(numVec):
            for iSamp in range(numOut):
                curVal = dataDict[aBarcode][iVec][iSamp]
                if (curVal == "NA"):
                    continue
                allNAs[iSamp] = 0
                try:
                    iVal = int(curVal)
                except:
                    intFlags[iSamp] = 0

                if (curVal != "YES" and curVal != "NO"):
                    ynFlags[iSamp] = 0

    print ' intFlags ...... ', intFlags
    print ' ynFlags ....... ', ynFlags
    print ' allNAs ........ ', allNAs

    for iSamp in range(numOut):
        if (allNAs[iSamp]):
            continue

        if ((intFlags[iSamp] + ynFlags[iSamp]) == 0):
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if (curVal == "NA"):
                        continue
                    try:
                        iVal = int(float(curVal))
                    except:
                        if (curVal.startswith("<")):
                            iVal = int(curVal[1:])
                            dataDict[aBarcode][iVec][iSamp] = iVal
                        elif (curVal.startswith(">")):
                            iVal = int(curVal[1:])
                            dataDict[aBarcode][iVec][iSamp] = iVal
                        else:
                            print " forcing <%s> to NA " % curVal, iVec, iSamp, dataDict[aBarcode]
                            dataDict[aBarcode][iVec][iSamp] = "NA"
                            intFlags[iSamp] = 1
                            # print curVal
                            # print " BAILING (a) ... "

        if ((intFlags[iSamp] + ynFlags[iSamp]) == 2):
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if (curVal == "NA"):
                        continue
                    print curVal
            print " BAILING (b) ... "
            sys.exit(-1)

    for aBarcode in dataDict.keys():
        if (len(dataDict[aBarcode]) > 1):
            print " need to compress this: ", dataDict[aBarcode]
            numVec = len(dataDict[aBarcode])
            numSamp = len(dataDict[aBarcode][0])
            newVec = [0] * numSamp
            sumVec = [0] * numSamp
            countV = [0] * numSamp
            for iSamp in range(numSamp):
                allInt = 1
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if (curVal == "NA"):
                        continue
                    try:
                        iVal = int(float(curVal))
                        sumVec[iSamp] += iVal
                        countV[iSamp] += 1
                    except:
                        allInt = 0
                        if (sumVec[iSamp] == 0):
                            sumVec[iSamp] = curVal
                        if (sumVec[iSamp] != curVal):
                            if (sumVec[iSamp] == "NO" and curVal == "YES"):
                                sumVec[iSamp] = curVal
                            elif (sumVec[iSamp] == "YES" and curVal == "NO"):
                                doNothing = 1
                            else:
                                print " what to do now ??? ", iSamp, sumVec, dataDict[aBarcode][iVec][iSamp]
                                sys.exit(-1)

                if (allInt):
                    if (countV[iSamp] > 1):
                        newVec[iSamp] = int(
                            float(sumVec[iSamp]) / float(countV[iSamp]) + 0.1)
                    elif (countV[iSamp] == 1):
                        newVec[iSamp] = sumVec[iSamp]
                    else:
                        newVec[iSamp] = "NA"

            dataDict[aBarcode] = [newVec]
            print " --> now this: ", dataDict[aBarcode]

    # and finally we can write it out ...

    print " "
    print hdrTokens
    fhOut.write("bcr_patient_barcode")
    for iTok in range(1, numTokens):
        if (allNAs[iTok - 1]):
            continue
        if (intFlags[iTok - 1]):
            fhOut.write("\tN:SAMP:%s" % hdrTokens[iTok])
        elif (ynFlags[iTok - 1]):
            fhOut.write("\tC:SAMP:%s" % hdrTokens[iTok])
        else:
            print " SKIPPING ??? (a) ", iTok, hdrTokens[iTok]
            print allNAs, intFlags, ynFlags
            # sys.exit(-1)
    fhOut.write("\n")

    barcodeList = dataDict.keys()
    barcodeList.sort()
    for aBarcode in barcodeList:
        print aBarcode, dataDict[aBarcode]
        fhOut.write("%s" % aBarcode)
        for iTok in range(1, numTokens):
            if (allNAs[iTok - 1]):
                continue
            if ((not intFlags[iTok - 1]) and (not ynFlags[iTok - 1])):
                continue
            if (dataDict[aBarcode][0][iTok - 1] == "NA"):
                fhOut.write("\tNA")
            else:
                fhOut.write("\t%s" % str(dataDict[aBarcode][0][iTok - 1]))
        fhOut.write("\n")

    fhOut.close()


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
