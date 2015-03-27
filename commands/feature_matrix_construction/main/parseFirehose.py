# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars
import chrArms
import miscMath
import miscTCGA

import numpy
import path
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getDate(dName):

    dateString = dName[-10:]
    try:
        iDate = int(dateString[0:4]) * 10000 + \
                int(dateString[5:7]) * 100 + int(dateString[8:10])
        print " extracting date from <%s> <%s> %d " % ( dName, dateString, iDate )
    except:
        print " WARNING ... failed to extract date from <%s> ??? " % dName, dateString
        iDate = 0
    return (iDate)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMostRecentDir(topDir, cancerList, awgFlag):

    print " in getMostRecentDir ... "
    print topDir
    print cancerList, awgFlag

    d1 = path.path(topDir)
    genDates = []
    awgDates = []

    for d1Name in d1.dirs():

        ## print "     looking at directory name <%s> " % d1Name
        if ( d1Name.endswith("__bkp") ): continue

        if (d1Name.find("analyses") >= 0):
            print "         --> adding gen date <%s> " % getDate(d1Name)
            genDates += [getDate(d1Name)]

        if (len(cancerList) == 1):
            if ( awgFlag == "YES" ):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        awgDates += [getDate(d1Name)]
                        print "         --> adding awg date <%s> " % getDate(d1Name)

    genDates.sort()
    awgDates.sort()

    print genDates
    print awgDates

    lastDir = "NA"

    ## give priority to an AWG run ...
    if ( (awgFlag=="YES") and (len(awgDates)>0) ):

        lastDate = str(awgDates[-1])
        lastDate = lastDate[0:4] + "_" + lastDate[4:6] + "_" + lastDate[6:8]
        print "     using this awg date : ", lastDate

        for d1Name in d1.dirs():
            # give first priority to awg specific run ...
            if (len(cancerList) == 1):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        if (d1Name.endswith(lastDate)):
                            lastDir = d1Name
    
    else:

        lastDate = str(genDates[-1])
        lastDate = lastDate[0:4] + "_" + lastDate[4:6] + "_" + lastDate[6:8]
        print "     using this gen date : ", lastDate
    
        if (lastDir == "NA"):
            for d1Name in d1.dirs():
                if (d1Name.find("analyses") >= 0):
                    if (d1Name.endswith(lastDate)):
                        lastDir = d1Name
    
    print " using firehose outputs from: ", lastDir

    return (lastDir)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCancerDir(topDir, zCancer):

    nextDir = topDir + "/" + zCancer.upper()
    dateString = topDir[-10:]
    nextDir += "/" + dateString[0:4] + dateString[5:7] + dateString[8:10]

    return (nextDir)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getNewClusterNumbers(cMetric):

    numClus = len(cMetric)

    u1 = []
    for aVal in cMetric:
        if (aVal not in u1):
            u1 += [aVal]
    if (len(u1) < numClus):
        print " this will cause problems ... "
        sys.exit(-1)

    u1_s = sorted(u1, reverse=True)
    newNum1 = [-1] * numClus

    for oldC in range(numClus):
        newC = u1_s.index(cMetric[oldC])
        newNum1[oldC] = newC

    return (newNum1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseBestClusFiles(lastDir, outDir, zCancer):

    print " "
    print " "
    print " START: parsing bestclus.txt files from firehose outputs "
    print lastDir
    print outDir
    print " "

    numGot = 0

    # now that we have the most recent firehose run, we loop over all of
    # the Level_4 directories looking for *.bestclus.txt files
    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        if (d2Name.find("Level_4") > 0):

            ## careful never to grab those FFPE-specific runs
            if ( d2Name.find("FFPE") > 0 ): continue

            d3 = path.path(d2Name)
            for fName in d3.files():
                if (fName.endswith("bestclus.txt")):
                    print " >>> got one !!! ", fName
                    numGot += 1

                    # create output file name
                    outName = outDir + getLastBit(d2Name) + ".bestclus.tsv"
                    # print outName

                    if (fName.find("mRNA_Clustering_CNMF") >= 0):
                        clusType = "mRNA_CNMF"
                    elif (fName.find("mRNA_Clustering_Consensus") >= 0):
                        clusType = "mRNA_CC"
                    elif (fName.find("mRNAseq_Clustering_CNMF") >= 0):
                        clusType = "mRNAseq_CNMF"
                    elif (fName.find("mRNAseq_Clustering_Consensus") >= 0):
                        clusType = "mRNAseq_CC"
                    elif (fName.find("miR_Clustering_CNMF") >= 0):
                        clusType = "miR_CNMF"
                    elif (fName.find("miRseq_Clustering_CNMF") >= 0):
                        clusType = "miRseq_CNMF"
                    elif (fName.find("miRseq_Mature_Clustering_CNMF") >= 0):
                        clusType = "miRseq_Mature_CNMF"
                    elif (fName.find("miR_Clustering_Consensus") >= 0):
                        clusType = "miR_CC"
                    elif (fName.find("miRseq_Clustering_Consensus") >= 0):
                        clusType = "miRseq_CC"
                    elif (fName.find("miRseq_Mature_Clustering_Consensus") >= 0):
                        clusType = "miRseq_Mature_CC"
                    elif (fName.find("Methylation_Clustering_CNMF") >= 0):
                        clusType = "meth_CNMF"
                    elif (fName.find("Methylation_Clustering_Consensus") >= 0):
                        clusType = "meth_CC"
                    elif (fName.find("RPPA_Clustering_CNMF") >= 0):
                        clusType = "RPPA_CNMF"
                    elif (fName.find("RPPA_Clustering_Consensus") >= 0):
                        clusType = "RPPA_CC"
                    elif (fName.find("CopyNumber_Clustering_CNMF_arm") >= 0):
                        clusType = "cnvr_CNMF_arm"
                    ## elif (fName.find("CopyNumber_Clustering_CNMF.Level_4") >= 0):
                    elif (fName.find("CopyNumber_Clustering_CNMF_thresholded.Level_4") >= 0):
                        clusType = "cnvr_CNMF"
                    else:
                        print " --> failed to find magic string ... skipping ... "
                        continue
                        if ( 0 ):
                            print " ERROR in parseBestClusFiles ... failed to find magic string ??? "
                            print fName
                            print d2Name
                            sys.exit(-1)

                    # 03may13 ... need to chop up the filename and use some information
                    # from the filename for the feature name ...
                    nameTokens = fName.split('/')
                    nameTokens = nameTokens[-1].split('.')
                    namePrefix = nameTokens[0]
                    print " (a) namePrefix : ", namePrefix, nameTokens

                    # first I'm going to read in all of the cluster information
                    # so that I can rename the clusters if I want to ...
                    fhIn = file(fName)
                    print "     reading in <%s> " % fName
                    aLine = fhIn.readline()
                    aLine = fhIn.readline()

                    dataDict = {}
                    done = 0
                    iMax = -999
                    iMin = 999

                    print " reading input file ... "

                    while not done:
                        aLine = fhIn.readline()
                        aLine = aLine.strip()
                        tokenList = aLine.split('\t')

                        print " tokenList : ", tokenList
                        if (len(tokenList) != 3):
                            done = 1

                        else:
                            # sanity checking that these tokens look correct
                            # ...
                            goodData = 1
                            aBarcode = miscTCGA.fixTCGAbarcode (tokenList[0], zCancer)

                            if (aBarcode.startswith("TCGA")):
                                try:
                                    iClus = int(tokenList[1])
                                    sVal = float(tokenList[2])
                                except:
                                    goodData = 0
                            else:
                                goodData = 0

                            if not goodData:
                                print " ERROR ??? these values do not look right ??? "
                                print tokenList
                                sys.exit(-1)

                            # found some invalid barcodes in one of these files ...
                            # 01234567890123456789
                            # TCGA-A6-2672-01-Y
                            # 01234567890123456789012345678
                            # TCGA-A6-2678-01A-01D-1549-01

                            if (len(aBarcode) < 16):
                                print " trying to get a good barcode ... ", aBarcode
                                aBarcode = miscTCGA.get_tumor_barcode(aBarcode)
                                print " is this one good ??? ", aBarcode
                            else:
                                if (len(aBarcode) > 16):
                                    aBarcode = aBarcode[:16]
                                    if ( aBarcode[15] == "-" ):
                                        aBarcode = miscTCGA.get_tumor_barcode(aBarcode[:15])

                            print " --> aBarcode : ", aBarcode

                            if (aBarcode in dataDict.keys()):
                                if (sVal > dataDict[aBarcode][1]):
                                    dataDict[aBarcode] = (iClus, sVal)
                            else:
                                print " adding to dataDict ... ", aBarcode, iClus, sVal
                                dataDict[aBarcode] = (iClus, sVal)

                            if (iMin > iClus): iMin = iClus
                            if (iMax < iClus): iMax = iClus

                    fhIn.close()

                    # now let's look at all of the clusters and see how they
                    # rank ...
                    if (iMin != 1):
                        print " ERROR ??? shouldn't there be a cluster #1 ??? ", iMin, iMax
                        sys.exit(-1)
                    numClus = iMax - iMin + 1
                    print " cluster indices ... ", iMin, iMax, numClus
                    print " dataDict length = ", len(dataDict)

                    sumSV = [0] * numClus
                    numTot = [0] * numClus
                    numPos = [0] * numClus

                    cMetric = [0] * numClus

                    for aKey in dataDict.keys():

                        iClus = dataDict[aKey][0]
                        sVal = dataDict[aKey][1]
                        print " looping over dataDict ... ", aKey, iClus, sVal
                        sumSV[iClus - 1] += sVal
                        numTot[iClus - 1] += 1
                        if (sVal > 0):
                            numPos[iClus - 1] += 1

                    for iClus in range(numClus):
                        print " cluster metrics ... ", iClus, sumSV[iClus], numTot[iClus], numPos[iClus]
                        metric1 = sumSV[iClus] / float(numTot[iClus])
                        metric2 = float(numPos[iClus]) / float(numTot[iClus])
                        cMetric[iClus] = metric1 + metric2 + metric2

                    cMetric_s = sorted(cMetric, reverse=True)

                    reNumber = 0
                    if (0):
                        # turning off cluster renumbering (15aug13)
                        if (cMetric != cMetric_s):
                            print "         clusters should be renumbered ... "
                            reNumber = 1

                    if (reNumber):
                        reNum = getNewClusterNumbers(cMetric)
                        print "         --> ", reNum
                        for aKey in dataDict.keys():
                            iClus = dataDict[aKey][0]
                            sVal = dataDict[aKey][1]
                            jClus = reNum[iClus - 1] + 1
                            # print " old cluster #%d --> new cluster #%d " % (
                            # iClus, jClus )
                            if (jClus < 1 or jClus > numClus):
                                print " ERROR in mapping to new cluster numbers ??? ", iClus, jClus
                                sys.exit(-1)
                            dataDict[aKey] = (jClus, sVal)

                    fhOut = file(outName, 'w')
                    print "     writing out <%s> " % outName
                    # the cluster IDs are written as C1, C2, etc and are categorical SAMP features
                    # and the silhouette values are written as floating point values and are
                    # numerical SAMP features
                    fhOut.write(
                        "bcr_patient_barcode\tC:SAMP:%s_%s_%d::::\tN:SAMP:%s_%s_%d_sv::::\n" %
                        (namePrefix, clusType, numClus, namePrefix, clusType, numClus))
                    for aKey in dataDict.keys():
                        iClus = dataDict[aKey][0]
                        sVal = dataDict[aKey][1]
                        fhOut.write("%s\tC%d\t%6.3f\n" %
                                    (aKey, iClus, sVal))
                    fhOut.close()

    print " "
    print " DONE: parsing bestclus.txt files from firehose outputs (%d files) " % numGot
    if (numGot == 0):
        print " ERROR ??? no bestclus.txt files found ??? "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def parseMutSig_CountsRatesFile(inName, outName):

    print " "
    print " "
    print " START: parsing MutSig Counts & Rates file from firehose outputs "
    print inName
    print " "

    fhIn = file(inName)
    print "     reading in <%s> " % inName
    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)

    ## updating this nasty hack of a function on 09feb2015 ... because there is 
    ## once again another version of MutSig ...
    ##          to recap: MutSig1.5 has 10 columns \  and are
    ##                    MutSig2.0 has 10 columns /  the same
    ##                    MutSigCV  has 13 columns
    ##                    MutSig2CV has 22 columns

    if ((numTokens != 10) and (numTokens != 13) and (numTokens !=22) ):
        print " ERROR ??? unexpected number of hdrTokens ??? ", numTokens
        print hdrTokens
        sys.exit(-1)

    print "         numTokens = %d " % numTokens

    # check that the hdrTokens are as we expect ... "
    goodData = 1
    if (numTokens == 10):
        if (hdrTokens[2] != "name"):
            goodData = 0
        if (hdrTokens[7] != "rate_dbsnp"):
            goodData = 0
        if (hdrTokens[8] != "rate_sil"):
            goodData = 0
        if (hdrTokens[9] != "rate_non"):
            goodData = 0
    elif (numTokens == 13):
        if (hdrTokens[0] != "name"):
            goodData = 0
        if (hdrTokens[11] != "rate_sil"):
            goodData = 0
        if (hdrTokens[12] != "rate_non"):
            goodData = 0
    elif (numTokens == 22):
        if (hdrTokens[0] != "name"):
            goodData = 0
        if (hdrTokens[13] != "rate_sil"):
            goodData = 0
        if (hdrTokens[14] != "rate_non"):
            goodData = 0
        if (hdrTokens[15] != "rate_tot"):
            goodData = 0


    if (not goodData):
        print " ERROR ??? unexpected hdrTokens ??? ", numTokens
        print hdrTokens
        sys.exit(-1)

    fhOut = file(outName, 'w')
    print "     writing out <%s> " % outName
    if (numTokens == 10):
        fhOut.write(
            "bcr_patient_barcode\tN:SAMP:MutSig_rateDbSnp_perMb:::::\tN:SAMP:MutSig_rateSil_perMb:::::\tN:SAMP:MutSig_rateNon_perMb:::::\tN:SAMP:MutSig_rateTot_perMb:::::\tB:SAMP:MutSig_HiMut_bit:::::\n")
    elif (numTokens == 13):
        fhOut.write(
            "bcr_patient_barcode\tN:SAMP:MutSig_rateSil_perMb:::::\tN:SAMP:MutSig_rateNon_perMb:::::\tN:SAMP:MutSig_rateTot_perMb:::::\tB:SAMP:MutSig_HiMut_bit:::::\n")
    elif (numTokens == 22):
        fhOut.write(
            "bcr_patient_barcode\tN:SAMP:MutSig_rateSil_perMb:::::\tN:SAMP:MutSig_rateNon_perMb:::::\tN:SAMP:MutSig_rateTot_perMb:::::\tB:SAMP:MutSig_HiMut_bit:::::\n")
    else:
        print " ERROR ??? not writing anything out ??? "
        sys.exit(-1)

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1

        else:

            # they seem to like to change the patient ID here ...
            if (numTokens == 10):
                patientID = tokenList[2]
            elif (numTokens == 13):
                patientID = tokenList[0]
            elif (numTokens == 22):
                patientID = tokenList[0]

            print " checking that patient ID looks ok ... ", patientID

            if (patientID.find("TCGA-") >= 0):
                i1 = patientID.find("TCGA-")
                patientID = patientID[i1:]
                print "     --> (a) change to ", patientID

                if (patientID.find("-Tumor") >= 0):
                    i1 = patientID.find("-Tumor")
                    patientID = patientID[:i1]
                    print "     --> (b) change to ", patientID

            else:
                i1 = patientID.find("-")
                if (i1 < 0):
                    print " ERROR ??? bad patient ID ??? ", patientID
                    sys.exit(-1)
                i2 = patientID.find("-", i1 + 1)
                if (i2 < 0):
                    print " ERROR ??? bad patient ID ??? ", patientID
                    sys.exit(-1)
                patientID = "TCGA" + patientID[i1:]
                print "     --> (c) change to ", patientID

            # as of the 24oct12 analyses, the barcodes seem to look like this:
            # 012345678901234
            # BRCA-A1-A0SO-TP
            print " now here in parseFirehose ... ", patientID
            if (len(patientID) > 12):
                if (patientID[13:15] == "TP"):
                    patientID = patientID[:13] + "01" + patientID[15:]
                elif (patientID[13:15] == "TR"):
                    patientID = patientID[:13] + "02" + patientID[15:]
                elif (patientID[13:15] == "TB"):
                    patientID = patientID[:13] + "03" + patientID[15:]
                elif (patientID[13:15] == "TM"):
                    patientID = patientID[:13] + "06" + patientID[15:]
                elif (patientID[13:15] == "NB"):
                    patientID = patientID[:13] + "10" + patientID[15:]
                elif (patientID[13:15] == "NT"):
                    patientID = patientID[:13] + "11" + patientID[15:]
                else:
                    try:
                        tumorType = int(patientID[13:15])
                    except:
                        print " ERROR in parseFirehose !!! invalid patientID ??? ", patientID

                print "     --> (e) change to ", patientID
                if ( len(patientID) > 16 ):
                    patientID = patientID[:16]
                    print "     --> (f) change to ", patientID

            if (len(patientID) < 16):
                print "     --> looking for a longer barcode ... "
                patientID = miscTCGA.get_tumor_barcode(patientID)
                print "     --> (d) change to ", patientID

            try:
                if (numTokens == 10):
                    rateDbSnp = float(tokenList[7])
                    rateSil = float(tokenList[8])
                    rateNon = float(tokenList[9])
                    rateTot = rateDbSnp + rateSil + rateNon
                elif (numTokens == 13):
                    ## print " WARNING : no dbSNP rate column "
                    rateDbSnp = 0.
                    rateSil = float(tokenList[11])
                    rateNon = float(tokenList[12])
                    rateTot = rateSil + rateNon
                elif (numTokens == 22):
                    ## print " WARNING : no dbSNP rate column "
                    rateDbSnp = 0.
                    rateSil = float(tokenList[13])
                    rateNon = float(tokenList[14])
                    rateTot = float(tokenList[15])
                else:
                    print " wrong number of token ??? ", numTokens
                    print tokenList
                    sys.exit(-1)
            except:
                print " ERROR ??? could not get mutation rate ??? "
                print tokenList
                sys.exit(-1)

            rateDbSnp_perMb = rateDbSnp * 1000000.
            rateSil_perMb = rateSil * 1000000.
            rateNon_perMb = rateNon * 1000000.
            rateTot_perMb = rateTot * 1000000.

            # this threshold is set somewhat arbitrarily at 10 ...
            # setting it back to 10 ... 25apr13
            rate_bit = int(rateNon_perMb >= 10.)

        print " and ready to write out now ... ", patientID

        if (numTokens == 10):
            fhOut.write("%s\t%7.3f\t%7.3f\t%7.3f\t%7.3f\t%d\n" %
                        (patientID, rateDbSnp_perMb, rateSil_perMb, rateNon_perMb, rateTot_perMb, rate_bit))
        elif (numTokens == 13):
            fhOut.write("%s\t%7.3f\t%7.3f\t%7.3f\t%d\n" %
                        (patientID, rateSil_perMb, rateNon_perMb, rateTot_perMb, rate_bit))
        elif (numTokens == 22):
            fhOut.write("%s\t%7.3f\t%7.3f\t%7.3f\t%d\n" %
                        (patientID, rateSil_perMb, rateNon_perMb, rateTot_perMb, rate_bit))

    fhIn.close()
    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this file comes in with the columns being the patients (again with the
# the messed up TCGA barcode), and the rows are the significantly mutated
# genes, so when I write it back out it will be rotated ...


def parseMutSig_SampleSigGeneFile(inName, outName):

    fhIn = file(inName)
    print "     reading in <%s> " % inName

    # the first line should have the word "gene" followed by a bunch
    # of patient IDs
    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)

    if (hdrTokens[0] != "gene"):
        print " ERROR ??? unexpected hdrTokens ??? ", len(hdrTokens)
        print hdrTokens
        sys.exit(-1)

    patientIDs = []
    for ii in range(1, numTokens):
        oneID = hdrTokens[ii]
        i1 = oneID.find("-")
        if (i1 < 0):
            print " ERROR ??? bad patient ID ??? ", oneID
            sys.exit(-1)
        i2 = oneID.find("-", i1 + 1)
        if (i2 < 0):
            print " ERROR ??? bad patient ID ??? ", oneID
            sys.exit(-1)
        patientIDs += ["TCGA" + oneID[i1:]]

    # next we need to grab all of the significantly mutated genes
    mutDict = {}

    minVal = 99
    maxVal = -99
    maxSumMut = 0

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1

        else:
            geneName = tokenList[0]
            mutDict[geneName] = tokenList[1:]

            sumMut = 0
            for ii in range(len(patientIDs)):
                mutCount = int(mutDict[geneName][ii])
                if (minVal > mutCount):
                    minVal = mutCount
                if (maxVal < mutCount):
                    maxVal = mutCount
                sumMut += (mutCount > 0)

            if (maxSumMut < sumMut):
                mostMutGene = geneName
                maxSumMut = sumMut

    fhIn.close()

    # now we're ready to write out the output file ...
    print " writing output file ", outName
    fhOut = file(outName, 'w')

    # first comes the header row ...
    outLine = "bcr_patient_barcode"
    geneList = mutDict.keys()
    geneList.sort()
    for aGene in geneList:
        outLine += "\tN:GNAB:%s:::::MutSigN" % aGene
    fhOut.write("%s\n" % outLine)

    for ii in range(len(patientIDs)):
        outLine = "%s" % patientIDs[ii]
        for aGene in geneList:
            mutCount = int(mutDict[aGene][ii])
            outLine += "\t%d" % mutCount
        fhOut.write("%s\n" % outLine)

    fhOut.close()

    print " range of values : ", minVal, maxVal
    print " most mutated gene : ", mostMutGene, maxSumMut

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this file is a ranked list of the most significantly mutated genes ...
# it has 16 columns and we want to filter on the list one, which is
# the q-value ...


