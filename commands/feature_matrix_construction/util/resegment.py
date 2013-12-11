'''
Created on Aug 13, 2012

@author: michael
'''
from datetime import datetime
import numpy
import traceback

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
stopIndex = 0
valueIndex = 1
NA_VALUE = -999999
NEAR_ZERO = 0.0001

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _prettyPrint(aVec, skipFlag=1):

    if (len(aVec) < 1):
        print "WARNING: in _prettyPrint ... empty vector ..."
        return

    ii = 0
    print " %6d  %8.2f " % (ii, aVec[ii])
    lastVal = aVec[ii]

    for ii in range(1, len(aVec) - 1):
        if (abs(aVec[ii] - lastVal) > 0.1):
            print " %6d  %8.3f " % (ii, aVec[ii])
            lastVal = aVec[ii]
        if (not skipFlag):
            lastVal = (NA_VALUE + NA_VALUE)

    ii = len(aVec) - 1
    print " %6d  %8.2f " % (ii, aVec[ii])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _prettyPrint2(aDict):

    startKeys = aDict.keys()
    startKeys.sort()
    print " number of start keys : ", len(startKeys), startKeys[:3], startKeys[-3:]
    for iStart in startKeys:
        stopKeys = aDict[iStart].keys()
        if (len(stopKeys) != 1):
            print aDict
            raise ValueError(
                " ERROR ??? in _prettyPrint2 ... how can there by multiple stop keys ??? ")
        iStop = stopKeys[0]
        try:
            print " [ (%d,%d) : %.3f ]   " % (int(iStart), int(iStop), aDict[iStart][iStop])
        except Exception as e:
            mess = "ERROR in _prettyPrint2 ???  startKeys: %s contents for current startKey: %i %s stopKeys: %s number of stopKeys: %i\n\t" % \
                (str(startKeys), iStart,
                 str(aDict[iStart]), str(stopKeys), len(aDict[iStart]))
            raise ValueError(mess, e)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _getLocalArrayMean(tv, tvZero):
    # we only want to sum values that are not NA
    b1 = (tv != NA_VALUE)
    num = b1.sum(axis=1, dtype=float)
    # the following would eliminate the need for tvZero but takes 1 1/2 minutes longer for brca
    # sum1 = numpy.where(b1, tv, 0).sum(axis = 1)
    sum1 = tvZero.sum(axis=1)
    # if num[i] == 0, this brings up the following warning but does not raise an exception.
    # 'RuntimeWarning: invalid value encountered in divide'
    # the correct value is calculated for each num[i] != 0
    mu = sum1 / num
    mu[numpy.isnan(mu)] = NA_VALUE
    return (mu, num)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _removeZerosNAs(diffvec):
    # new, shaves off a bit of the over all time --mm 2012-08-06 (note:
    # depends on diffvec being >= 0, otherwise use abs(diffvec))
    if (len(diffvec) < 1):
        raise ValueError('in _removeZerosNAs() ... zero length vector ???')

    notZerosNAs = numpy.logical_and(
        diffvec > NEAR_ZERO, diffvec < abs(NA_VALUE) - 1)
    diffvec_nz = diffvec[notZerosNAs]
    if len(diffvec_nz) < 1:
        _prettyPrint(diffvec)
        raise ValueError("ERROR ???  in _removeZerosNAs() ... %i %i" %
                         (len(diffvec), len(diffvec_nz)))
    return diffvec_nz

    # old
    n1 = len(diffvec)
    if (n1 < 1):
        raise ValueError('in _removeZerosNAs() ... zero length vector ???')

    n0 = 0
    for kk in range(n1):
        if (abs(diffvec[kk]) < NEAR_ZERO):
            n0 += 1
        elif (abs(diffvec[kk]) > (abs(NA_VALUE) - 1)):
            n0 += 1
        else:
            pass

    n2 = n1 - n0
    if (n2 < 10):
        _prettyPrint(diffvec)
        raise ValueError("ERROR ???  in _removeZerosNAs() ... %i %i %i %i" %
                         (len(diffvec), n1, n0, n2))

    diffvec_nz = numpy.zeros(n2)

    nn = 0
    for kk in range(n1):
        if (abs(diffvec[kk]) < 0.0001):
            pass
        elif (abs(diffvec[kk]) > (abs(NA_VALUE) - 1)):
            pass
        else:
            diffvec_nz[nn] = diffvec[kk]
            nn += 1

        # print " returning diffvec_nz ... ", len(diffvec_nz), nn,
        # min(diffvec_nz), max(diffvec_nz)
        return (diffvec_nz)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this used to be done with a single numpy.subtract call but now we need
