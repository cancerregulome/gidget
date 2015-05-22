# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars
import miscMath
import miscTCGA

import commands
import numpy
import path
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

name_map_dict = {}
haveNameMapDict = 0

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getDate(dName):

    dateString = dName[-10:]
    iDate = int(dateString[0:4]) * 10000 + \
        int(dateString[5:7]) * 100 + int(dateString[8:10])
    return (iDate)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMostRecentDir(topDir, cancerList):

    print " in getMostRecentDir ... "
    print topDir
    print cancerList

    d1 = path.path(topDir)
    iDates = []
    for d1Name in d1.dirs():

        if (d1Name.find("stddata") >= 0):
            iDates += [getDate(d1Name)]

        if (0):
            if (len(cancerList) == 1):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        iDates += [getDate(d1Name)]

    iDates.sort()
    print iDates

    lastDate = str(iDates[-1])
    lastDate = lastDate[0:4] + "_" + lastDate[4:6] + "_" + lastDate[6:8]
    print lastDate

    lastDir = "NA"
    for d1Name in d1.dirs():

        if (0):
            # give first priority to awg specific run ...
            if (len(cancerList) == 1):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        if (d1Name.find(lastDate) >= 0):
                            lastDir = d1Name

    if (lastDir == "NA"):
        for d1Name in d1.dirs():
            if (d1Name.find("stddata") >= 0):
                if (d1Name.find(lastDate) >= 0):
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


