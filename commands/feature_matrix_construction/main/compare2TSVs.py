# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscIO
import tsvIO

import math
import sys


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtHeaderTokens(aTokens):

    patientList = []
    typeDict = {}

    for a in aTokens:
        if (a.upper().startswith("TCGA-")):
            patientID = a[8:12].upper()
            if (patientID not in patientList):
                patientList += [patientID]
            if (len(a) >= 15):
                typeID = a[13:15]
                if (typeID not in typeDict.keys()):
                    typeDict[typeID] = 0
                typeDict[typeID] += 1
            else:
                print " WARNING : no typeID ??? <%s> " % a

    if (len(patientList) > 0):
        print " "
        print " # of unique patients : ", len(patientList)
        print " sample type counts   : ", typeDict
        print " "
        print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lookAtLine(aLine):

    if (1):
        print len(aLine)

        numTab = 0
        numLF = 0
        numCR = 0
        numSpace = 0
        numDigit = 0
        numLetter = 0

        numLinesOut = 0

        i1 = 0
        for ii in range(len(aLine)):
            ordVal = ord(aLine[ii])
            if (1):
                if (ordVal == 9):
                    # this is a tab ...
                    numTab += 1
                elif (ordVal == 10):
                    numLF += 1
                elif (ordVal == 13):
                    numCR += 1
                elif (ordVal == 32):
                    numSpace += 1
                elif ((ordVal >= 48 and ordVal <= 57) or (ordVal == 46)):
                    numDigit += 1
                elif ((ordVal >= 65 and ordVal <= 90) or (ordVal >= 97 and ordVal <= 122)):
                    numLetter += 1
                elif (ordVal < 32 or ordVal > 126):
                    print " %6d     %3d " % (ii, ordVal)
                else:

                    # print " %6d <%s> %3d " % ( ii, aLine[ii], ord ( aLine[ii]
                    # ) )
                    doNothing = 1
            if (ordVal == 13):
                i2 = ii
                # print " --> writing out from %d to %d " % ( i1, i2 )
                # print " <%s> " % aLine[i1:i2]
                numLinesOut += 1
                ## if ( numLinesOut == 5 ): sys.exit(-1)
                ## fhOut.write ( "%s\n" % aLine[i1:i2] )
                i1 = i2 + 1

        print numTab, numLF, numCR, numSpace, numDigit, numLetter
        print numLinesOut

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def findIndex(rowLabels, aLabel):

    ## print " in findIndex ... ", aLabel
    ## print rowLabels[:5]
    aLabel2 = aLabel.lower()

    for ii in range(len(rowLabels)):
        rLabel = oneBetterLabel ( rowLabels[ii] ) 
        rLabel2 = rLabel.lower()
        ## print "         %4d  comparing <%s> and <%s> " % ( ii, rLabel2, aLabel2 )
        if ( rLabel2 == aLabel2 ): return (ii)

    if ( not aLabel.startswith("TCGA-") ):
        print " ??? not found ??? ", aLabel
        print rowLabels[:5]
        print rowLabels[-5:]
        sys.exit(-1)
    return (-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def chopOneFeat ( aLabel, labelTokens ):

    aType = labelTokens[1].lower()

    if ( aType == "gexp" ):
        return ( labelTokens[0] + ":" + labelTokens[1] + ":" + labelTokens[2] + ":::::" + labelTokens[7] )

    if ( aType == "gnab" ):
        return ( labelTokens[0] + ":" + labelTokens[1] + ":" + labelTokens[2] + ":::::" + labelTokens[7] )

    if ( aType == "mirn" ):
        return ( labelTokens[0] + ":" + labelTokens[1] + ":" + labelTokens[2] + ":::::" + labelTokens[7] )

    ## some of the gene-level CNVR features that we got from the Broad
    ## could not get annotated for whatever reason, and so they 
    ## do not have position information and need to rely on the gene symbol
    ## eg:         N:CNVR:ARPM1:::::Gistic
    ## instead of  N:CNVR:AATK:chr17:79091095:79139877:-:Gistic
    ##             0 1    2    3     4        5        6 7
    ## if there is no position information for a CNVR feature, then keep the whole label
    if ( aType == "cnvr" ):
        if ( labelTokens[3] == '' ):
            return ( aLabel )
        else:
            return ( labelTokens[0] + ":" + labelTokens[1] + "::" + labelTokens[3] + ":" \
                   + labelTokens[4] + ":" + labelTokens[5] + "::" + labelTokens[7] )

    if ( aType == "meth" ):
        try:
            splitLast = labelTokens[7].split('_')
        except:
            splitLast = [ '' ]
        return ( labelTokens[0] + ":" + labelTokens[1] + "::::::" + splitLast[0] )

    if ( aType == "rppa" ):
        return ( labelTokens[0] + ":" + labelTokens[1] + "::::::" + labelTokens[7] )

    if ( aType == "clin" ):
        return ( labelTokens[0] + "::" + labelTokens[2] + ":::::" + labelTokens[7] )

    if ( aType == "samp" ):
        return ( labelTokens[0] + "::" + labelTokens[2] + ":::::" + labelTokens[7] )

    print " in chopOneFeat ... ", aLabel
    print labelTokens
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def oneBetterLabel ( oldLabel ):

    if ( 1 ):
        aLabel = oldLabel.lower()
        aTokens = aLabel.split(':')
        if ( len(aTokens) > 3 ):
            if ( 1 ):
                newLabel = chopOneFeat ( aLabel, aTokens ) 
                ## print " from this label <%s> to this: <%s> " % ( aLabel, newLabel )
            else:
                if ( aTokens[1]=="clin"  or  aTokens[1]=="samp" ):
                    newLabel = aLabel[6:]
                    ## print " from this label <%s> to this: <%s> " % ( aLabel, newLabel )
                else:
                    ## print " (a) not changing this label <%s> " % ( aLabel )
                    newLabel = aLabel
        else:
            ## print " (b) not changing this label <%s> " % ( aLabel )
            newLabel = aLabel

    return ( newLabel )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def makeBetterLabels ( originalLabels ):

    betterLabels = []
    for aLabel in originalLabels:
        betterLabels += [ oneBetterLabel ( aLabel ) ]
    betterLabels.sort()

    return ( betterLabels )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def fixBarcodes ( colLabelsA, colLabelsB ):

    ## what are the lengths of the barcodes ?
    aLen = len(colLabelsA[0])
    bLen = len(colLabelsB[0])

    ## make sure that they are consistent
    aConsistent = 1
    for ii in range(len(colLabelsA)):
        if ( len(colLabelsA[ii]) != aLen ):
            aConsistent = 0

    bConsistent = 1
    for ii in range(len(colLabelsB)):
        if ( len(colLabelsB[ii]) != bLen ):
            bConsistent = 0

    ## if they are not consistent, then bail ...
    if ( (aConsistent + bConsistent) != 2 ): return ( colLabelsA, colLabelsB )

    ## if they are consistent, then make them comparable if necessary
    if ( aLen == bLen ): return ( colLabelsA, colLabelsB )

    ## TCGA-BI-A0VS-01
    ## 012345678901234
    changeA = 0
    changeB = 0
    new_aLen = aLen
    new_bLen = bLen

    if ( aLen > bLen ):
        if ( bLen >= 15 ): 
            changeA = 1
            new_aLen = bLen

    if ( bLen > aLen ):
        if ( aLen >= 15 ): 
            changeB = 1
            new_bLen = aLen

    print " change flags : ", changeA, changeB, aLen, bLen, new_aLen, new_bLen

    if ( changeA ):
        for ii in range(len(colLabelsA)):
            colLabelsA[ii] = colLabelsA[ii][:new_aLen]

    if ( changeB ):
        for ii in range(len(colLabelsB)):
            colLabelsB[ii] = colLabelsB[ii][:new_aLen]

    return ( colLabelsA, colLabelsB )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print ' Usage : %s <input TSV #1> <input TSV #2> ' % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    inFileA = sys.argv[1]
    inFileB = sys.argv[2]

    try:
        fhA = file(inFileA, 'r')
        fhA.close()
        fhB = file(inFileB, 'r')
        fhB.close()
    except:
        print " one or the other file does not exist ??? "
        print inFileA
        print inFileB
        sys.exit(-1)

    print " "
    print " reading input files ... : "
    print "     file A : ", inFileA
    print "     file B : ", inFileB
    print " "

    dataA = tsvIO.readTSV(inFileA)
    dataB = tsvIO.readTSV(inFileB)

    if (len(dataA) == 0):
        print " input file A does not exist ??? "
        print inFileA
        sys.exit(-1)

    if (len(dataB) == 0):
        print inFileB
        print " input file B does not exist ??? "
        sys.exit(-1)

    # first take a look at the feature (row) labels ...
    rowLabelsA = makeBetterLabels ( dataA['rowLabels'] )
    rowLabelsB = makeBetterLabels ( dataB['rowLabels'] )

    # and also take a look at the sample (column) labels ...
    ( dataA['colLabels'], dataB['colLabels'] ) = fixBarcodes ( dataA['colLabels'], dataB['colLabels'] )

    print len(rowLabelsA), len(rowLabelsB)
    print rowLabelsA[:2], rowLabelsA[-2:]
    print rowLabelsB[:2], rowLabelsB[-2:]
    print dataA['colLabels'][:2], dataA['colLabels'][-2:]
    print dataB['colLabels'][:2], dataB['colLabels'][-2:]

    numAinB = 0
    featLabelsAnotB = []
    for aLabel in rowLabelsA:
        if (aLabel in rowLabelsB):
            numAinB += 1
        else:
            featLabelsAnotB += [aLabel]

    numBinA = 0
    featLabelsBnotA = []
    for aLabel in rowLabelsB:
        if (aLabel in rowLabelsA):
            numBinA += 1
        else:
            featLabelsBnotA += [aLabel]

    print " "
    print "     --> total # of features in each : %6d  %6d " % (len(rowLabelsA), len(rowLabelsB))
    print "         overlap counts              : %6d  %6d " % (numAinB, numBinA)

    featLabelsAnotB.sort()
    featLabelsBnotA.sort()

    ## print len(featLabelsAnotB), featLabelsAnotB[:5]
    ## print len(featLabelsBnotA), featLabelsBnotA[:5]

    print " "
    if (len(featLabelsAnotB) > 0):
        print " %d labels in A but not in B (string names have been arbitrarily forced to lower-case) : " % (len(featLabelsAnotB))
        for aLabel in featLabelsAnotB:
            print "     feat in A not B: ", aLabel
    else:
        print " NO labels in A but not in B (string names have been arbitrarily forced to lower-case) : "

    print " "
    if (len(featLabelsBnotA) > 0):
        print " %d labels in B but not in A (string names have been arbitrarily forced to lower-case) : " % (len(featLabelsBnotA))
        for aLabel in featLabelsBnotA:
            print "     feat in B not A: ", aLabel
    else:
        print " NO labels in B but not in A (string names have been arbitrarily forced to lower-case) : "

    # and next at the column (sample) labels ...

    # first check the sample ID lengths ...
    colLabelA_len = len(dataA['colLabels'][0])
    colLabelB_len = len(dataB['colLabels'][0])
    minLen = min(colLabelA_len, colLabelB_len)
    if (minLen < colLabelA_len):
        print " NOTE: sample IDs in A will be abbreviated ... eg from <%s> to <%s> " \
            % (dataA['colLabels'][0], dataA['colLabels'][0][:minLen])
    if (minLen < colLabelB_len):
        print " NOTE: sample IDs in B will be abbreviated ... eg from <%s> to <%s> " \
            % (dataB['colLabels'][0], dataB['colLabels'][0][:minLen])

    colLabelsA = []
    for aLabel in dataA['colLabels']:
        colLabelsA += [aLabel[:minLen].upper()]
    colLabelsB = []
    for aLabel in dataB['colLabels']:
        colLabelsB += [aLabel[:minLen].upper()]

    numAinB = 0
    samplesAnotB = []
    for aLabel in colLabelsA:
        if (aLabel in colLabelsB):
            numAinB += 1
        else:
            samplesAnotB += [aLabel]

    numBinA = 0
    samplesBnotA = []
    for aLabel in colLabelsB:
        if (aLabel in colLabelsA):
            numBinA += 1
        else:
            samplesBnotA += [aLabel]

    print " "
    print "     --> total # of samples in each  : %6d  %6d " % (len(colLabelsA), len(colLabelsB))
    print "         overlap counts              : %6d  %6d " % (numAinB, numBinA)

    samplesAnotB.sort()
    samplesBnotA.sort()

    print " "
    if (len(samplesAnotB) > 0):
        print " %d samples in A but not in B (string names have been arbitrarily forced to upper-case) : " % (len(samplesAnotB))
        for aLabel in samplesAnotB:
            print aLabel
    else:
        print " NO samples in A but not in B (string names have been arbitrarily forced to upper-case) : "

    print " "
    if (len(samplesBnotA) > 0):
        print " %d samples in B but not in A (string names have been arbitrarily forced to upper-case) : " % (len(samplesBnotA))
        for aLabel in samplesBnotA:
            print aLabel
    else:
        print " NO samples in B but not in A (string names have been arbitrarily forced to upper-case) : "

    # now, for the features that exist in both, compare the *data* values ...
    print " "
    print " "
    print " "
    print " now checking data values, feature by feature ... "
    print " (based on features in A that are also in B) "

    ## print rowLabelsA[:5]
    ## print featLabelsAnotB[:5]

    for aLabel in rowLabelsA:

        ## print " aLabel = <%s> " % aLabel

        # skip this feature if it is in the A-not-B list ...
        if (aLabel in featLabelsAnotB):
            continue

        # skip binary indicator features since they are generated automatically
        # ...
        if (aLabel[6:9] == ":i("):
            continue

        # get the feature index for each matrix ...
        iA = findIndex(dataA['rowLabels'], aLabel)
        iB = findIndex(dataB['rowLabels'], aLabel)
        ## print " (a) ", aLabel, iA, iB


        # grab the data vector from each matrix ...
        dataVecA = dataA['dataMatrix'][iA]
        dataVecB = dataB['dataMatrix'][iB]
        ## print " the two data vectors : "
        ## print dataVecA
        ## print dataVecB

        numDiff = 0
        numNotNA = 0
        numChangeNA = 0

        sumDiff = 0.
        sumDiff2 = 0.
        sumN = 0

        # now loop over the individual data values for this feature
        ## print " looping jA over %d " % len(dataVecA)
        for jA in range(len(dataVecA)):
            sampleA = dataA['colLabels'][jA]
            ## print jA, sampleA, dataVecA[jA]

            flag_AisNA = 0
            if (str(dataVecA[jA]) == "NA" or str(dataVecA[jA]) == "-999999"):
                ## print " (NA) "
                flag_AisNA = 1

            else:

                jB = findIndex(dataB['colLabels'], sampleA)
                if (jB < 0):
                    ## print " sample <%s> not found in matrix B " % sampleA
                    if (str(dataVecA[jA]) == "NA"):
                        doNothing = 1
                    elif (str(dataVecA[jA]) == "-999999"):
                        doNothing = 1
                    else:
                        numDiff += 1
                else:
                    ## print jA, jB
                    ## print dataVecA[jA], dataVecB[jB]

                    flag_BisNA = 0
                    if (str(dataVecB[jB]) == "NA" or str(dataVecB[jB]) == "-999999"):
                        flag_BisNA = 1

                    if ( flag_AisNA and flag_BisNA ):
                        ## if both of them are NA, then there is nothing to do ...
                        doNothing = 1

                    elif ( flag_AisNA ):
                        ## if A is NA but B is not ... then something has changed ...
                        numChangeNA += 1
                        print " NANA : A is NA but B is not ... ", aLabel, jA, jB, iA, iB, sampleA, dataVecA[jA], dataVecB[jB]

                    elif ( flag_BisNA ):
                        numChangeNA += 1
                        print " NANA : B is NA but A is not ... ", aLabel, jA, jB, iA, iB, sampleA, dataVecA[jA], dataVecB[jB]
                        
                    else:
                        numNotNA += 1

                        if (str(dataVecA[jA]).lower() != str(dataVecB[jB]).lower()):
                            ## print " values are different for sample <%s> : <%s> # vs <%s> " % ( sampleA, str(dataVecA[jA]), str(dataVecB[jB]) )
                            numDiff += 1
                            try:
                                diffVal = float (dataVecA[jA] ) - \
                                    float(dataVecB[jB])
                                if (abs(diffVal) > 99999):
                                    print " ERROR ??? using NA value ??? !!! ", jA, dataVecA[jA], jB, dataVecB[jB]
                                sumDiff += diffVal
                                sumDiff2 += (diffVal * diffVal)
                                sumN += 1
                            except:
                                doNothing = 1

        if (numDiff == 0):
            print " all %4d non-NA values are the same <%s> (%d) {%d} " % (numNotNA, aLabel, len(dataVecA), numChangeNA)
        else:
            if (sumN > 3):
                meanDiff = float(sumDiff) / float(sumN)
                meanDiff2 = float(sumDiff2) / float(sumN)
                sigmDiff = math.sqrt(
                    max((meanDiff2 - (meanDiff * meanDiff)), 0.))
                if (abs(meanDiff) > 0.02 or sigmDiff > 0.02):
                    print " %4d out of %4d non-NA values are different <%s> (%d) {%d} [%d,%.2f,%.2f] " % \
                        (numDiff, numNotNA, aLabel,
                         len(dataVecA), numChangeNA, sumN, meanDiff, sigmDiff)
                else:
                    print " %4d out of %4d non-NA values are different <%s> (%d) {%d} -- but not significantly [%d,%.2f,%.2f] " % \
                        (numDiff, numNotNA, aLabel,
                         len(dataVecA), numChangeNA, sumN, meanDiff, sigmDiff)
            else:
                print " %4d out of %4d non-NA values are different <%s> (%d) {%d} " % (numDiff, numNotNA, aLabel, len(dataVecA), numChangeNA)


    print " "
    print " FINISHED "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