# to handle the NA_VALUEs ...
##       diffvec[k] = cnvsum[k+1] - cnvsum[k]
##       diffvec = numpy.subtract ( cnvsum[1::1], cnvsum[0:-1:1] )


def _computeFirstDiffVec(cnvsum):
    start = datetime.now()
    # new, shaves off some time --mm 2012-08-06
    na = numpy.logical_or(
        abs(cnvsum[0:-1]) == abs(NA_VALUE), abs(cnvsum[1:]) == abs(NA_VALUE))
    diffvec = numpy.subtract(cnvsum[1:], cnvsum[0:-1])
    diffvec[na] = NA_VALUE
    notNA = (diffvec != NA_VALUE)
    if (0):
        if (max(diffvec[notNA]) > 1000):
            print " ERROR ??? how did we get this value ??? "
            print " "
            for ii in range(len(diffvec)):
                print ii, cnvsum[ii + 1], cnvsum[ii], diffvec[ii]
            raise ValueError(
                "ERROR ??? how did we get this value %f for max value in _computeFirstDiffVec??? " %
                max(diffvec[notNA]))
    print '\t', start, datetime.now(), 'finished _computeFirstDiffVec'
    if 0 == len(diffvec[notNA]):
        minVal = 0
        maxVal = 0
    else:
        minVal = min(diffvec[notNA])
        maxVal = max(diffvec[notNA])

    return (diffvec, minVal, maxVal)

    # old
    minDiff = 999999.
    maxDiff = -999999.
    b0 = (cnvsum == NA_VALUE)
    for kk in range(len(diffvec)):
        # if either of the two values to be differenced are NA, then
        # we set the diffvec value to NA
        if (b0[kk] or b0[kk + 1]):
            diffvec[kk] = NA_VALUE
        # only if we have two valid values do we compute the difference
        else:
            diffvec[kk] = cnvsum[kk + 1] - cnvsum[kk]
            if (minDiff > diffvec[kk]):
                minDiff = diffvec[kk]
            if (maxDiff < diffvec[kk]):
                maxDiff = diffvec[kk]

    if (0):
        if (maxDiff > 1000):
            print " ERROR ??? how did we get this value ??? "
            print " "
            for ii in range(len(diffvec)):
                print ii, cnvsum[ii + 1], cnvsum[ii], diffvec[ii]
            raise ValueError(
                "ERROR ??? how did we get this value %f for max value in _computeFirstDiffVec??? " % maxDiff)

    print '\t', start, datetime.now(), 'finished _computeFirstDiffVec'
    return (diffvec, min(diffvec[notNA]), max(diffvec[notNA]))

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# accumulate the current binned vector into the summed vector ...
# 25may12: changing this to operate on absolute values so that large positive
# values and large negative values don't cancel each other out!!!