def parseMutSig_SigGenesFile(inName, outName):

    fhIn = file(inName, 'r')
    print "     reading in <%s> " % inName

    # the first line should have the word "rank" followed by
    # the rest of the column headers ...
    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)
    print numTokens

    if (hdrTokens[0] != "rank" and hdrTokens[0] != "gene"):
        print " ERROR ??? unexpected hdrTokens ??? ", len(hdrTokens)
        print hdrTokens
        sys.exit(-1)

    # in one version of this file, when the first column is "rank", the columns are:
    # 0 rank
    # 1 gene
    # 2 description
    # 3 N
    # 4 n
    # 5 npat
    # 6 nsite
    # 7 nsil
    # 8 n1
    # 9 n2
    # 10 n3
    # 11 n4
    # 12 n5
    # 13 n6
    # 14 p_classic
    # 15 p_ns_s
    # 16 p_cons
    # 17 p_joint
    # 18 p
    # 19 q

    # and in the "CV" version, when the first column is "gene", the columns are:
    # 0 gene
    # 1 Nnon
    # 2 Nsil
    # 3 Nflank
    # 4 nnon
    # 5 npat
    # 6 nsite
    # 7 nsil
    # 8 nflank
    # 9 nnei
    # 10 fMLE
    # 11 p
    # 12 score
    # 13 time
    # 14 q

    # in the MutSig1.5 version, here are the columns:
    # 0 rank
    # 1 gene
    # 2 description
    # 3 N
    # 4 n
    # 5 npat
    # 6 nsite
    # 7 nsil
    # 8 n1
    # 9 n2
    # 10 n3
    # 11 n4
    # 12 n5
    # 13 n6
    # 14 p_ns_s
    # 15 p
    # 16 q

    fhOut = file(outName, 'w')
    print "     writing out <%s> " % outName
    done = 0
    numOut = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1
            continue

        pString = "NADA"
        if (hdrTokens[0] == "rank"):
            if (numTokens >= 19):
                pString = tokenList[18]
            elif (numTokens == 17):
                pString = tokenList[15]
        elif (hdrTokens[0] == "gene"):
            pString = tokenList[11]

        if (pString == "NADA"):
            print " ERROR in parseMutSig_SigGenesFile ... "
            print hdrTokens
            print tokenList
            sys.exit(-1)

        try:
            pValue = float(pString)
        except:
            if (pString.startswith("<")):
                pValue = float(pString[1:])
            else:
                print " ERROR parsing p value ??? ", pString
                sys.exit(-1)

        if (hdrTokens[0] == "rank"):
            if (pValue <= 0.01):
                if (numTokens >= 19):
                    fhOut.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                                (tokenList[
                                    1], tokenList[
                                    3], tokenList[4], tokenList[5],
                                 tokenList[6], tokenList[7], tokenList[18], tokenList[19]))
                elif (numTokens == 17):
                    fhOut.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                                (tokenList[
                                    1], tokenList[
                                    3], tokenList[4], tokenList[5],
                                 tokenList[6], tokenList[7], tokenList[15], tokenList[16]))
                numOut += 1
        elif (hdrTokens[0] == "gene"):
            if (pValue <= 0.01):
                fhOut.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                            (tokenList[
                                0], tokenList[1], tokenList[2], tokenList[5],
                             tokenList[6], tokenList[7], tokenList[11], tokenList[14]))
                numOut += 1

    fhOut.close()
    fhIn.close()

    print " --> number of significantly mutated genes : ", numOut


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this is the top-level driver for parsing the MutSig files -- it calls
# other function to handle each individual file