def getMetaDataInfo(metaFilename):

    fh = file(metaFilename)
    metaData = {}
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        probeID = tokenList[0]
        featName = tokenList[1]
        metaData[probeID] = featName

    fh.close()
    return (metaData)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeParentheticalStuff(aString):

    # print " in removeParentheticalStuff ... ", aString

    i1 = aString.find('(')
    if (i1 >= 0):
        i2 = aString.find(')', i1)
        if (i2 >= 0):
            aString = aString[:i1] + aString[i2 + 1:]
            aString = removeParentheticalStuff(aString)

    # print " returning from removeParentheticalStuff ... ", aString
    return (aString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanString(aString):

    # print " in cleanString <%s> " % aString
    tString = removeParentheticalStuff(aString)
    if (len(tString) > 1):
        aString = tString

    skipChars = ["(", ")", "'", "@", '"']
    spaceChars = [" ", ".", "/", ":"]
    okChars = ["-", "_", ","]

    bString = ''
    for ii in range(len(aString)):
        if (aString[ii] in skipChars):
            doNothing = 1
        elif (aString[ii] in spaceChars):
            if (len(bString) > 0):
                if (bString[-1] != "_"):
                    bString += "_"
        elif (aString[ii] in okChars):
            bString += aString[ii]
        else:
            iChar = ord(aString[ii])
            if ((iChar < ord('0')) or (iChar > ord('z'))):
                # print " what character is this ??? ", iChar
                doNothing = 1
            elif ((iChar > ord('9')) and (iChar < ord('A'))):
                # print " what character is this ??? ", iChar
                doNothing = 1
            elif ((iChar > ord('Z')) and (iChar < ord('a'))):
                # print " what character is this ??? ", iChar
                doNothing = 1
            else:
                bString += aString[ii]

    # somewhat of a hack ;-)
    if (bString.lower() == "stage_0"):
        # print " Transforming <STAGE 0> to <TIS> "
        bString = "Tis"

    if (bString.lower().startswith("stage_")):
        bString = bString[6:]
    if (bString.lower().startswith("grade_")):
        bString = bString[6:]

    try:
        while (bString[-1] == "_"):
            bString = bString[:-1]
    except:
        doNothing = 1

    # print "     returning bString <%s> " % bString
    return (bString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtData(dataVec):

    numSamples = len(dataVec)
    numNA = 0
    isFloat = 1
    isInt = 1

    for ii in range(numSamples):
        if (dataVec[ii] == "NA"):
            numNA += 1
            continue
        try:
            xFloat = float(dataVec[ii])
            try:
                xInt = int(dataVec[ii])
                if (abs(xInt - xFloat) > 0.1):
                    isInt = 0
            except:
                isInt = 0
        except:
            isFloat = 0
            isInt = 0
            dataVec[ii] = cleanString(dataVec[ii])

    uVec = []
    for ii in range(numSamples):
        if (dataVec[ii] == "NA"):
            continue
        if (dataVec[ii] not in uVec):
            uVec += [dataVec[ii]]

    if (isInt):
        dataType = "INT"
    elif (isFloat):
        dataType = "FLOAT"
    else:
        dataType = "STRING"

    # print dataType, uVec
    fracNA = float(numNA) / float(numSamples)

    return (dataType, len(uVec), fracNA, dataVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readNameMapDict():

    fh = file(gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR'] + "/metadata/name_map.tsv")
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if (len(tokenList) == 2):
            name_map_dict[tokenList[0]] = tokenList[1]
            print " setting up mapping from <%s> to <%s> " % (tokenList[0], tokenList[1])
        else:
            print " bad input line in name_map file ??? ", len(tokenList)
            print tokenList
    fh.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def makeFeatureName(featName, dataType):

    global haveNameMapDict
    global name_map_dict

    if (0):
        if (dataType == "STRING"):
            newFeatName = "C:CLIN:"
        else:
            newFeatName = "N:CLIN:"
    else:
        newFeatName = ""

    if (1):
        newFeatName = featName
        newFeatName2 = newFeatName

    if (not haveNameMapDict):
        readNameMapDict()
        haveNameMapDict = 1

    try:
        tmpName1 = name_map_dict[newFeatName]
    except:
        print " NOTE: name not in name_map_dict <%s> " % newFeatName
        tmpName1 = newFeatName

    try:
        tmpName2 = name_map_dict[newFeatName2]
    except:
        print " NOTE: name not in name_map_dict <%s> " % newFeatName2
        tmpName2 = newFeatName2

    return (tmpName1, tmpName2)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseClinicalDataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    # these features are protected even if they have cardinality 1 ...
    protectedFeatures = ["disease_code", "tumor_tissue_site",
                         "days_to_additional_surgery_metastatic_procedure",
                         "days_to_birth", "days_to_death",
                         "days_to_initial_pathologic_diagnosis",
                         "days_to_last_followup",
                         "days_to_new_tumor_event_after_initial_treatment",
                         "days_to_submitted_specimen_dx",
                         "new_tumor_event_after_initial_treatment",
                         "tumor_type", "tumor_tissue_site"]

    print " "
    print " "
    print " in parseCinicalDataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    if (subsetName == ""):
        expectedFileName = zCancer.upper() + ".clin.merged.picked.txt"
    else:
        expectedFileName = zCancer.upper() + "-" + \
            subsetName + "clin.merged.picked.txt"

    print " expectedFileName : <%s> " % expectedFileName

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        if (d2Name.find("Clinical_Pick_Tier1") > 0):
            if (d2Name.find(".Level_4.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    if (fName.endswith(expectedFileName)):
                        if (1):
                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM.clin.merged.txt
                            outFile = zCancer + ".firehose__clin_merged." + \
                                suffixString + ".tsv"
                            try:
                                print " opening output file : ", outFile
                                fhOut = file(outFile, 'w')
                            except:
                                print " ERROR ??? failed to open output file ??? "
                                print outFile
                                sys.exit(-1)

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file

                            fh = file(fName)

                            # first I need to get the patient barcodes ...
                            fh = file(fName)
                            for aLine in fh:
                                if (aLine.startswith("Hybridization REF")):
                                    aLine = aLine.strip()
                                    tokenList = aLine.split('\t')
                                    barcodeList = []
                                    for ii in range(1, len(tokenList)):
                                        barcodeList += [tokenList[ii].upper()]
                                    print barcodeList
                            fh.close()

                            # we need to turn these patient barcodes into tumor
                            # sample barcodes
                            numPatients = len(barcodeList)
                            tumorBarcodeList = []
                            for iP in range(numPatients):
                                patientBarcode = barcodeList[iP]
                                tumorBarcode = miscTCGA.get_tumor_barcode(
                                    patientBarcode)
                                tumorBarcodeList += [tumorBarcode]

                            # and then write them to the output file
                            outLine = "M:CLIN"
                            for iP in range(numPatients):
                                outLine += "\t%s" % tumorBarcodeList[iP]
                            fhOut.write("%s\n" % outLine)

                            # we need to make sure that we are generating
                            # unique feature names
                            uniqNames = []

                            # and now we read all of the other data ...
                            fh = file(fName)
                            for aLine in fh:

                                if (aLine.startswith("Composite Element REF")):
                                    continue
                                if (aLine.find("dccupload") >= 0):
                                    continue

                                aLine = aLine.strip()
                                tokenList = aLine.split('\t')

                                # take a look at the feature name ...
                                featName = ""
                                for aa in tokenList[0]:
                                    if (aa == '.'):
                                        featName += "_"
                                    else:
                                        featName += aa

                                # and at the data ...
                                dataVec = tokenList[1:]
                                (dataType, dataCard, fracNA,
                                 dataVec) = lookAtData(dataVec)
                                print featName, dataType, dataCard, fracNA

                                (newFeatName1, newFeatName2) = makeFeatureName(
                                    featName, dataType)
                                print " feature name mapping : ", featName, newFeatName1, newFeatName2

                                if ((newFeatName1 not in protectedFeatures) and
                                        (newFeatName2 not in protectedFeatures)):
                                    if (dataCard < 2):
                                        if (featName not in protectedFeatures):
                                            print " --> skipping uninformative feature ", featName
                                            continue
                                    if (fracNA > 0.90):
                                        print " --> skipping feature with too many NAs (%.2f) " % fracNA, featName
                                        continue

                                if (newFeatName1 in uniqNames):
                                    if (newFeatName2 in uniqNames):
                                        print " ERROR !!! ??? repeated feature name <%s> <%s> " % (newFeatName2, newFeatName1)
                                        print " --> skipping "
                                        continue
                                        # sys.exit(-1)
                                    else:
                                        print " NOTE ... using <%s> instead of <%s> " % (newFeatName2, newFeatName1)
                                        newFeatName = newFeatName2
                                else:
                                    print " using primary feature name <%s> " % newFeatName1
                                    newFeatName = newFeatName1

                                uniqNames += [newFeatName]

                                outLine = newFeatName
                                for iP in range(numPatients):
                                    outLine += "\t%s" % dataVec[iP]
                                fhOut.write("%s\n" % outLine)

                            fh.close()
                            fhOut.close()

    print " DONE with parseClinicalDataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseMethylationDataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseMethylationDataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        if (d2Name.find("Merge_methylation__") > 0):
            if (d2Name.find("__data.Level_3.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    if (fName.find("methylation__humanmethylation") >= 0):
                        if (fName.endswith(".data.txt")):

                            if (subsetName != ""):
                                if (fName.find(subsetName) < 0):
                                    continue

                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM.methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.data.txt
                            if (fName.find("humanmethylation450") > 0):
                                outFile = zCancer + ".jhu-usc.edu__humanmethylation450__methylation." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "HumanMethylation450"
                                    numCol = 4
                                    iCol = 1
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            elif (fName.find("humanmethylation27") > 0):
                                outFile = zCancer + ".jhu-usc.edu__humanmethylation27__methylation." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "HumanMethylation27"
                                    numCol = 4
                                    iCol = 1
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            else:
                                print " new data type ??? "
                                print fName
                                sys.exit(-1)

                            # --------------------------------------
                            # do we need some metadata?
                            metaData = getMetaDataInfo(
                                gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR'] + "/metadata/meth.probes.15oct13.txt")

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file
                            fh = file(fName)
                            hdr1Line = fh.readline()
                            hdr2Line = fh.readline()
                            hdr1Line = hdr1Line.strip()
                            hdr2Line = hdr2Line.strip()
                            hdr1Tokens = hdr1Line.split('\t')
                            hdr2Tokens = hdr2Line.split('\t')

                            outLine = "N:METH"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + hdr1Tokens[kk]
                            fhOut.write("%s\n" % outLine)

                            outLine = "C:SAMP:methPlatform"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + platformName
                            fhOut.write("%s\n" % outLine)

                            print " # of header tokens : ", len(hdr1Tokens)
                            numData = (len(hdr1Tokens) - 1) / numCol
                            print " # of data columns : ", numData
                            dataVec = [0] * numData

                            done = 0
                            iLine = 1
                            while not done:
                                aLine = fh.readline()
                                aLine = aLine.strip()
                                aList = aLine.split('\t')
                                if (len(aList) < 5):
                                    done = 1
                                    continue

                                iLine += 1
                                if ((iLine % 10000) == 0):
                                    print iLine

                                try:
                                    aFeature = metaData[aList[0]]
                                except:
                                    # print " SKIPPING !!! "
                                    continue

                                ii = 0
                                for kk in range(iCol, len(aList), numCol):
                                    if (aList[kk] == "NA"):
                                        dataVec[ii] = "NA"
                                    else:
                                        dataVec[ii] = "%.3f" % (
                                            float(aList[kk]))
                                    ii += 1
                                # print dataVec
                                outLine = aFeature
                                for ii in range(len(dataVec)):
                                    outLine += "\t" + dataVec[ii]
                                fhOut.write("%s\n" % outLine)

                            fhOut.close()

    print " DONE with parseMethylationDataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseMicroRNADataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseMicroRNADataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        if (d2Name.find("Merge_mirnaseq__") > 0):
            if (d2Name.find("gene_expression__data.Level_3.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    if (fName.find("mirnaseq__") >= 0):
                        if (fName.endswith(".data.txt")):

                            if (subsetName != ""):
                                if (fName.find(subsetName) < 0):
                                    continue

                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM.mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.data.txt
                            if (fName.find("illuminahiseq_mirnaseq__bcgsc") > 0):
                                outFile = zCancer + ".bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "IlluminaHiSeq_miRNASeq"
                                    numCol = 3
                                    iCol = 2
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            elif (fName.find("illuminaga_mirnaseq__bcgsc") > 0):
                                outFile = zCancer + ".bcgsc.ca__illuminaga_mirnaseq__mirnaseq." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "IlluminaGA_miRNASeq"
                                    numCol = 3
                                    iCol = 2
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            else:
                                print " new data type ??? "
                                print fName
                                sys.exit(-1)

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file
                            fh = file(fName)
                            hdr1Line = fh.readline()
                            hdr2Line = fh.readline()
                            hdr1Line = hdr1Line.strip()
                            hdr2Line = hdr2Line.strip()
                            hdr1Tokens = hdr1Line.split('\t')
                            hdr2Tokens = hdr2Line.split('\t')

                            outLine = "N:MIRN"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + hdr1Tokens[kk]
                            fhOut.write("%s\n" % outLine)

                            outLine = "C:SAMP:mirnPlatform"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + platformName
                            fhOut.write("%s\n" % outLine)

                            print " # of header tokens : ", len(hdr1Tokens)
                            numData = (len(hdr1Tokens) - 1) / numCol
                            print " # of data columns : ", numData
                            dataVec = [0] * numData

                            done = 0
                            iLine = 1
                            while not done:
                                aLine = fh.readline()
                                aLine = aLine.strip()
                                aList = aLine.split('\t')
                                if (len(aList) < 5):
                                    done = 1
                                    continue

                                iLine += 1
                                if ((iLine % 10000) == 0):
                                    print iLine

                                aFeature = "N:MIRN:" + aList[0] + ":::::"
                                # print aFeature

                                ii = 0
                                for kk in range(iCol, len(aList), numCol):
                                    if (aList[kk] == "NA"):
                                        dataVec[ii] = "NA"
                                    else:
                                        dataVec[ii] = "%.3f" % (
                                            float(aList[kk]))
                                    ii += 1
                                # print dataVec
                                outLine = aFeature
                                for ii in range(len(dataVec)):
                                    outLine += "\t" + dataVec[ii]
                                fhOut.write("%s\n" % outLine)

                            fhOut.close()

    print " DONE with parseMicroRNADataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseMatureMicroRNADataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseMatureMicroRNADataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        ## print d2Name
        if (d2Name.find("miRseq_Mature_Preprocess") > 0):
            if (d2Name.find(".Level_4.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    ## print fName
                    if (fName.find("miRseq_mature") >= 0):
                        if (fName.endswith("_log2.txt")):

                            if (subsetName != ""):
                                if (fName.find(subsetName) < 0):
                                    continue

                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM-All_Samples.miRseq_mature_PKM_log2.txt
                            if (fName.find("miRseq_mature_PKM") > 0):
                                # note that this name is not quite correct, but leaving it anyway
                                # because it won't break the subsequent
                                # pipeline steps ...
                                outFile = zCancer + ".bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "miRNASeq_mature_PKM"
                                    numCol = 1
                                    iCol = 1
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            else:
                                print " new data type ??? "
                                print fName
                                sys.exit(-1)

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file
                            fh = file(fName)
                            hdr1Line = fh.readline()
                            hdr1Line = hdr1Line.strip()
                            hdr1Tokens = hdr1Line.split('\t')

                            outLine = "N:MIRN"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + hdr1Tokens[kk]
                            fhOut.write("%s\n" % outLine)

                            outLine = "C:SAMP:mirnPlatform"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + platformName
                            fhOut.write("%s\n" % outLine)

                            print " # of header tokens : ", len(hdr1Tokens)
                            numData = (len(hdr1Tokens) - 1) / numCol
                            print " # of data columns : ", numData
                            dataVec = [0] * numData

                            done = 0
                            iLine = 1
                            while not done:
                                aLine = fh.readline()
                                aLine = aLine.strip()
                                aList = aLine.split('\t')
                                print aList
                                if (len(aList) < 5):
                                    done = 1
                                    continue

                                iLine += 1
                                if ((iLine % 10000) == 0):
                                    print iLine

                                aSplit = aList[0].split('|')

                                aFeature = "N:MIRN:" + \
                                    aSplit[0] + ":::::" + aSplit[1]
                                print aFeature

                                ii = 0
                                for kk in range(iCol, len(aList), numCol):
                                    if (aList[kk] == "NA"):
                                        dataVec[ii] = "NA"
                                    else:
                                        print kk, aList[kk]
                                        dataVec[ii] = "%.3f" % (
                                            float(aList[kk]))
                                    ii += 1
                                # print dataVec
                                outLine = aFeature
                                for ii in range(len(dataVec)):
                                    outLine += "\t" + dataVec[ii]
                                fhOut.write("%s\n" % outLine)

                            fhOut.close()

    print " DONE with parseMatureMicroRNADataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getGeneAntibodyMap():

    geneAntibodyMap = {}

    fh = file( gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] + "/tcga_platform_genelists/MDA_antibody_annotation_2014_03_04.txt" )
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        token0 = tokenList[0].strip()
        token1 = tokenList[1].strip()

        if (token0 != "Gene Name"):
            geneAntibodyMap[token1] = token0

    fh.close()
    return (geneAntibodyMap)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# for the RPPA data we could either grab data form
# gdac.broadinstitute.org_THCA-TP.RPPA_AnnotateWithGene.Level_3.2013071400.0.0
# where the file is called THCA-TP.rppa.txt and has row labels like
# EIF4EBP1|4E-BP1_pT70
# TP53BP1|53BP1
# ARAF|A-Raf_pS299
# ACACA|ACC1
# ACACA ACACB|ACC_pS79

# or
# gdac.broadinstitute.org_THCA-TP.Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3.2013071400.0.0
# where the file is called THCA-TP.protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.data.txt
# and the row labels are like
# 14-3-3_epsilon
# 4E-BP1
# 4E-BP1_pS65
# 4E-BP1_pT37_T46
# 53BP1
# ACC_pS79
# ACC1
# Akt

# the problem is that in both of these files, apparently it is ok for the barcode
# to end in -TP rather than -01 (at least that is what I am seeing in the THCA run
# from July but not from the SKCM run in October)


def parseRPPADataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseRPPADataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        if (d2Name.find("Merge_protein_exp__") > 0):
            if (d2Name.find("protein_normalization__data.Level_3.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    if (fName.find("rppa_core__") >= 0):
                        if (fName.endswith(".data.txt")):

                            if (subsetName != ""):
                                if (fName.find(subsetName) < 0):
                                    continue

                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM.mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.data.txt
                            if (fName.find("protein_exp__mda_rppa_core") > 0):
                                outFile = zCancer + ".mdanderson.org__mda_rppa_core__protein_exp." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "MDA_RPPA_Core"
                                    numCol = 1
                                    iCol = 1
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)
                            else:
                                print " new data type ??? "
                                print fName
                                sys.exit(-1)

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file
                            print " >>> ready to parse input file and write output file "
                            print " >>> %s " % fName
                            fh = file(fName)

                            hdr1Line = fh.readline()
                            hdr2Line = fh.readline()
                            hdr1Line = hdr1Line.strip()
                            hdr2Line = hdr2Line.strip()
                            hdr1Tokens = hdr1Line.split('\t')
                            hdr2Tokens = hdr2Line.split('\t')

                            numTok = len(hdr1Tokens)

                            outLine = "N:RPPA"
                            for kk in range(iCol, numTok, numCol):
                                # we may need to 'fix' the barcode
                                barcode = miscTCGA.fixTCGAbarcode(
                                    hdr1Tokens[kk], zCancer)
                                outLine += "\t" + barcode
                            fhOut.write("%s\n" % outLine)

                            outLine = "C:SAMP:rppaPlatform"
                            for kk in range(iCol, numTok, numCol):
                                outLine += "\t" + platformName
                            fhOut.write("%s\n" % outLine)

                            print " # of header tokens : ", numTok
                            numData = (numTok - 1) / numCol
                            print " # of data columns : ", numData
                            dataVec = [0] * numData

                            geneAntibodyMap = getGeneAntibodyMap()

                            done = 0
                            iLine = 1
                            while not done:
                                aLine = fh.readline()
                                aLine = aLine.strip()
                                aList = aLine.split('\t')
                                if (len(aList) < 5):
                                    done = 1
                                    continue

                                iLine += 1
                                if ((iLine % 10000) == 0):
                                    print iLine

                                try:
                                    geneName = geneAntibodyMap[aList[0]]
                                except:
                                    print " ERROR ??? could not get antibody <%s> to gene mapping ??? " % aList[0]
                                    sys.exit(-1)

                                aFeature = "N:RPPA:" + \
                                    geneName + ":::::" + aList[0]
                                # print aFeature

                                ii = 0
                                for kk in range(iCol, len(aList), numCol):
                                    if (aList[kk] == "NA"):
                                        dataVec[ii] = "NA"
                                    else:
                                        dataVec[ii] = "%.3f" % (
                                            float(aList[kk]))
                                    ii += 1
                                # print dataVec
                                outLine = aFeature
                                for ii in range(len(dataVec)):
                                    outLine += "\t" + dataVec[ii]
                                fhOut.write("%s\n" % outLine)

                            fhOut.close()

    print " DONE with parseRPPADataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# removed the other parse RPPA script ...

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def parseRNAseqDataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseRNAseqDataFiles ... "
    print " lastDir = <%s> " % lastDir
    print " outDir = <%s> " % outDir

    print lastDir

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        # we are looking for RNAseq data ...
        if (d2Name.find("Merge_rnaseq") > 0):

            # but if it comes from UNC then we only want the V2 data ...
            if (d2Name.find("__unc_edu__") > 0):
                if (d2Name.find("RSEM_genes_normalized__data.Level_3.") < 0):
                    continue

            # whereas if it comes from BCGSC then we just need to check for
            # gene expression data
            if (d2Name.find("__bcgsc_ca__") > 0):
                if (d2Name.find("gene_expression__data.Level_3.") < 0):
                    continue

            if (1):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    if (fName.find(".rnaseq") >= 0):
                        if (fName.endswith(".data.txt")):

                            if (subsetName != ""):
                                if (fName.find(subsetName) < 0):
                                    continue

                            print " >>> got one !!! ", fName

                            # --------------------------------------
                            # figure out the name of the output file based on the name of the input file
                            # SKCM.mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.data.txt
                            if (fName.find("illuminahiseq_rnaseqv2") > 0):
                                outFile = zCancer + ".unc.edu__illuminahiseq_rnaseqv2__rnaseqv2." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "IlluminaHiSeq_RNASeqV2"
                                    # in this file the only column is called
                                    # "normalized_count"
                                    numCol = 1
                                    iCol = 1
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            elif (fName.find("illuminaga_rnaseq_") > 0):
                                outFile = zCancer + ".bcgsc.ca__illuminaga_rnaseq__rnaseq." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "IlluminaGA_RNASeq"
                                    # NOTE: the 3 columns are raw_counts,
                                    # median_length_normalized, and RPKM
                                    numCol = 3
                                    iCol = 3
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            elif (fName.find("illuminahiseq_rnaseq_") > 0):
                                outFile = zCancer + ".bcgsc.ca__illuminahiseq_rnaseq__rnaseq." + \
                                    suffixString + ".tsv"
                                try:
                                    print " opening output file : ", outFile
                                    fhOut = file(outFile, 'w')
                                    platformName = "IlluminaHiSeq_RNASeq"
                                    numCol = 3
                                    iCol = 3
                                except:
                                    print " ERROR ??? failed to open output file ??? "
                                    print outFile
                                    sys.exit(-1)

                            else:
                                print " new data type ??? "
                                print fName
                                sys.exit(-1)

                            # --------------------------------------
                            # ok, time to parse the input file and write the
                            # output file
                            fh = file(fName)

                            hdr1Line = fh.readline()
                            hdr2Line = fh.readline()
                            hdr1Line = hdr1Line.strip()
                            hdr2Line = hdr2Line.strip()
                            hdr1Tokens = hdr1Line.split('\t')
                            hdr2Tokens = hdr2Line.split('\t')

                            outLine = "N:GEXP"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + hdr1Tokens[kk]
                            fhOut.write("%s\n" % outLine)

                            outLine = "C:SAMP:gexpPlatform"
                            for kk in range(iCol, len(hdr1Tokens), numCol):
                                outLine += "\t" + platformName
                            fhOut.write("%s\n" % outLine)

                            print " # of header tokens : ", len(hdr1Tokens)
                            numData = (len(hdr1Tokens) - 1) / numCol
                            print " # of data columns : ", numData
                            dataVec = [0] * numData

                            done = 0
                            iLine = 1
                            while not done:
                                aLine = fh.readline()
                                aLine = aLine.strip()
                                aList = aLine.split('\t')
                                if (len(aList) < 5):
                                    done = 1
                                    continue

                                iLine += 1
                                if ((iLine % 10000) == 0):
                                    print iLine

                                # there is a very troublesome gene label that starts out like this:
                                # Em:AC008101.5|?_calculated
                                # so then it gets split into [ 'Em:AC008101.5',
                                # '?_calculated' ]

                                geneTokens = aList[0].split('|')

                                # fiddle around with these gene tokens a little
                                # bit ...
                                if (len(geneTokens) < 2):
                                    print " ERROR ???? assuming / expecting at least two tokens here ??? ", geneTokens

                                if (geneTokens[-1].endswith("?_calculated")):
                                    geneTokens[-1] = geneTokens[-1][:-12]
                                elif (geneTokens[-1].endswith("_calculated")):
                                    geneTokens[-1] = geneTokens[-1][:-11]

                                if (geneTokens[-1] == ""):
                                    geneTokens = geneTokens[:-1]

                                if (len(geneTokens) == 3):
                                    if (geneTokens[1] != '?'):
                                        geneTokens[2] = geneTokens[1] + \
                                            ',' + geneTokens[2]

                                # 17sep13 ... added 'cleanString' call here because of this
                                # pesky gene name: Em:AC008101.5|?_calculated (which is supposedly
                                # also ESR1 or some variant of it ???)

                                if (geneTokens[0] == "?"):
                                    if (len(geneTokens) < 2):
                                        print " ERROR ??? no information about this gene ??? "
                                        print geneTokens
                                        sys.exit(-1)
                                    geneTokens[
                                        -1] = cleanString(geneTokens[-1])
                                    ## aFeature = "N:GEXP:" + geneTokens[-1] + ":::::" + geneTokens[-1]
                                    aFeature = "N:GEXP:" + \
                                        geneTokens[-1] + ":::::"
                                else:
                                    geneTokens[0] = cleanString(
                                        geneTokens[0])
                                    if (len(geneTokens) == 1):
                                        aFeature = "N:GEXP:" + \
                                            geneTokens[0] + ":::::"
                                    else:
                                        geneTokens[
                                            -1] = cleanString(geneTokens[-1])
                                        aFeature = "N:GEXP:" + \
                                            geneTokens[0] + \
                                            ":::::" + geneTokens[-1]
                                # print aFeature

                                ii = 0
                                for kk in range(iCol, len(aList), numCol):
                                    if (aList[kk] == "NA"):
                                        dataVec[ii] = "NA"
                                    else:
                                        dataVec[ii] = "%.3f" % (
                                            float(aList[kk]))
                                    ii += 1
                                # print dataVec
                                outLine = aFeature
                                for ii in range(len(dataVec)):
                                    outLine += "\t" + dataVec[ii]
                                fhOut.write("%s\n" % outLine)

                            fhOut.close()

    print " DONE with parseRNAseqDataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this just calls the snp_firehose_level3_matrix.py script ...


def parseSNP6dataFiles(lastDir, outDir, zCancer, subsetName, suffixString):

    print " "
    print " "
    print " in parseSNP6dataFiles "

    d2 = path.path(lastDir)
    for d2Name in d2.dirs():

        ## print "     d2Name : ", d2Name

        if (d2Name.find("Merge_snp__") > 0):
            if (d2Name.find("segmented_scna_minus_germline_cnv_hg19__seg.Level_3.") > 0):

                d3 = path.path(d2Name)
                for fName in d3.files():

                    ## print "         fName : ", fName

                    if (fName.endswith("hg19__seg.seg.txt")):

                        if (subsetName != ""):
                            if (fName.find(subsetName) < 0):
                                continue

                        print " >>> got one !!! ", fName

                        inputFile = fName
                        outputFile = zCancer + ".broad.mit.edu__genome_wide_snp_6__snp." + \
                            suffixString + ".tsv"
                        cmdString = "python " + gidgetConfigVars['TCGAFMP_ROOT_DIR'] + "/main/snp_firehose_Level3_matrix.py " + \
                            inputFile + " " + outputFile
                        print " running command : "
                        print cmdString
                        (status, output) = commands.getstatusoutput(
                            cmdString)
                        print " "
                        print " status "
                        print status
                        print " output "
                        print output

    print " "
    print " "
    print " DONE with parseSNP6dataFiles "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#
# this program goes through the Firehose outputs and creates TSV files
# that are ready for our pipeline ...
#

if __name__ == "__main__":

    # list of cancer directory names
    cancerDirNames = [
        'acc',  'blca', 'brca', 'cesc', 'cntl', 'coad', 'dlbc', 'esca', 'gbm',
        'hnsc', 'kich', 'kirc', 'kirp', 'laml', 'lcll', 'lgg',  'lihc', 'lnnh',
        'luad', 'lusc', 'ov',   'paad', 'prad', 'read', 'sarc', 'skcm', 'stad',
        'thca', 'ucec', 'lcml', 'pcpg', 'meso', 'tgct', 'ucs' ]

    if (1):
        if (len(sys.argv) < 3):
            print " Usage: %s <tumorType> <suffix-string> [path-to-stddata] [subset-name] " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        else:
            tumorType = sys.argv[1].lower()
            if (tumorType == "all"):
                print " this option is no longer allowed "
                sys.exit(-1)
            elif (tumorType in cancerDirNames):
                print " --> processing a single tumor type: ", tumorType
                cancerDirNames = [tumorType]
            else:
                print " ERROR ??? tumorType <%s> not in list of known tumors? " % tumorType
                print cancerDirNames
                sys.exit(-1)

            suffixString = sys.argv[2]

            if (len(sys.argv) >= 4):
                path_to_stddata = sys.argv[3]
                topDir = path_to_stddata
            else:
                # if we are not told where to get the stddata, then get the
                # most recent ...
                firehoseTopDir = gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR'] + "/"
                topDir = getMostRecentDir(firehoseTopDir, cancerDirNames)

            if (len(sys.argv) == 5):
                subsetName = sys.argv[4]
                if (subsetName == "NA"):
                    subsetName = ""
                elif (not subsetName.endswith(".")):
                    subsetName += "."
            else:
                subsetName = ""

    outDir = "./"

    # outer loop over tumor types
    for zCancer in cancerDirNames:
        print ' '
        print ' PROCESSING FIREHOSE STDDATA FOR CANCER TYPE ', zCancer

        lastDir = getCancerDir(topDir, zCancer)

        # first we parse the Merge_Clinical output file
        if (1):
            parseClinicalDataFiles(
                lastDir, outDir, zCancer, subsetName, suffixString)

        # next we parse the methylation data file(s)
        if (1):
            parseMethylationDataFiles(
                lastDir, outDir, zCancer, subsetName, suffixString)

        # and then the microRNA data file(s)
        if (1):
            ## parseMicroRNADataFiles ( lastDir, outDir, zCancer, subsetName, suffixString )
            parseMatureMicroRNADataFiles(
                lastDir, outDir, zCancer, subsetName, suffixString)

        # and then RPPA data file(s)
        if (1):
            parseRPPADataFiles(lastDir, outDir, zCancer,
                               subsetName, suffixString)
            # not using this one for now ... if we want to use it, we will need
            # to split out just one gene name
            ## parseRPPADataFiles2 ( lastDir, outDir, zCancer, suffixString )

        # and then RNAseq data file(s)
        if (1):
            parseRNAseqDataFiles(
                lastDir, outDir, zCancer, subsetName, suffixString)

        # and finally the copy-number resegmentation ...
        if (1):
            parseSNP6dataFiles(lastDir, outDir, zCancer,
                               subsetName, suffixString)

        sys.exit(-1)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