def _add2CNVsum(cnvsum, cnvvec):
    cnvvec = abs(cnvvec)
    # first any values in cnvsum that are NA should just be set
    # equal to whatever is coming in (even if it is NA)
    b1 = (cnvsum == abs(NA_VALUE))
    cnvsum[b1] = cnvvec[b1]

    # next, any values in cnvvec that are *not* NA should be
    # added to any values in cnvsum that are *not* NA
    # EXCEPT for any values that were just set in step #1 above!!!
    b2 = (cnvvec != abs(NA_VALUE))
    b3 = (cnvsum != abs(NA_VALUE))
    nb1 = (b1 == False)
    b4 = (b2 & b3 & nb1)
    cnvsum[b4] += cnvvec[b4]

    return (cnvsum)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _validate(start, stopPlus1, length):
    if (stopPlus1 == length):
        stopPlus1 -= 1
    if (start >= stopPlus1):
        return

    if (start < 0):
        # print "ERROR in _copyInto ??? %i %i %i %s" % (len(cnvvec), start,
        # stopPlus1, str(value))
        raise ValueError("ERROR in _copyInto ??? %i %i %i" %
                         (length, start, stopPlus1))
        start = 0
    if (start >= (length - 1)):
        # print " ERROR in _copyInto ??? ", len(cnvvec), start, stopPlus1,
        # value
        raise ValueError("ERROR in _copyInto ??? %i %i %i" %
                         (length, start, stopPlus1))
        start = length - 1
    if (stopPlus1 < 1):
        # print " ERROR in _copyInto ??? ", len(cnvvec), start, stopPlus1,
        # value
        raise ValueError("ERROR in _copyInto ??? %i %i %i" %
                         (length, start, stopPlus1))
        stopPlus1 = 1
    if (stopPlus1 > length):
        # print " ERROR in _copyInto ??? ", len(cnvvec), start, stopPlus1,
        # value
        raise ValueError("ERROR in _copyInto ??? %i %i %i" %
                         (length, start, stopPlus1))
        stopPlus1 = length

    if (start >= stopPlus1):
        raise ValueError("ERROR in _copyInto ??? %i %i %i" %
                         (length, start, stopPlus1))

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _setupSegments(chrName, chr2data, chr2maxcoord, barcodeList, barcode2index, steplength):
    data = chr2data[chrName]
    maxchrcoord = chr2maxcoord[chrName] + 1
    numSamples = len(barcodeList)
    dataTemp = numpy.zeros((numSamples, maxchrcoord))
    dataZero = numpy.zeros((numSamples, maxchrcoord))
    # print ' maxchrcoord : ', maxchrcoord
    # and then allocate a vector of that length, initialized to NA_VALUE
    # this vector will contain the sum, across all segments, of the binned CN
    # values

    # instead of using _copyInto, now uses numpy.repeat().  speeds up code a factor of 12x
    #    cnvsum = numpy.repeat(abs(NA_VALUE), maxchrcoord)
    cnvsum = numpy.repeat(float(abs(NA_VALUE)), maxchrcoord)
    startTime = datetime.now()
    # now we loop over all of the samples (jS: 0 to numSamples-1)
    # and for each sample, loop over all of the segments, sorted by start
    # position
    for jS in range(len(barcodeList)):
        barcode = barcodeList[jS]
        sampleIndex = barcode2index[barcode]
        # print " C      --> looping over %d start keys ... " %(len(startKeys))
        startKeys = data[sampleIndex].keys()
        startKeys.sort()
        ranges = []
        values = []
        zeroedValues = []
        prevAdjStopIndex = -1
# uncomment to compare against former way
#        cnvvec = numpy.repeat(float(NA_VALUE), maxchrcoord)
        for start in startKeys:
            tup = data[sampleIndex][start]
            startcoord = int(int(start) / steplength)  # floor
            stopcoord = int(int(tup[stopIndex]) / steplength)
