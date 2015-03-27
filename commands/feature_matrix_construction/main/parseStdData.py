# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars
import miscMath
import miscTCGA

import numpy
import path
import sys

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

        if (len(cancerList) == 1):
            if (d1Name.find("awg_") >= 0):
                if (d1Name.find(cancerList[0]) >= 0):
                    iDates += [getDate(d1Name)]

    iDates.sort()
    print iDates

    lastDate = str(iDates[-1])

    # HACK HACK HACK !!!
    if (lastDate == '20130421'):
        lastDate = str(iDates[-2])

    lastDate = lastDate[0:4] + "_" + lastDate[4:6] + "_" + lastDate[6:8]
    print lastDate

    lastDir = "NA"
    for d1Name in d1.dirs():
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


def getArchiveName(fName):

    i1 = len(fName) - 1
    while (fName[i1] != '/'):
        i1 -= 1
    i2 = i1 - 1
    while (fName[i2] != '/'):
        i2 -= 1

    archiveName = fName[i2 + 1:i1]
    print archiveName
    return (archiveName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def chopArchiveName(archiveName):

    tokenList = archiveName.split('.')
    print tokenList

    return (tokenList[2], tokenList[3], tokenList[5])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def add2sampleDict(fName, sampleDict):

    print " in add2sampleDict ... <%s> " % fName, len(sampleDict)

    archiveName = getArchiveName(fName)
    (setName, platformName, dateString) = chopArchiveName(archiveName)
    print setName,  platformName, dateString

    fh = file(fName)
    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()
        tokenList = aLine.split('\t')
        for aToken in tokenList:
            if (aToken.startswith("TCGA-")):
                possibleBarcode = aToken

                if (1):
                    if (possibleBarcode not in sampleDict.keys()):
                        print possibleBarcode
                        sampleDict[possibleBarcode] = [
                            (setName, platformName, dateString)]
                    else:
                        addFlag = 1
                        for aTuple in sampleDict[possibleBarcode]:
                            fullMatch = 1
                            if (setName != aTuple[0]):
                                fullMatch = 0
                            if (platformName != aTuple[1]):
                                fullMatch = 0
                            if (dateString != aTuple[2]):
                                fullMatch = 0
                            if (fullMatch):
                                addFlag = 0
                        if (addFlag):
                            sampleDict[
                                possibleBarcode] += [(setName, platformName, dateString)]
                            # print " repeated barcode ??? ", possibleBarcode
                            # print sampleDict[possibleBarcode]

    print len(sampleDict)
    return (sampleDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanupSampleDict(sampleDict):

    print len(sampleDict)
    print sampleDict

    cleanSampleDict = []

    for aSample in sampleDict:
        if (len(aSample) == 12):
            if (aSample not in cleanPatientList):
                cleanPatientList += [aSample]
        elif (len(aSample) == 16):
            shortB = aSample[:12]
            if (shortB not in cleanPatientList):
                cleanPatientList += [shortB]
            if (aSample not in cleanSampleDict):
                cleanSampleDict += [aSample]

    cleanPatientList.sort()
    cleanSampleDict.sort()

    return (cleanPatientList, cleanSampleDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# new code for building up a white list of samples based on all of the
# Level_4 firehose analysis outputs ...


def buildSampleWhiteList(lastDir, outDir):

    print " "
    print " START: parsing all mage-tab directories to build sample white list "
    print " "

    print lastDir

    sampleDict = {}

    d2 = path.path(lastDir)
    print " d2 : <%s> " % d2

    i1 = len(d2) - 1
    while (d2[i1] != '/'):
        i1 -= 1
    dateString = d2[i1 + 1:]
    print " dateString : <%s> " % dateString

    i2 = i1 - 1
    while (d2[i2] != '/'):
        i2 -= 1
    i3 = i2 - 1
    while (d2[i3] != '/'):
        i3 -= 1
    runName = d2[i3 + 1:i2]
    print " runName : <%s> " % runName

    for d2Name in d2.dirs():

        if (d2Name.find("mage-tab") > 0):

            d3 = path.path(d2Name)
            for fName in d3.files():

                if (fName.endswith(".sdrf.txt")):
                    sampleDict = add2sampleDict(fName, sampleDict)

    outName = outDir + "gdac.broadinstitute.org__" + \
        runName + "__" + dateString + ".sampleList.txt"
    fh = file(outName, 'w')
    keyList = sampleDict.keys()
    keyList.sort()
    for aKey in keyList:
        for aTuple in sampleDict[aKey]:
            fh.write("%s\t%s\t%s\t%s\n" %
                     (aKey, aTuple[0], aTuple[1], aTuple[2]))
    fh.close()

    sys.exit(-1)

    if (0):
        (cleanPatientList, cleanSampleDict) = cleanupSampleDict(sampleDict)

    outName = outDir + "gdac.broadinstitute.org_" + \
        runName + "__" + dateString + ".sampleList.txt"
    fh = file(outName, 'w')
    for aSample in sampleDict:
        fh.write("%s\n" % aSample)
    fh.close()

    print " "
    print " DONE: building sample white list ", len(cleanPatientList), len(cleanSampleDict)
    print " "

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
        'acc', 'blca', 'brca', 'cesc', 'cntl', 'coad', 'dlbc', 'esca', 'gbm', 'hnsc', 'kirc',
        'kirp', 'laml', 'lcll', 'lgg', 'lihc', 'lnnh', 'luad', 'lusc', 'ov', 'meso', 'tgct',
        'paad', 'prad', 'read', 'sarc', 'skcm', 'stad', 'thca', 'ucec', 'lcml', 'pcpg', 'ucs' ]

    if (1):
        if (len(sys.argv) != 2):
            print " Usage: %s <tumorType> " % sys.argv[0]
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        else:
            tumorType = sys.argv[1].lower()
            if (tumorType == "all"):
                print " this option is no longer allowed "
                sys.exit(-1)
                print " --> processing all tumor types: ", cancerDirNames
            elif (tumorType in cancerDirNames):
                print " --> processing a single tumor type: ", tumorType
                cancerDirNames = [tumorType]
            else:
                print " ERROR ??? tumorType <%s> not in list of known tumors? " % tumorType
                print cancerDirNames
                sys.exit(-1)

    firehoseTopDir = gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR']+ "/"
    outDir = "./"

    # first thing we have to do is find the most recent top-level directory
    topDir = getMostRecentDir(firehoseTopDir, cancerDirNames)
    print " here now : ", topDir

    # outer loop over tumor types
    for zCancer in cancerDirNames:
        print ' '
        print ' OUTER LOOP over CANCER TYPES ... ', zCancer

        lastDir = getCancerDir(topDir, zCancer)

        # build up the 'master' list of samples ...
        buildSampleWhiteList(lastDir, outDir)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
