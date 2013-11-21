'''
Created on Sep 13, 2013

@author: michael
'''
import argparse
from datetime import datetime

import miscTCGA
import new_Level3_matrix_MM28may13
import resegment
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this is Timo's resegmentation code(mostly) with numpy improvements by mm


def _resegmentCNdata(sampleList, chr2data, chr2maxcoord, steplength=1000, cutFrac=0.01):
    # when we get to this point, we have:
    # sampleList: list of sample barcodes, eg TCGA-74-6575-01A-11D-1842-01
    # dataMatrix: will be the final output with the transposed contents of newMatrix
    # steplength: bin size, eg 1000 bp
    # cutFrac:    fraction to keep, eg 0.01
    start = datetime.now()
    print start, "in _resegmentCNdata() ... ", len(sampleList), steplength, cutFrac
    if (0):
        print sampleList[:5], sampleList[-5:]
        print chr2data['1'][0].keys()[0], '=', chr2data['1'][0][chr2data['1'][0].keys()[0]]
        print chr2data['1'][0].keys()[-1], '=', chr2data['1'][0][chr2data['1'][0].keys()[-1]]
        print chr2data['10'][0].keys()[0], '=', chr2data['10'][0][chr2data['10'][0].keys()[0]]
        print chr2data['10'][0].keys()[-1], '=', chr2data['10'][0][chr2data['10'][0].keys()[-1]]
        print chr2data['Y'][0].keys()[0], '=', chr2data['Y'][0][chr2data['Y'][0].keys()[0]]
        print chr2data['Y'][0].keys()[-1], '=', chr2data['Y'][0][chr2data['Y'][0].keys()[-1]]

    numSamples = len(sampleList)

    chrNames = [new_Level3_matrix_MM28may13.unifychr(str(x))
                for x in range(1, 25)]
    segList, barcodeList, newMatrix = resegment._resegmentChromosomes(
        chrNames, chr2data, chr2maxcoord, sampleList,
        steplength, cutFrac)
    # now we flip the 'newMatrix' and return it as the output 'dataMatrix'
    numSeg = len(newMatrix[0])
    dataMatrix = [0] * numSeg
    numNA = 0
    for kS in range(numSeg):
        dataMatrix[kS] = [0] * numSamples
        for jS in range(numSamples):
            dataMatrix[kS][jS] = newMatrix[jS][kS]
            if(abs(dataMatrix[kS][jS]) > abs(resegment.NA_VALUE / 2)):
                # print kS, jS, dataMatrix[kS][jS]
                numNA += 1

    print "number of NA samples found while flipping : %i\n" % numNA

    # take a look at the barcodes ... tumor only? mix?
    miscTCGA.lookAtBarcodes(barcodeList)
    end = datetime.now()
    print end, end - start, "RETURNING from resegmentCNdata() ...\n"
    return [seg for seg in segList], barcodeList, dataMatrix

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _readDatumDetails(tokens, sampleIndex, chr2data, chr2maxcoord, steplength):
    aChr = new_Level3_matrix_MM28may13.unifychr(tokens[1])
    iStart = int(tokens[2])
    try:
        iStop = int(tokens[3])
    except:
        try:
            iStop = int(float(tokens[3]))
        except Exception as e:
            raise ValueError(
                "FATAL ERROR: failed to parse segment stop position from <%s> " % tokens[3], e)
    chr2data[aChr][sampleIndex][iStart] = (iStop, float(tokens[-1]))
    maxchrcoord = chr2maxcoord[aChr]
    chr2maxcoord[aChr] = max(maxchrcoord, int(int(iStop) / steplength))

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def _readAllSnpDataFile(fName, include, chr2data, chr2maxcoord, steplength):
    print datetime.now(), "begin readAllSnpDataFile()"

    # read through the file and for each sample, assemble its segments
    sample2segments = {}
    segmentCount = 0
    line = ''
    try:
        with open(fName) as fh:
            # read the header line
            line = fh.readline()
            # and the rest of them
            for line in fh:
                fields = line.strip().split('\t')
                if not include and '0' != fields[0][13]:
                    continue
                segments = sample2segments.setdefault(fields[0], [])
                segments += [fields]
                segmentCount += 1
    except Exception as e:
        msg = " ERROR in readAllSnpDataFile ... "
        if line:
            msg += " problem reading line (%s) %s\n\t%s" % (e, fName, line)
        else:
            msg += " failed to open input file %s: %s!?!?! " % (fName, e)
        raise ValueError(msg)

    print '_readAllSnpDataFile(): %i samples with %i segments' % (len(sample2segments), segmentCount)
    # now create and populate the return data structures
    samples = sample2segments.keys()
    samples.sort()
    for i, sample in enumerate(samples):
        segments = sample2segments[sample]
        for tokens in segments:
            _readDatumDetails(tokens, i, chr2data, chr2maxcoord, steplength)

    print datetime.now(), "end readAllSnpDataFile()"
    return samples


def parseArgs():
    parser = argparse.ArgumentParser(description='get parameters')
    parser.add_argument('--include', '-i', action='store_true')
    parser.add_argument('infile')
    parser.add_argument('outfile')
    args = parser.parse_args()
    print 'args: %s' % (args)

    return args


def main():
    args = parseArgs()
    chr2data = {}
    chr2maxcoord = {}
    for index in range(1, 25):
        chrom = new_Level3_matrix_MM28may13.unifychr(str(index))
        chr2data[chrom] = new_Level3_matrix_MM28may13.AutoVivification()
        chr2maxcoord[chrom] = 0

    steplength = 1000
    sampleList = _readAllSnpDataFile(
        args.infile, args.include, chr2data, chr2maxcoord, steplength)

    cutFrac = 0.02
    resegment.NA_VALUE = -999999
    resegment.NEAR_ZERO = 0.0001
    segList, _, dataMatrix = _resegmentCNdata(
        sampleList, chr2data, chr2maxcoord, steplength, cutFrac)

    try:
        dataD = {}
        dataD['rowLabels'] = segList
        dataD['colLabels'] = sampleList
        dataD['dataMatrix'] = dataMatrix
        dataD['dataType'] = "%s:%s" % ("N", "CNVR")

        newFeatureName = "C:SAMP:" + "cnvrPlatform"
        newFeatureValue = "Genome_Wide_SNP_6"
        dataD = tsvIO.addConstFeature(dataD, newFeatureName, newFeatureValue)

        sortRowFlag = 0
        sortColFlag = 1
        tsvIO.writeTSV_dataMatrix(
            dataD, sortRowFlag, sortColFlag, args.outfile)
    except:
        print " FATAL ERROR: failed to write out any resegmented copy-number data "


if __name__ == '__main__':
    main()