#            cnvvec = _copyInto(cnvvec, startcoord, stopcoord + 1, tup[valueIndex])
            if (startcoord >= stopcoord + 1):
                continue
            _validate(startcoord, stopcoord + 1, maxchrcoord)
            # print " "
            # print " calling copyInto ... ", startcoord,
            # data[sampleIndex][start]
            if startcoord < prevAdjStopIndex:
                raise ValueError(
                    'need to add support for large overlapping segments. overlap: %i' %
                    startcoord < prevAdjStopIndex)

            endStartOverlap = False
            if startcoord == prevAdjStopIndex:
                endStartOverlap = True

            naStretch = 0
            if 0 <= startcoord - (prevAdjStopIndex + 1):
                naStretch = 1
                if 0 < startcoord - (prevAdjStopIndex + 1):
                    # add in the non-value range
                    values += [NA_VALUE]
                    zeroedValues += [0]
                    if 0 > startcoord - (prevAdjStopIndex + 1):
                        raise ValueError('an NA range has a negative range')
                    ranges += [startcoord - (prevAdjStopIndex + 1)]
            values += [tup[valueIndex]]
            zeroedValues += [tup[valueIndex]]

            if maxchrcoord - 1 == stopcoord:
                # this is to stay compatible with the previous code (which
                # always makes the last segment = NA_VALUE(???NOT SURE WHY?)
                # --mm)
                stopcoord -= 1
            if 0 > stopcoord - (startcoord - naStretch):
                raise ValueError('a range has a negative range')
            ranges += [stopcoord - (startcoord - naStretch)]

            if endStartOverlap and abs(values[-2]) < abs(values[-1]):
                # loop over consecutive small segments and remove them
                while 0 == ranges[-2]:
                    # this happens when a very small segment (less than steplength) occurs and is overlapped
                    # print 'removing range and value (%.4f) before [%.4f,%i]'
                    # % (values[-2], values[-1], ranges[-1])
                    del ranges[-2:-1]
                    del values[-2:-1]
                    del zeroedValues[-2:-1]
                # now adjust the ranges if condition still holds
                if abs(values[-2]) < abs(values[-1]):
                    ranges[-2] -= 1
                    ranges[-1] += 1
                    if 0 > ranges[-2]:
                        raise ValueError('problem creating array for sample index %s: %i %s %i %s.  adjusted range is negative' % (
                            barcodeList[jS], len(values), values, len(ranges), ranges))

            prevAdjStopIndex = stopcoord

        if maxchrcoord - 1 > prevAdjStopIndex:
            # add in the final non-value range
            values += [NA_VALUE]
            zeroedValues += [0]
            ranges += [maxchrcoord - (prevAdjStopIndex + 1)]
        try:
            dataTemp[jS] = numpy.repeat(
                numpy.array(values), numpy.array(ranges))
            dataZero[jS] = numpy.repeat(
                numpy.array(zeroedValues), numpy.array(ranges))
            #mask = dataZero == NA_VALUE
            #dataZero[mask] = 0
        except Exception as e:
            traceback.print_exc(10)
            raise ValueError(
                'problem creating array for sample index %s: %i %s %i %s' %
                (barcodeList[jS], len(values), values, len(ranges), ranges), e)

