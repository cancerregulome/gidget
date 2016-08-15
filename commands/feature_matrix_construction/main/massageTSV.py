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
# the incoming dataDict has barcodes as keys and then information tokens ...

def checkMultiPartTokens ( dataDict ):

    for aBarcode in dataDict.keys():
        aList = dataDict[aBarcode]
        for ii in range(len(aList)):
            bList = aList[ii]
            for jj in range(len(bList)):
                if ( bList[jj].find("|") > 0 ):
                    print " doing this thing ", aBarcode, dataDict[aBarcode]
                    cList = bList[jj].split('|')
                    uList = []
                    for cStr in cList:
                        if ( cStr not in uList ):
                            uList += [ cStr ]
                    print bList
                    print cList
                    print uList
                    if ( len(uList) == 1 ):
                        dataDict[aBarcode][ii][jj] = uList[0]
                    else:
                        newStr = uList[0]
                        for kk in range(1,len(uList)):
                            newStr += ";" + uList[kk]
                        dataDict[aBarcode][ii][jj] = newStr
                    aBarcode, ii, jj, dataDict[aBarcode]

    return dataDict

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
    print " running massageTSV on: "
    print "     input file  : ", inFile
    print "     output file : ", outFile
    fhIn = file(inFile,  'r')
    fhOut = file(outFile, 'w')

    dataDict = {}

    ## the first header line has column names, eg 'bcr_sample_barcode' and 'days_to_collection'
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
        if (len(aLine) < 8 ):
            print " looks like eof ... <%s> ", aLine
            done = 1

        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        print len(tokenList), tokenList

        if ( not aLine.startswith("TCGA-") ): 
            print " skipping this row because it doesn't start with TCGA barcode "
            continue

        if (len(tokenList) != numTokens): 
            print " unexpected number of tokens ??? ", len(tokenList), numTokens
            continue

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

    ## I have noticed that sometimes the "token" is a multi-part string separated by "|"
    ## and sometimes the two parts are identical, so let's avoid that and also remove
    ## that particular special character ...
    dataDict = checkMultiPartTokens ( dataDict )

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

    print " "
    print " LOOP 1 "
    print " "

    numOut = numTokens - 1

    ## initialize set of flags to "all TRUE"
    intFlags = [1] * numOut
    fltFlags = [1] * numOut
    ynFlags = [1] * numOut
    allNAs = [1] * numOut

    # in this first pass we figure out whether each feature is either
    # 'all NA', or an integer, or a yes/no flag ...
    for aBarcode in dataDict.keys():
        numVec = len(dataDict[aBarcode])
        print "     checking %s %d %d " % ( aBarcode, numVec, numOut )
        for iVec in range(numVec):
            ## print "         ", iVec, dataDict[aBarcode][iVec]
            for iSamp in range(numOut):
                curVal = dataDict[aBarcode][iVec][iSamp]
                print curVal

                # is the current value NA?
                if (curVal == "NA"): continue
                allNAs[iSamp] = 0

                # can the current value be seen as an integer?
                try:
                    iVal = int(curVal)
                except:
                    intFlags[iSamp] = 0

                # can the current value be seen as a continuous value?
                try:
                    fVal = float(curVal)
                except:
                    fltFlags[iSamp] = 0

                # is the current value all yes or all no?
                if (curVal.upper() != "YES" and curVal.upper() != "NO"):
                    ynFlags[iSamp] = 0

                print iSamp, " : ", intFlags[iSamp], fltFlags[iSamp], ynFlags[iSamp], allNAs[iSamp]


    print ' intFlags ...... ', intFlags
    print ' fltFlags ...... ', fltFlags
    print ' ynFlags ....... ', ynFlags
    print ' allNAs ........ ', allNAs

    print " "
    print " LOOP 2 "
    print " "

    # in this second pass we take another look at the contents of these
    # data vectors ...
    for iSamp in range(numOut):
        print " iSamp=%d (out of %d) " % ( iSamp, numOut )
        print intFlags[iSamp], fltFlags[iSamp], ynFlags[iSamp], allNAs[iSamp]

        # if all of the features are NA, nothing to be done ...
        if (allNAs[iSamp]): continue

        # do we think this is an integer?
        if ( intFlags[iSamp] ):
            print " should have integers ... "
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if ( curVal == "NA" ): continue

                    try:
                        iVal = int(float(curVal))
                        dataDict[aBarcode][iVec][iSamp] = iVal
                    except:
                        print " ERROR ??? I thought this was an integer ??? "
                        print aBarcode, iVec, iSamp, dataDict[aBarcode][iVec][iSamp]
                        sys.exit(-1)
            continue

        # do we think this is a continuous value?
        if ( fltFlags[iSamp] ):
            print " should have continuous values ... "
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if ( curVal == "NA" ): continue

                    try:
                        fVal = float(curVal)
                        dataDict[aBarcode][iVec][iSamp] = fVal
                    except:
                        print " ERROR ??? I thought this was a float ??? "
                        print aBarcode, iVec, iSamp, dataDict[aBarcode][iVec][iSamp]
                        sys.exit(-1)
            continue

        # do we think this is a yes/no?
        if ( ynFlags[iSamp] ):
            print " should have YES or NO values "
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if ( curVal == "NA" ): continue

                    if ( curVal.upper() == "YES" ):
                        dataDict[aBarcode][iVec][iSamp] = "YES"
                    elif ( curVal.upper() == "NO" ):
                        dataDict[aBarcode][iVec][iSamp] = "NO"
                    else:
                        print " ERROR ??? I thought this was a YES or NO ??? "
                        print aBarcode, iVec, iSamp, dataDict[aBarcode][iVec][iSamp]
                        sys.exit(-1)
            continue

        # otherwise ...
        if ( 1 ):
            print " or random strings ... "
            for aBarcode in dataDict.keys():
                numVec = len(dataDict[aBarcode])
                for iVec in range(numVec):
                    curVal = dataDict[aBarcode][iVec][iSamp]
                    if ( curVal == "NA" ): continue
                    dataDict[aBarcode][iVec][iSamp] = curVal
            continue

    # and now finally in this 3rd pass we need to do something ...

    print " "
    print " LOOP 3 "
    print " "

    for aBarcode in dataDict.keys():
        print aBarcode, dataDict[aBarcode]
        if (len(dataDict[aBarcode]) > 1):

            print " need to compress this: ", dataDict[aBarcode]
            numVec = len(dataDict[aBarcode])
            numSamp = len(dataDict[aBarcode][0])

            ## numVec is the number of different samples-worth-of-data that you
            ## somehow need to compress ... numSamp is the number of values in each vector
            print "     numVec = %d    numSamp = %d " % ( numVec, numSamp )
            newVec = [0] * numSamp
            sumVec = [0] * numSamp
            countV = [0] * numSamp

            for iSamp in range(numSamp):

                print "         allNAs %d    intFlags %d   fltFlags %d    ynFlags %d " % \
                    (  allNAs[iSamp], intFlags[iSamp], fltFlags[iSamp], ynFlags[iSamp] )

                ## if they are all NAs, then nothing needs doing ...
                if ( allNAs[iSamp] ): 
                    print " --> all NA, nothing to do ... "
                    newVec[iSamp] = "NA"
                    continue

                ## also, if they are all the same (disregarding NAs), we get off easy ...
                ## --> we'll also disregard "Other" and consider that equivalent to NA ...
                allSame = 1
                ## first, find the first non-NA value ...
                oneVal = "NA"
                for iVec in range(numVec):
                    if ( dataDict[aBarcode][iVec][iSamp] != "NA" ): 
                        if ( dataDict[aBarcode][iVec][iSamp] != "Other" ):
                            oneVal = dataDict[aBarcode][iVec][iSamp]
                if ( oneVal == "NA" ):
                    newVec[iSamp] = "NA"
                    continue

                print " might they all be the same? ", oneVal
                for iVec in range(numVec):
                    if ( dataDict[aBarcode][iVec][iSamp] != "NA" ):
                        if ( dataDict[aBarcode][iVec][iSamp] != "Other" ):
                            if ( dataDict[aBarcode][iVec][iSamp] != oneVal ):
                                allSame = 0
                if ( allSame ):
                    print " --> all the same, nothing to do ... ", oneVal
                    newVec[iSamp] = oneVal
                    continue

                ## next, if they are all numbers, we'd like to do some math
                if ( intFlags[iSamp] or fltFlags[iSamp] ):
                    print " we should have all numbers now! "
                    numV = 0
                    sumV = 0
                    for iVec in range(numVec):
                        print aBarcode, iVec, iSamp, dataDict[aBarcode][iVec][iSamp]
                        curVal = dataDict[aBarcode][iVec][iSamp] 
                        if ( curVal != "NA" ):
                            numV += 1
                            sumV += float(curVal)
                        if ( numV > 0 ):
                            if ( intFlags[iSamp] ):
                                newVec[iSamp] = int ( float(sumV)/float(numV) + 0.5 )
                            if ( fltFlags[iSamp] ):
                                newVec[iSamp] = ( float(sumV)/float(numV) )
                        else:
                            newVec[iSamp] = "NA"
                        continue

                else:
                    print " WARNING: may need to concatenate strings ..."
                    uList = []
                    for iVec in range(numVec):
                        print aBarcode, iVec, iSamp, dataDict[aBarcode][iVec][iSamp]
                        if ( dataDict[aBarcode][iVec][iSamp] not in uList ):
                            uList += [ dataDict[aBarcode][iVec][iSamp] ]
                    print uList
                    if ( len(uList) == 1 ): 
                        newStr = uList[0]
                    else:
                        newStr = ""
                        for ii in range(len(uList)):
                            newStr += uList[ii]
                            if ( ii < len(uList)-1 ): newStr += "; "
                    print newStr
                    newVec[iSamp] = newStr


            print " setting vector to the newVec ... "
            dataDict[aBarcode] = [newVec]
            print " --> now this: ", dataDict[aBarcode]

    # and finally we can write it out ...

    print " "
    print " time to write output ... ", numTokens, outFile, allNAs, intFlags, fltFlags
    print hdrTokens

    numW1 = 0

    print " "
    print hdrTokens
    fhOut.write("bcr_patient_barcode")
    for iTok in range(1, numTokens):
        if (allNAs[iTok - 1]):
            continue
        if (intFlags[iTok - 1] or fltFlags[iTok - 1]):
            fhOut.write("\tN:SAMP:%s" % hdrTokens[iTok])
            numW1 += 1
        else:
            fhOut.write("\tC:SAMP:%s" % hdrTokens[iTok])
            numW1 += 1
    fhOut.write("\n")

    if ( numW1 < 1 ):
        print " ERROR ??? nothing written out ??? ", numW1, outFile
        fhOut.close()
        sys.exit(-1)

    barcodeList = dataDict.keys()
    barcodeList.sort()
    for aBarcode in barcodeList:
        numW2 = 0
        print aBarcode, dataDict[aBarcode]
        fhOut.write("%s" % aBarcode)
        for iTok in range(1, numTokens):
            if (allNAs[iTok - 1]):
                continue
            if ( dataDict[aBarcode][0][iTok - 1] == "NA" ):
                fhOut.write("\tNA")
                numW2 += 1
            elif ( intFlags[iTok - 1] ):
                fhOut.write("\t%d" % int(dataDict[aBarcode][0][iTok - 1]) )
                numW2 += 1
            elif ( fltFlags[iTok - 1] ):
                fhOut.write("\t%.2f" % float(dataDict[aBarcode][0][iTok - 1]) )
                numW2 += 1
            else:
                fhOut.write("\t%s" % str(dataDict[aBarcode][0][iTok - 1]) )
                numW2 += 1
        fhOut.write("\n")
        if ( numW2 != numW1 ):
            print " ERROR ??? number of tokens written doesn't match ??? ", numW1, numW2
            fhOut.close()
            sys.exit(-1)

    fhOut.close()

    print " "
    print " ------------------------------------------- "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
