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
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        inFile = sys.argv[1]
        outFile = sys.argv[2]

    print " "
    print " "
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

    print numTokens
    print hdrTokens

    if (numTokens < 2):
        print " ERROR ... no information available ??? "
        sys.exit(-1)
    print " header tokens : ", numTokens, hdrTokens

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        ## print len(tokenList), tokenList

        if (len(tokenList)<2): done = 1
        if (len(tokenList) != numTokens): continue

        if ( not aLine.startswith("TCGA") ): continue

        barcode = tokenList[0]
        ## truncate barcode to 16 characters, eg TCGA-BF-A1PU-01A
        if (len(barcode) >= 17): barcode = barcode[:16]

        ## print barcode

        if (barcode in dataDict.keys()):
            dataDict[barcode] += [(tokenList[1:])]
        else:
            dataDict[barcode] = [(tokenList[1:])]

    print " done reading input file ... "
    fhIn.close()

    print " "
    if ( len(dataDict) == 0 ):
        print " ERROR ??? empty data dictionary ??? "
        print " "
        sys.exit(-1)
    ## print len(dataDict)
    aBarcode = (dataDict.keys())[0]
    ## print aBarcode
    ## print dataDict[aBarcode]
    ## print " "

    # now we have to go back and make sure we have only *one* set of inputs
    # per patient/sample ...

    ## print " "
    ## print " LOOP 1 "
    ## print " "

    numOut = numTokens - 1
    intFlags = [1] * numOut
    ynFlags = [1] * numOut
    allNAs = [1] * numOut

    # in this first pass we figure out whether each feature is either
    # 'all NA', or an integer, or a yes/no flag ...
    for aBarcode in dataDict.keys():
        numVec = len(dataDict[aBarcode])
        if ( 0 ):
            if ( numVec > 1 ):
                print " WARNING !!! have more than one data vector ", aBarcode, numVec, numOut
            else:
                print " all OK .... have exactly one data vector   ", aBarcode, numVec, numOut
        for iVec in range(numVec):
            ## print "         ", iVec, dataDict[aBarcode][iVec]
            for iSamp in range(numOut):
                curVal = dataDict[aBarcode][iVec][iSamp]
                if (curVal == "NA"): continue
                allNAs[iSamp] = 0
                try:
                    iVal = int(curVal)
                except:
                    intFlags[iSamp] = 0

                if (curVal != "YES" and curVal != "NO"):
                    ynFlags[iSamp] = 0
                ## print "         allNAs %d    intFlags %d    ynFlags %d " % \
                    (  allNAs[iSamp], intFlags[iSamp], ynFlags[iSamp] )

    print ' intFlags ...... ', intFlags
    print ' ynFlags ....... ', ynFlags
    print ' allNAs ........ ', allNAs

    ## print " LOOP 2 "
    # in this second pass we take a nother look at the contents of these
    # data vectors ...
    for iSamp in range(numOut):

        # if all of the features are NA, nothing to be done ...
        if (allNAs[iSamp]): continue

        # if it is neither an integer nor a yes-no flag ...
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
                            # we are not handling strings, so if it is a string of some
                            # kind (eg TOP or BOTTOM), then just force to NA for now
                            ## print " forcing <%s> to NA " % curVal, iVec, iSamp, dataDict[aBarcode]
                            dataDict[aBarcode][iVec][iSamp] = "NA"
                            intFlags[iSamp] = 1
                            # print curVal

        # if it appears to sometimes be an integer and sometimes a yes-no flag (???)
        if ((intFlags[iSamp] + ynFlags[iSamp]) == 2):
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if (curVal == "NA"):
                        continue
                    ## print curVal
            print " BAILING (b) ... ", iSamp, intFlags, ynFlags, curVal, numVec
            sys.exit(-1)

    # and now finally in this 3rd pass we need to do something ...
    ## print " LOOP 3 "
    for aBarcode in dataDict.keys():
        if (len(dataDict[aBarcode]) > 1):
            print " need to compress this: ", dataDict[aBarcode]
            numVec = len(dataDict[aBarcode])
            numSamp = len(dataDict[aBarcode][0])
            newVec = [0] * numSamp
            sumVec = [0] * numSamp
            countV = [0] * numSamp
            for iSamp in range(numSamp):
                ## print "         allNAs %d    intFlags %d    ynFlags %d " % \
                ##     (  allNAs[iSamp], intFlags[iSamp], ynFlags[iSamp] )
                if ( allNAs[iSamp] ): continue
                allInt = 1

                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if (curVal == "NA"): continue

                    ## if this is a yes-no flag, then initially set the 'newVec'
                    ## to the first value and then check to see that there are
                    ## no contradictions ...
                    if ( ynFlags[iSamp] ):
                        allInt = 0
                        if ( iVec==0 ):
                            ## print "         --> setting newVec[%d] to " % iSamp, curVal
                            newVec[iSamp] = curVal
                        else:
                            ## if there is a contradiction, reset to NA
                            ## print "         --> checking ... ", iSamp, newVec[iSamp], curVal
                            if ( newVec[iSamp] != curVal ):
                                ## print "         CONTRADICTION "
                                newVec[iSamp] = "NA"

                    else:
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
                                    print " BAILING (c) ... ", iSamp, intFlags, ynFlags, curVal, numVec
                                    sys.exit(-1)

                # if all of the values were integers, now let's compute an average ...
                if (allInt):
                    if (countV[iSamp] > 1):
                        ## print " computing average ", iSamp, sumVec[iSamp], countV[iSamp]
                        newVec[iSamp] = int(float(sumVec[iSamp]) / float(countV[iSamp]) + 0.1)
                    elif (countV[iSamp] == 1):
                        ## print " no need to average ", iSamp, sumVec[iSamp], countV[iSam]
                        newVec[iSamp] = sumVec[iSamp]
                    else:
                        ## print " oops, resetting to NA ??? ", iSamp
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

    print " "
    print " ------------------------------------------- "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