#        if len(dataTemp[jS]) != len(cnvvec) or not (dataTemp[jS] == cnvvec).all():
#            raise ValueError('new way has different results than old way: %i' % len(dataTemp[jS]) != len(cnvvec))
        cnvsum = _add2CNVsum(cnvsum, dataTemp[jS])

    print '\t', startTime, datetime.now(), 'finished processing labels'
    # end of loop over barcodes ...
    if (0):
        print ' '
        print ' cnvsum : ', len(cnvsum), min(cnvsum), max(cnvsum)
        _prettyPrint(cnvsum)
    return cnvsum, numSamples, dataTemp, dataZero

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _resegmentChr(chrName, dataTuple):
    startChr = datetime.now()
    # when we get to this point, we have:
    # chr2data: a map from chromosome to the data in the files
    # chr2maxcoord: a map from chromosome to the maximum end coordinate in the data
    # newMatrix: the final matrix to add the new segments to
    # barcodeList: the alphabetized list of the samples' barcodes
    # barcode2index: a map from the barcode to the original position of the sample in data
    # steplength: bin size, eg 1000 bp
    # cutFrac:    fraction to keep, eg 0.01

    # chr2data is a layered map to a tuple value: chr2data[chrName][sampleIndex][iStart] = (iStop, float(tokens[self.tokenDatumIndex]))
    # {'1': {'TCGA-06-0189-01A-01D-0236-01': {25534592: (65646460, 0.0325), 72532097: (72543731, 0.855), ...} ...} ...}
    # chr   barcode                          start      stop      value,
    # start      stop      value, ...} ...} ...}

    # newMatrix[i][j] will contain the log2(CN/2) copy-number value for the
    # ith segment for the jth patient, eg: -0.447
    chr2data, chr2maxcoord, barcodeList, barcode2index, steplength, cutFrac = dataTuple

    cnvsum, numSamples, dataTemp, dataZero = _setupSegments(
        chrName, chr2data, chr2maxcoord, barcodeList, barcode2index, steplength)

    # compute the first difference(slope) vector:
    diffvec, minDiff, maxDiff = _computeFirstDiffVec(cnvsum)
    if 0 == len(diffvec):
        print '\tthere were no segment differences in %s' % (cnvsum)
        print datetime.now() - startChr,  'processed chromosome %s.  #segments = %i' % (chrName, 0)
        return [], numpy.zeros((numSamples, 0))

    # sanity check on value range ...
    if (max(abs(minDiff), abs(maxDiff)) > numSamples):
        print "\n************************************ "
        print "WARNING !!! extreme values found ??? \n     numSamples = %6d " % numSamples
        print "     difference vector range : %.1f to %.1f " % (minDiff, maxDiff)
        print "************************************\n"

    if (0):
        print ' '
        print ' diffvec : ', len(diffvec), min(diffvec), max(diffvec)
        _prettyPrint(diffvec)

    # NEW: taking the absolute value here ...
    diffvec = abs(diffvec)
    if 0:
        print ' '
        print ' diffvec : ', len(diffvec), min(diffvec), max(diffvec)
        _prettyPrint(diffvec)

    # print ' '
    # print ' diffvec : ', len(diffvec), min(diffvec), max(diffvec)
    # _prettyPrint(diffvec)
    # remove the zeros and the NAs ...
    diffvec_nz = _removeZerosNAs(diffvec)
    if 0:
        print ' '
        print ' diffvec_nz : ', len(diffvec_nz), min(diffvec_nz), max(diffvec_nz)
        _prettyPrint(diffvec_nz)

    min(diffvec_nz)
    max(diffvec_nz)
    diffvec_nz = numpy.sort(diffvec_nz, axis=0)
    if (0):
        print ' '
        print ' diffvec_nz : ', len(diffvec_nz), min(diffvec_nz), max(diffvec_nz)
        _prettyPrint(diffvec_nz)

    # get the number of rows in diffvec and in diffvec_nz(the first is just the number of
    # bins for this chrosome, and the second is the # of bins with non-zero
    # slope)
    ndiff = diffvec.shape[0]
    # print ndiff, len(diffvec)
    ndiff_nz = diffvec_nz.shape[0]

    # print ndiff_nz, len(diffvec_nz)

    # determine the cutoff beyond which we will create segment boundaries
    # ( hmmmm ... note that this cutoff is being chosen separately for each chromosome )
    cutoff_hi = diffvec_nz[int((1 - cutFrac - cutFrac) * ndiff_nz)]
    print "\tF2 cutoff : ", cutoff_hi, ndiff, ndiff_nz, int(2 * cutFrac * ndiff_nz)

    # print " "
    # print " F3 --> now looping over %d difference bins ... " % ndiff
    # NOTE: when there is a significant difference at the kth bin in diffvec, that means that
    # there was a big jump between the kth and the(k+1)th bin in the original binning
    # of the chromosome
    breakpoints_per_chr = 0
    lastcoord = -1
    segList = []
    cutoff_indices = numpy.where(
        numpy.logical_and(diffvec >= cutoff_hi, diffvec < abs(NA_VALUE) - 1))[0]
    if cutoff_indices[len(cutoff_indices) - 1] != len(diffvec) - 1:
        cutoff_indices = numpy.append(cutoff_indices, len(diffvec) - 1)

    beforeNA_indices = numpy.where(numpy.logical_and(
        diffvec[0:-1] < abs(NA_VALUE), diffvec[1:] == abs(NA_VALUE)))[0] + 1
    # don't use a quick sort because the arrays above will be somewhat sorted
    # already
    cutoff_indices = numpy.sort(numpy.unique(
        numpy.insert(cutoff_indices, len(cutoff_indices), beforeNA_indices)), None, 'Heapsort')

    newMatrix = numpy.zeros((numSamples, len(cutoff_indices)))
    for index in range(len(cutoff_indices)):
        cutoff_index = cutoff_indices[index]
        breakpoints_per_chr += 1
        navalues_indices = numpy.where(
            diffvec[lastcoord + 1:cutoff_index] > abs(NA_VALUE) - 1)[0]
        if 0 < len(navalues_indices):
            startcoord = navalues_indices.max() + 1
        else:
            startcoord = lastcoord + 1

        stopcoord = cutoff_index
        lastcoord = cutoff_index
        startpos = startcoord * steplength
        stoppos = stopcoord * steplength + steplength
        if (cutoff_index < len(diffvec) - 1):
            stoppos -= 1

        # print " F4  cutoff_index=%2d  startcoord=%2d  stopcoord=%2d  startpos=%8d stoppos=%8d " % ( cutoff_index, startcoord, stopcoord, startpos, stoppos )
        # not sure if update is right for diff below
        # print "             difference is significant",
        # diffvec[cutoff_index], startcoord, stopcoord, startpos, stoppos

        # print " F5  looping over barcodes ... ", barcodeList[:5], " ... ",
        # barcodeList[-5:]

        segList += ['N:CNVR::chr' + chrName + ':' +
                    str(startpos) + ':' + str(stoppos) + '::']
        newMatrix[:, index] = _getLocalArrayMean(
            dataTemp[:, startcoord:(stopcoord + 1)], dataZero[:, startcoord:(stopcoord + 1)])[0]
