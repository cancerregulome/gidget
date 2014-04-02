#!/usr/bin/env python

import miscClin

import datetime
import sys

#------------------------------------------------------------------------------


def noData(aValue):

    # print aValue
    try:
        if (aValue.upper() == "NA"):
            return (1)
        if (aValue.upper() == "NAN"):
            return (1)
    except:
        try:
            fVal = float(aValue)
            return (0)
        except:
            return (0)

    return (0)

#------------------------------------------------------------------------------


def writeARFF(allClinDict, bestKeyOrder, progName, outName):

    if (not outName.endswith(".arff")):
        outName += ".arff"

    print " "
    print " writing output arff file ", outName

    fh = file(outName, 'w')

    # before we get started we want to know which features we are going to write
    # out and their data types ...
    keyTypes = [0] * len(bestKeyOrder)

    # this is not being decided by lookAtKey anymore ...
    useFlags = [1] * len(bestKeyOrder)

    labelLists = [0] * len(bestKeyOrder)
    labelCounts = [0] * len(bestKeyOrder)
    numSkip = 0
    numNumeric = 0
    numNominal = 0
    for ii in range(len(bestKeyOrder)):
        aKey = bestKeyOrder[ii]
        (keyTypes[ii], nCount, nNA, nCard, labelLists[ii],
         labelCounts[ii]) = miscClin.lookAtKey(allClinDict[aKey])
        # print aKey, useFlags[ii], keyTypes[ii], nCount, nNA, nCard
        if (useFlags[ii]):
            if (keyTypes[ii] == 'NUMERIC'):
                numNumeric += 1
            if (keyTypes[ii] == 'NOMINAL'):
                numNominal += 1
        else:
            numSkip += 1

    aKey = bestKeyOrder[0]
    numK = len(allClinDict[aKey])

    # first we write some comments at the top ...
    now = datetime.datetime.now()
    fh.write('%% TCGA clinical data extracted from xml files\n')
    fh.write('%% %s\n' % str(progName))
    # TODO: replease with configurable username!
    fh.write('%% TODO@systemsbiology.org\n')
    fh.write('%% %s\n' % now.strftime("%Y-%m-%d %H:%M"))
    fh.write('%% %d numeric fields, %d nominal fields, %d skipped\n' %
             (numNumeric, numNominal, numSkip))
    fh.write('%% %d examples\n' % numK)
    fh.write('\n')

    # then comes the header information:
    fh.write('@RELATION clinical-test\n')
    fh.write('\n')

    # the ARFF format allows for several different types of attributes:
    # numeric, nominal, string, date, and relational
    # --> for the moment we will only use numeric and nominal

    # so we need to be able to determine, for every key, whether it
    # is 'numeric' or 'nominal'
    for ii in range(len(bestKeyOrder)):
        aKey = bestKeyOrder[ii]
        if (useFlags[ii]):
            fh.write('@ATTRIBUTE %s ' % aKey)
            if (keyTypes[ii] == 'NUMERIC'):
                minVal = 999999
                maxVal = -999999
                for jj in range(len(allClinDict[aKey])):
                    try:
                        xVal = float(allClinDict[aKey][jj])
                        if (minVal > xVal):
                            minVal = xVal
                        if (maxVal < xVal):
                            maxVal = xVal
                    except:
                        doNothing = 1
                fh.write('NUMERIC %% [%d, %d] %d\n' %
                         (int(minVal + 0.499), int(maxVal + 0.499), naCount))
            elif (keyTypes[ii] == 'NOMINAL'):
                fh.write('{')
                for jj in range(len(labelLists[ii])):
                    aLabel = labelLists[ii][jj]
                    fh.write('"%s"' % aLabel)
                    if (jj < (len(labelLists[ii]) - 1)):
                        fh.write(', ')
                fh.write('} %% [ ')
                totCount = 0
                for jj in range(len(labelLists[ii])):
                    fh.write("%d" % labelCounts[ii][jj])
                    totCount += labelCounts[ii][jj]
                    if (jj < (len(labelLists[ii]) - 1)):
                        fh.write(", ")
                naCount = numK - totCount
                fh.write(' ] + %d\n' % naCount)

    fh.write('\n')
    fh.write('@DATA\n')

    # and now we can write the data:
    for kk in range(numK):
        # print " kk=%d ... " % kk
        outLine = ''
        for ii in range(len(bestKeyOrder)):
            if (useFlags[ii]):
                aKey = bestKeyOrder[ii]
                # print aKey
                # print allClinDict[aKey][kk]
                if (noData(allClinDict[aKey][kk])):
                    outLine += '?, '
                else:
                    if (keyTypes[ii] == 'NUMERIC'):
                        try:
                            outLine += ('%s, ' % str(allClinDict[aKey][kk]))
                        except:
                            print ' ERROR ??? ', aKey, kk, allClinDict[aKey][kk]
                            sys.exit(-1)
                    else:
                        try:
                            outLine += ('"%s", ' %
                                        allClinDict[aKey][kk].upper())
                        except:
                            outLine += ('"%s", ' % str(allClinDict[aKey][kk]))
                            # print " WARNING: this field is supposedly not numeric??? ", aKey, kk, allClinDict[aKey][kk]
                            # print allClinDict[aKey]
                            # sys.exit(-1)
        if (outLine.endswith(", ")):
            outLine = outLine[:-2]

        outLine += ("\t\t%% ")
        try:
            outLine += ("%s" % allClinDict['bcr_patient_barcode'][kk])
        except:
            try:
                outLine += ("%s" % allClinDict['C:CLIN:bcr_patient_barcode:::::'][kk])
            except:
                print " ERROR in writeARFF "
                print allClinDict.keys()
                sys.exit(-1)
        fh.write("%s\n" % outLine)

    fh.write('\n')
    fh.close()

#------------------------------------------------------------------------------