def parseMutSigFiles(lastDir, outDir, MSverString):

    print " "
    print " START: parsing MutSig files from firehose outputs ", MSverString
    print " "
    numGot = 0

    print lastDir

    # now that we have the most recent firehose run, we loop over all of
    # the Level_4 directories looking for MutSig files
    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        print "     checking in <%s> " % d2Name

        ## if (d2Name.find("Mutation_Significance.Level_4") > 0 or d2Name.find("MutSigNozzleReport1.5.Level_4") > 0):
        if ( d2Name.find(MSverString) >= 0  and  d2Name.find("Level_4") >= 0 ):

            ## careful never to grab those FFPE-specific runs
            if ( d2Name.find("FFPE") > 0 ): continue

            d3 = path.path(d2Name)
            for fName in d3.files():

                # the first file we are interested in is the
                # patients.counts_and_rates file ...
                if ( fName.endswith("patients.counts_and_rates.txt") or
                     fName.endswith("patient_counts_and_rates.txt") ):
                    inName = fName
                    print " >>> got one !!! ", fName
                    numGot += 1
                    outName = outDir + \
                        getLastBit(d2Name) + ".patients.counts_and_rates.tsv"
                    parseMutSig_CountsRatesFile(inName, outName)

                # the next file we're interested in is sample_sig_gene_table.txt file
                # 20dec udpate: this file isn't in the MutSig outputs anymore and we
                # we don't really want it anyway, Brady's mutation bits are
                # better
                if (0):
                    if (fName.endswith("sample_sig_gene_table.txt")):
                        inName = fName
                        outName = outDir + \
                            getLastBit(d2Name) + ".sample_sig_gene_table.tsv"
                        parseMutSig_SampleSigGeneFile(inName, outName)

                # 25jun12 update: now we want to grab the ".sig_genes.txt"
                # file and get a list of the most significantly mutated genes
                if (fName.endswith(".sig_genes.txt")):
                    inName = fName
                    outName = outDir + getLastBit(d2Name) + ".sig_genes.txt"
                    parseMutSig_SigGenesFile(inName, outName)

    print " "
    print " DONE: parsing MutSig files from firehose outputs (%d files) " % numGot
    if (numGot == 0):
        print " ERROR ??? no MutSig files found ??? "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getChromosomeName(aString):
    i1 = aString.find(":")
    return (aString[:i1])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getStartStop(aString):
    i1 = aString.find(":")
    i2 = aString.find("-", i1)
    i3 = aString.find("(", i2)
    if (i3 < 0):
        i3 = len(aString)

    iStart = int(aString[i1 + 1:i2])
    iStop = int(aString[i2 + 1:i3])
    return (iStart, iStop)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def makeGisticFeatureName(
    namePrefix, roiName, cytoName, widePeakString, peakString,
        regionString, threshString):

    if (0):
        print " in makeGisticFeatureName "
        print roiName
        print cytoName
        print widePeakString
        print peakString
        print regionString
        print threshString

    peakString = peakString.strip()
    chrName = getChromosomeName(peakString)
    ## wideBounds = getStartStop ( widePeakString )
    peakBounds = getStartStop(peakString)
    ## regionBounds = getStartStop ( regionString )

    if (threshString == "Actual Copy Change Given"):
        featName = "N:CNVR:%s:%s:%d:%d::%s_Gistic_ROI_r_" % (
            cytoName.strip(), chrName, peakBounds[0], peakBounds[1], namePrefix)
    elif (threshString.startswith("0:")):
        featName = "C:CNVR:%s:%s:%d:%d::%s_Gistic_ROI_d_" % (
            cytoName.strip(), chrName, peakBounds[0], peakBounds[1], namePrefix)
    else:
        print " ERROR in makeGisticFeatureName ??? ", threshString
        sys.exit(-1)

    if (roiName.startswith("Amp")):
        featName += "amp"
    elif (roiName.startswith("Del")):
        featName += "del"
    else:
        print " unexpected ROI name ??? <%s> " % roiName
        sys.exit(-1)

    if (0):
        print " returning : <%s> " % featName
    return (featName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseGistic_AllDataByGenesFile(inName, outName):

    # 012345678901234567890123456789
    # gdac.broadinstitute.org_SKCM-All_Metastatic.CopyNumber_Gistic2.Level_4.2013050200.0.0
    nameTokens = inName.split('/')
    nameTokens = (nameTokens[-2][24:]).split('.')
    namePrefix = nameTokens[0]
    print " (d) namePrefix : ", namePrefix, nameTokens

    # 23may13 ... adding this new code ...
    print " in parseGistic_AllDataByGenesFile "
    print " input file name : ", inName
    print " output file name : ", outName

    fhIn = file(inName)
    fhOut = file(outName, 'w')

    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    # print hdrTokens[:10]
    numTokens = len(hdrTokens)
    # print numTokens

    outLine = "N:CNVR"
    for ii in range(3, numTokens):
        outLine += "\t%s" % hdrTokens[ii]
    outLine += "\n"
    fhOut.write(outLine)

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1
            continue

        # print tokenList[:10]
        # print len(tokenList)

        ## outLine = "N:CNVR:%s:::::Gistic_%s" % ( tokenList[0], namePrefix )
        outLine = "N:CNVR:%s:::::Gistic" % (tokenList[0])
        for ii in range(3, numTokens):
            outLine += "\t%s" % tokenList[ii]
        outLine += "\n"
        fhOut.write(outLine)

    fhIn.close()
    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseGistic_LesionsFile(inName, outName):

    # 03may13 ... need to chop up the filename and use some information
    # from the filename for the feature name ...

    # 012345678901234567890123456789
    # gdac.broadinstitute.org_SKCM-All_Metastatic.CopyNumber_Gistic2.Level_4.2013050200.0.0
    nameTokens = inName.split('/')
    nameTokens = (nameTokens[-2][24:]).split('.')
    namePrefix = nameTokens[0]
    print " (b) namePrefix : ", namePrefix, nameTokens

    fhIn = file(inName)
    print "     reading in <%s> " % inName

    # this file has 9 columns that give detailed information for each row
    # and then after that come the sampleIDs (with full barcodes)

    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)
    numSamples = numTokens - 9

    # sanity check the header tokens a bit ...
    goodData = 1
    if (hdrTokens[0] != "Unique Name"):
        goodData = 0
    if (hdrTokens[1] != "Descriptor"):
        goodData = 0
    if (hdrTokens[2] != "Wide Peak Limits"):
        goodData = 0
    if (hdrTokens[3] != "Peak Limits"):
        goodData = 0
    if (hdrTokens[4] != "Region Limits"):
        goodData = 0
    if (hdrTokens[5] != "q values"):
        goodData = 0
    if (hdrTokens[6] != "Residual q values after removing segments shared with higher peaks"):
        goodData = 0
    if (hdrTokens[7] != "Broad or Focal"):
        goodData = 0
    if (not goodData):
        print " ERROR ??? unexpected hdrTokens ??? ", len(hdrTokens)
        print hdrTokens
        sys.exit(-1)

    sampleIDs = []
    for ii in range(9, numTokens):
        oneID = hdrTokens[ii]
        if (not oneID.startswith("TCGA-")):
            print " ERROR ??? this should be a TCGA barcode ??? ", oneID
            sys.exit(-1)
        sampleIDs += [oneID]

    # ok, now we read each row ... this file has two rows for each ROI
    # first the CN values have been discretized, and second it is the
    # "actual copy change" value ...
    # note that the discretized values are always {0,1,2} even when it
    # is a 'deletion', it's just where the thresholds are set that
    # changes ...

    roiDict = {}

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1

        else:
            roiName = tokenList[0]
            cytoName = tokenList[1]
            widePeakString = tokenList[2]
            peakString = tokenList[3]
            regionString = tokenList[4]
            qVal = float(tokenList[5])
            res_qVal = float(tokenList[6])
            bfString = tokenList[7]  # "Broad or Focal" column never used ???
            threshString = tokenList[8]

            featName = makeGisticFeatureName(
                namePrefix, roiName, cytoName, widePeakString,
                peakString, regionString, threshString)
            roiDict[featName] = [0] * numSamples
            if (threshString.startswith("Actual")):
                # it turns out that the Gistic "all_lesions" file does not contain log2(CN/2)
                # values but rather "CN-2" values, so here we are re-mapping them ... (01jun12)
                # Gistic -1  -->  log2(CN/2) -1
                # 0  -->              0
                # 2  -->             +1
                # 6  -->             +2
                for ii in range(numSamples):
                    gisticValue = float(tokenList[9 + ii])
                    cnValue = gisticValue + 2.
                    logCN = miscMath.log2(cnValue / 2.)
                    roiDict[featName][ii] = logCN
            else:
                # here we are handling the discretized values which we are going to
                # map as categorical values ...
                if (roiName.startswith("Amplification")):
                    for ii in range(numSamples):
                        ## roiDict[featName][ii] = int ( tokenList[9+ii] )
                        roiDict[featName][ii] = str("Amp" + tokenList[9 + ii])
                elif (roiName.startswith("Deletion")):
                    for ii in range(numSamples):
                        ## roiDict[featName][ii] = -1 * int ( tokenList[9+ii] )
                        roiDict[featName][ii] = str("Del" + tokenList[9 + ii])
                else:
                    print " unexpected ROI name ??? ", roiName
                    sys.exit(-1)

    fhIn.close()

    # now we're ready to write out the output file ...
    print " writing output file ", outName
    fhOut = file(outName, 'w')

    # first comes the header row ...
    outLine = "bcr_patient_barcode"
    featList = roiDict.keys()
    featList.sort()
    for aFeat in featList:
        outLine += "\t%s" % aFeat
    fhOut.write("%s\n" % outLine)

    for ii in range(len(sampleIDs)):
        outLine = "%s" % sampleIDs[ii]
        for aFeat in featList:
            if (aFeat.find("ROI_d") > 0 or aFeat.find("Arm_d") > 0):
                outLine += "\t%s" % roiDict[aFeat][ii]
            elif (aFeat.find("ROI_r") > 0 or aFeat.find("Arm_r") > 0):
                outLine += "\t%6.2f" % roiDict[aFeat][ii]
            else:
                print " ERROR in feature name ??? !!! ", aFeat
                sys.exit(-1)
        fhOut.write("%s\n" % outLine)

    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseGistic_BroadArmValuesFile(inName, outName):

    # 03may13 ... need to chop up the filename and use some information
    # from the filename for the feature name ...

    # 012345678901234567890123456789
    # gdac.broadinstitute.org_SKCM-All_Metastatic.CopyNumber_Gistic2.Level_4.2013050200.0.0
    nameTokens = inName.split('/')
    nameTokens = (nameTokens[-2][24:]).split('.')
    namePrefix = nameTokens[0]
    print " (c) namePrefix : ", namePrefix, nameTokens

    fhIn = file(inName)
    print "     reading in <%s> " % inName

    # this file uses just the first column to give the chromosome arm name
    hdrLine = fhIn.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)
    numSamples = numTokens - 1

    # sanity check the header tokens a bit ...
    goodData = 1
    if (hdrTokens[0] != "Chromosome Arm"):
        goodData = 0
    if (not goodData):
        print " ERROR ??? unexpected hdrTokens ??? ", len(hdrTokens)
        print hdrTokens
        sys.exit(-1)

    sampleIDs = []
    for ii in range(1, numTokens):
        oneID = hdrTokens[ii]
        if (not oneID.startswith("TCGA-")):
            print " ERROR ??? this should be a TCGA barcode ??? ", oneID
            sys.exit(-1)
        sampleIDs += [oneID]

    armDict = {}
    armList = []

    done = 0
    while not done:
        aLine = fhIn.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) != numTokens):
            done = 1

        else:
            armName = tokenList[0]
            chrName = armName[:-1]
            startPos = chrArms.arms_hg19[armName][0]
            stopPos = chrArms.arms_hg19[armName][1]

            # create two features per arm ... a 'continuous' feature and a
            # 'discrete' feature

            # 30jan14 : commenting this out (SMR)
            if ( 0 ):
                # first the continuous or "_r" feature:
                featName = "N:CNVR:" + armName + ":chr" + chrName + \
                    ":%d:%d::%s_GisticArm_r" % (startPos, stopPos, namePrefix)
                armDict[featName] = numpy.zeros(numSamples)
                armList += [featName]
                for ii in range(numSamples):
                    armDict[featName][ii] = float(tokenList[1 + ii])

            # then the discrete or "_d" feature:
            # 30jan14 : and changing this to a Numerical feature (SMR)
            featName = "N:CNVR:" + armName + ":chr" + chrName + \
                ":%d:%d::%s_GisticArm_d" % (startPos, stopPos, namePrefix)
            armDict[featName] = numpy.zeros(numSamples)
            armList += [featName]
            for ii in range(numSamples):
                fVal = float(tokenList[1 + ii])
                if (fVal < -1.3):
                    armDict[featName][ii] = -2
                elif (fVal < -0.3):
                    armDict[featName][ii] = -1
                elif (fVal < 0.3):
                    armDict[featName][ii] = 0
                elif (fVal < 0.9):
                    armDict[featName][ii] = 1
                else:
                    armDict[featName][ii] = 2

    fhIn.close()

    # now we're ready to write out the output file ...
    print " writing output file ", outName
    fhOut = file(outName, 'w')

    # first comes the header row ...
    outLine = "bcr_patient_barcode"
    for aFeat in armList:
        outLine += "\t%s" % aFeat
    fhOut.write("%s\n" % outLine)

    for ii in range(len(sampleIDs)):
        outLine = "%s" % sampleIDs[ii]
        for aFeat in armList:
            if (aFeat.find("ROI_r") > 0 or aFeat.find("Arm_r") > 0):
                outLine += "\t%6.2f" % armDict[aFeat][ii]
            elif (aFeat.find("ROI_d") > 0 or aFeat.find("Arm_d") > 0):
                outLine += "\t%2d" % armDict[aFeat][ii]
            else:
                print " ERROR ??? how did this happen ??? ", aFeat, armDict[aFeat][ii]
                sys.exit(-1)
        fhOut.write("%s\n" % outLine)

    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this is the top-level driver for parsing the Gistic files -- it calls