#        newMatrix[:, index] = _getLocalArrayMean(dataTemp[:, startcoord:(stopcoord + 1)], None)[0]
#        for jS in range(numSamples):
            # print " getLocalMean ... ", barcode, chrName, startcoord, stopcoord+1
            # print dataTemp[js][startcoord:(stopcoord+1)]

            # uncomment for debugging statements below
            ## barcode = barcodeList[jS]
            ## sampleIndex = barcode2index[barcode]
            ## data[sampleIndex]['CNV'][startpos][stoppos] = mu
#            if (jS == 0):
#                segName = 'N:CNVR::chr' + chrName + ':' + str(startpos) + ':' + str(stoppos) + '::'
#                segList += [segName]
#            mu, numMu = _getLocalMean(dataTemp[jS][startcoord:(stopcoord + 1)])
#            newMatrix[jS][index] = mu
            # print " --> mu=%f  numMu=%d " % ( mu, numMu )
#            if math.isnan(mu[jS]):
#                newMatrix[jS] += [NA_VALUE]
#            else:
#                newMatrix[jS] += [mu[jS]]
    # end of loop over diffcoord ...

    # print " H   %d breakpoints in chr %s" %(breakpoints_per_chr, chrName)
    # print len(newMatrix), len(newMatrix[0])
    # print len(segList), segList[:10], segList[-10:]

    # print " total number of barcodes : ", numSamples
    # print barcodeList[:4]
    # print barcodeList[-4:]
    # print " "
    # print data[0].keys()
    # print data[0]['CNV'].keys(), chrName
    # print data[0].keys(), chrName
    # print dataTemp[0], chrName
    # print " "
    # print barcodeList[0]
    # _prettyPrint2(data[0]['CNV'])
    # print barcodeList[1]
    # _prettyPrint2(data[1]['CNV'])

    # print " "
    # print " "

    # this is the end of processing for a single chromosome('chrom')
    # sys.exit(-1)
    print datetime.now() - startChr,  'processed chromosome %s.  #segments = %i' % (chrName, len(segList))
    return segList, newMatrix

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _resegmentChromosomes(chrNames, chr2data, chr2maxcoord, sampleList, steplength, cutFrac):
    numSamples = len(sampleList)
    barcodeList = [0] * numSamples
    barcode2index = {}
    for index in range(numSamples):
        barcodeList[index] = sampleList[index]
        barcode2index[sampleList[index]] = index
    barcodeList.sort()

    # the output matrix will initially be samples x segments but will
    # then be flipped just before returning from this function ...
    newMatrix = [[] for x in range(numSamples)]
    segList = []
    dataTuple = (chr2data, chr2maxcoord, barcodeList,
                 barcode2index, steplength, cutFrac)
    for index, chrName in enumerate(chrNames):
        curSegList, curMatrix = _resegmentChr(chrName, dataTuple)
        segList += curSegList
        for index in range(numSamples):
            newMatrix[index] += curMatrix[index].tolist()

    return segList, barcodeList, newMatrix