# other function to handle each individual file


def parseGisticFiles(lastDir, outDir):

    print " "
    print " START: parsing Gistic files from firehose outputs "
    print " "
    numGot = 0

    print lastDir

    # now that we have the most recent firehose run, we loop over all of
    # the Level_4 directories looking for Gistic output files
    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        # careful not to grab the "CopyNumberLowPass_Gistic2" outputs
        if (d2Name.find("CopyNumber_Gistic2.Level_4") > 0):

            d3 = path.path(d2Name)
            for fName in d3.files():

                # the first file we are interested in is the all_lesions file
                # ...
                if (fName.find("all_lesions") >= 0):
                    if (fName.endswith(".txt")):
                        inName = fName
                        print " >>> got one !!! ", fName
                        numGot += 1
                        outName = outDir + \
                            getLastBit(d2Name) + ".all_lesions.tsv"
                        parseGistic_LesionsFile(inName, outName)

                # the next file we are interested in is the broad_values_by_arm
                # file ...
                if (fName.endswith("broad_values_by_arm.txt")):
                    inName = fName
                    print " >>> got one !!! ", fName
                    numGot += 1
                    outName = outDir + \
                        getLastBit(d2Name) + ".broad_values_by_arm.tsv"
                    parseGistic_BroadArmValuesFile(inName, outName)

                # and we also want to parse the all_data_by_genes.txt file
                if (fName.endswith("all_data_by_genes.txt")):
                    inName = fName
                    print " >>> got one !!! ", fName
                    numGot += 1
                    outName = outDir + \
                        getLastBit(d2Name) + ".all_data_by_genes.txt"
                    parseGistic_AllDataByGenesFile(inName, outName)

    print " "
    print " DONE: parsing Gistic files from firehose outputs (%d files) " % numGot
    if (numGot == 0):
        print " ERROR ??? no Gistic files found ??? "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def add2sampleList(fName, sampleList):

    print " in add2sampleList ... <%s> " % fName, len(sampleList)

    fh = file(fName)
    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()
        tokenList = aLine.split('\t')
        for aToken in tokenList:
            if (aToken.startswith("TCGA-")):
                possibleBarcode = aToken
                # print " possible barcode : <%s> " % possibleBarcode
                # 012345678901234
                # TCGA-FS-A1ZP-06A-2
                if (len(possibleBarcode) == 12):
                    if (possibleBarcode not in sampleList):
                        print possibleBarcode
                        sampleList += [possibleBarcode]
                elif (len(possibleBarcode) >= 16):
                    shortBarcode = possibleBarcode[:16]
                    if ( shortBarcode[-1] == "-" ):
                        print " WARNING ERROR ... bad barcode ??? ", shortBarcode
                        shortBarcode = miscTCGA.get_tumor_barcode(shortBarcode[:15])
                        print "      --> fixed ??? ", shortBarcode
                    if (shortBarcode not in sampleList):
                        print shortBarcode
                        sampleList += [shortBarcode]

    print len(sampleList)
    return (sampleList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanupSampleList(sampleList):

    print len(sampleList)
    print sampleList

    cleanPatientList = []
    cleanSampleList = []

    for aSample in sampleList:
        if (len(aSample) == 12):
            if (aSample not in cleanPatientList):
                cleanPatientList += [aSample]
        elif (len(aSample) == 16):
            shortB = aSample[:12]
            if (shortB not in cleanPatientList):
                cleanPatientList += [shortB]
            if (aSample not in cleanSampleList):
                cleanSampleList += [aSample]

    cleanPatientList.sort()
    cleanSampleList.sort()

    return (cleanPatientList, cleanSampleList)

# for aSample in sampleList:
# if ( len(aSample) == 12 ):
##            rmFlag = 0
# for bSample in sampleList:
# if ( len(bSample) > 12 ):
# if ( bSample.startswith(aSample) ):
##                        rmFlag = 1
# if ( not rmFlag ):
##                cleanSampleList += [ aSample ]
# else:
##            cleanSampleList += [ aSample ]

    print " done "
    print len(cleanSampleList)
    for aSample in cleanSampleList:
        print aSample

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# new code for building up a white list of samples based on all of the
# Level_4 firehose analysis outputs ...


def buildSampleWhiteList(lastDir, outDir):

    print " "
    print " START: parsing all Level_4 outputs to build sample white list "
    print " "

    print lastDir

    sampleList = []

    d2 = path.path(lastDir)

    i1 = len(d2) - 1
    while (d2[i1] != '/'):
        i1 -= 1
    dateString = d2[i1 + 1:]

    for d2Name in d2.dirs():

        if (d2Name.find("Level_4") > 0):

            ## careful never to grab those FFPE-specific runs
            if ( d2Name.find("FFPE") > 0 ): continue

            d3 = path.path(d2Name)
            for fName in d3.files():

                if (fName.endswith(".txt")):
                    sampleList = add2sampleList(fName, sampleList)

    (cleanPatientList, cleanSampleList) = cleanupSampleList(sampleList)

    outName = outDir + "gdac.broadinstitute.org_" + \
        dateString + ".patientList.txt"
    fh = file(outName, 'w')
    for aSample in cleanPatientList:
        fh.write("%s\n" % aSample)
    fh.close()

    outName = outDir + "gdac.broadinstitute.org_" + \
        dateString + ".sampleList.txt"
    fh = file(outName, 'w')
    for aSample in cleanSampleList:
        fh.write("%s\n" % aSample)
    fh.close()

    print " "
    print " DONE: building sample white list ", len(cleanPatientList), len(cleanSampleList)
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getMutSigVersionString ( zCancer, auxName ):

    defaultString = "MutSigNozzleReport2CV"

    try:
        rootString = gidgetConfigVars['TCGAFMP_DATA_DIR']
    except:
        MSverString = defaultString
        print "     --> defaulting to %s " % defaultString

    fName = rootString + "/" + zCancer.lower() + "/" + auxName + "/MutSigversion.txt"
    try:
        fh = file ( fName, 'r' )
        print "     checking file %s for MutSig version specification " % fName
        for aLine in fh:
            if ( aLine.startswith("#") ): continue
            if ( aLine.find("MutSig") >= 0 ):
                MSverString = aLine.strip()
                print "     --> will look for %s outputs " % MSverString
    except:
        MSverString = defaultString
        print "     --> defaulting to %s " % defaultString

    return ( MSverString )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getLastBit(aName):

    ii = len(aName) - 1
    while (aName[ii] != '/'):
        ii -= 1

    # print ' <%s>    <%s> ' % ( aName, aName[ii+1:] )

    return (aName[ii + 1:])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#
# this program goes through the Firehose outputs and creates TSV files
# that are ready for our pipeline ...
#

if __name__ == "__main__":

    # list of cancer directory names
    cancerDirNames = [
        'acc',  'blca', 'brca', 'cesc', 'chol', 'cntl', 'coad', 'dlbc', 'esca', 'gbm',
        'hnsc', 'kich', 'kirc', 'kirp', 'laml', 'lcll', 'lgg',  'lihc', 'lnnh',
        'luad', 'lusc', 'ov',   'paad', 'prad', 'read', 'sarc', 'skcm', 'stad',
        'thca', 'ucec', 'lcml', 'pcpg', 'meso', 'tgct', 'ucs', 'uvm', 'thym' ]

    if (1):
        if ( (len(sys.argv)!=3) and (len(sys.argv)!=4) ):
            print " Usage: %s <tumorType> <public/private> [auxName] " % sys.argv[0]
            print " Notes: a single tumor type can be specified, eg brca "
            print "        the public/private option indicates whether an awg-specific "
            print "        firehose run should be used if available "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        else:

            tumorType = sys.argv[1].lower()
            if (tumorType == "all"):
                print " FATAL ERROR ... this option is no longer allowed "
                sys.exit(-1)
            elif (tumorType in cancerDirNames):
                print " --> processing a single tumor type: ", tumorType
                cancerDirNames = [tumorType]
            else:
                print " ERROR ??? tumorType <%s> not in list of known tumors? " % tumorType
                print cancerDirNames
                sys.exit(-1)

            ppString = sys.argv[2].lower()
            if ( ppString.find("pub") >= 0 ):
                awgFlag = "NO"
                print " --> will NOT use awg-specific firehose analyses even if available "
            elif ( ppString.find("priv") >= 0 ):
                awgFlag = "YES"
                print " --> WILL use awg-specific firehose anlaysese IF available "
            else:
                print " FATAL ERROR ... invalid public/private string ", ppString
                sys.exit(-1)

            if ( len(sys.argv) == 4 ):
                auxName = sys.argv[3]
            else:
                auxName = "aux"

    # 22jun : switching to new firehose analyses that were downloaded using
    # firehose_get -b analyses latest
    firehoseTopDir = gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR']+ "/"
    outDir = "./"

    # first thing we have to do is find the most recent top-level directory
    # which should have a name of the form
    # analyses__2012_04_25
    topDir = getMostRecentDir(firehoseTopDir, cancerDirNames, awgFlag)
    print " here now : ", topDir

    # outer loop over tumor types
    for zCancer in cancerDirNames:
        print ' '
        print ' OUTER LOOP over CANCER TYPES ... ', zCancer

        lastDir = getCancerDir(topDir, zCancer)

        # now we handle the *.bestclus.txt files ...
        parseBestClusFiles(lastDir, outDir, zCancer)

        # next we process files that come out of the MutSig module
        # ( but first we ask which version of MutSig is supposed to be 
        #   used for this tumor type )
        MSverString = getMutSigVersionString ( zCancer, auxName )
        parseMutSigFiles(lastDir, outDir, MSverString)

        # next we process the files that come out of Gistic
        parseGisticFiles(lastDir, outDir)

        # and finally grab the 'mature' miRNA matrix ...

        # build up the 'master' list of samples ...
        buildSampleWhiteList(lastDir, outDir)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
