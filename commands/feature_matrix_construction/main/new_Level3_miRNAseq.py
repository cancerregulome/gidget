# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import commands
import numpy
import os
import sys

# these are my local modules
from env import gidgetConfigVars
import miscIO
import miscTCGA
import path
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

debugON = 0
## debugON = 1

# NOTE: this is a modified script that handles ONLY the microRNAseq data
# from BCGSC
platformStrings = [
    'bcgsc.ca/illuminaga_mirnaseq/mirnaseq/',
    'bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/']

dataTypeDict = {}
dataTypeDict["IlluminaGA_miRNASeq"] = ["N", "MIRN"]
dataTypeDict["IlluminaHiSeq_miRNASeq"] = ["N", "MIRN"]

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# from Timo's resegmentation code:


class AutoVivification(dict):

    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getLastBit(aName):

    ii = len(aName) - 1
    while (aName[ii] != '/'):
        ii -= 1

    # print ' <%s>    <%s> ' % ( aName, aName[ii+1:] )

    return (aName[ii + 1:])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def loadNameMap(mapFilename):

    metaData = {}

    fh = file(mapFilename)
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        metaData[tokenList[1]] = tokenList[0]
    fh.close()

    return (metaData)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# hsa-let-7a-2 MIMAT0010195 N:MIRN:hsa-let-7a-2:::::MIMAT0010195


def makeFeatureName(tok0, tok1, metaData):

    try:
        featName = "N:MIRN:" + metaData[tok1] + ":::::" + tok1
        print " all good : ", tok0, tok1, featName
    except:
        featName = "N:MIRN:" + tok0 + ":::::" + tok1
        print " BAD ??? ", tok0, tok1, featName

    return (featName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def makeOutputFilename(outDir, tumorList, zString, outSuffix):

    if (len(tumorList) == 1):
        zCancer = tumorList[0]
    else:
        tumorList.sort()
        zCancer = tumorList[0]
        for aCancer in tumorList[1:]:
            zCancer = zCancer + '_' + aCancer
        print " --> combined multi-cancer name : <%s> " % zCancer

    # start by pasting together the outDir, cancer sub-dir, then '/'
    # and then the cancer name again, followed by a '.'
    outFilename = outDir + zCancer + "/" + zCancer + "."
    # now we are just going to assume that we are writing to the current
    # working directory (21dec12)
    outFilename = outDir + zCancer + "."

    # next we want to replace all '/' in the platform string with '__'
    i1 = 0
    while (i1 >= 0):
        i2 = zString.find('/', i1)
        if (i1 > 0 and i2 > 0):
            outFilename += "__"
        if (i2 > 0):
            outFilename += zString[i1:i2]
            i1 = i2 + 1
        else:
            i1 = i2

    # and finally we add on the suffix (usually something like '25jun')
    if (not outSuffix.startswith(".")):
        outFilename += "."
    outFilename += outSuffix

    return (outFilename)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    # list of cancer directory names
    cancerDirNames = [
        'acc',  'blca', 'brca', 'cesc', 'cntl', 'coad', 'dlbc', 'esca', 'gbm',
        'hnsc', 'kich', 'kirc', 'kirp', 'laml', 'lcll', 'lgg',  'lihc', 'lnnh',
        'luad', 'lusc', 'ov',   'paad', 'prad', 'read', 'sarc', 'skcm', 'stad',
        'thca', 'ucec', 'lcml', 'pcpg', 'meso', 'tgct', 'ucs' ]

    if (1):

        if (len(sys.argv) < 4):
            print " Usage: %s <outSuffix> <platformID> <tumorType#1> [tumorType#2 ...] [snapshot-name]"
            print " currently supported platforms : ", platformStrings
            print " currently supported tumor types : ", cancerDirNames
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        else:

            # output suffix ...
            outSuffix = sys.argv[1]

            # specified platform ...
            platformID = sys.argv[2]
            if (platformID[-1] != '/'):
                platformID += '/'
            if (platformID not in platformStrings):
                print " platform <%s> is not supported " % platformID
                print " currently supported platforms are: ", platformStrings
                sys.exit(-1)
            platformStrings = [platformID]

            # assume that the default snapshotName is "dcc-snapshot"
            snapshotName = "dcc-snapshot"

            # specified tumor type(s) ...
            argList = sys.argv[3:]
            # print argList
            tumorList = []
            for aType in argList:

                tumorType = aType.lower()
                if (tumorType in cancerDirNames):
                    tumorList += [tumorType]
                elif (tumorType.find("snap") >= 0):
                    snapshotName = tumorType
                    print " using this snapshot : <%s> " % snapshotName
                else:
                    print " ERROR ??? tumorType <%s> not in list of known tumors ??? " % tumorType
                    print cancerDirNames

            if (len(tumorList) < 1):
                print " ERROR ??? have no tumor types in list ??? ", tumorList
                sys.exit(-1)

            print " tumor type(s) list : ", tumorList

    # --------------------------------------
    # HERE is where the real work starts ...
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # now we need to get set up for writing the output ...
    # NEW: 21dec12 ... assuming that we will write to current working directory
    outDir = "./"
    outFilename = makeOutputFilename(
        outDir, tumorList, platformID, outSuffix)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # initialize a bunch of things ...
    sampleList = []
    gotFiles = []
    geneList = []
    numGenes = 0
    numProc = 0
    iS = 0

    # and then loop over tumor types ...
    for zCancer in tumorList:
        print ' '
        print ' ********************************** '
        print ' LOOP over %d CANCER TYPES ... %s ' % (len(tumorList), zCancer)

        # piece together the directory name ...
        ## topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/dcc-snapshot/public/tumor/" + zCancer + "/cgcc/" + platformID
        topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/" + \
            snapshotName + "/public/tumor/" + zCancer + "/cgcc/" + platformID

        print ' starting from top-level directory ', topDir

        dMatch = "Level_3"

        if (not os.path.exists(topDir)):
            print '     --> <%s> does not exist ' % topDir
            continue

        d1 = path.path(topDir)
        for dName in d1.dirs():

            print dName

            if (dName.find(dMatch) >= 0):
                print ' '
                print '     found a <%s> directory : <%s> ' % (dMatch, dName)
                archiveName = getLastBit(dName)
                print '     archiveName : ', archiveName
                if (dName.find("IlluminaHiSeq") > 0):
                    zPlat = "IlluminaHiSeq_miRNASeq"
                elif (dName.find("IlluminaGA") > 0):
                    zPlat = "IlluminaGA_miRNASeq"
                else:
                    print " not a valid platform: %s ??? !!! " % (dName)
                    sys.exit(-1)


                cmdString = "%s/shscript/expression_matrix_mimat.pl " % gidgetConfigVars['TCGAFMP_ROOT_DIR']
                cmdString += "-m " + gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/mirna_bcgsc/tcga_mirna_bcgsc_hg19.adf "
                cmdString += "-o %s " % outDir
                cmdString += "-p %s " % topDir
                cmdString += "-n %s " % zPlat

                print " "
                print cmdString
                print " "
                (status, output) = commands.getstatusoutput(cmdString)

                normMatFilename = outDir + "/expn_matrix_mimat_norm_%s.txt" % (zPlat)
                print " normMatFilename = <%s> " % normMatFilename

                # make sure that we can open this file ...
                try:
                    fh = file(normMatFilename, 'r')
                    gotFiles += [normMatFilename]
                    fh.close()
                except:
                    print " "
                    print " Not able to open expn_matrix_mimat_norm file ??? "
                    print " "
                    sys.exit(-1)

    print " "
    print " "
    if (len(gotFiles) == 0):
        print " ERROR in new_Level3_miRNAseq ... no data files found "
        sys.exit(-1)
    if (len(gotFiles) > 1):
        print " ERROR ??? we should have only one file at this point "
        print gotFiles
        sys.exit(-1)

    # if we get this far, we should make sure that the output directory we
    # want exists
    print " --> testing that we have an output directory ... <%s> " % outDir
    tsvIO.createDir(outDir)
    print "     output file name will be called <%s> " % outFilename

    # we also need to read in the mapping file ...
    metaData = loadNameMap(
        gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/mirna_bcgsc/mature.fa.flat.human.mirbase_v19.txt")

    if (1):

        fh = file(gotFiles[0], 'r')
        numRow = miscIO.num_lines(fh) - 1
        numCol = miscIO.num_cols(fh, '\t') - 1

        rowLabels = []
        dataMatrix = [0] * numRow
        for iR in range(numRow):
            dataMatrix[iR] = [0] * numCol

        hdrLine = fh.readline()
        hdrLine = hdrLine.strip()
        hdrTokens = hdrLine.split('\t')
        if (len(hdrTokens) != (numCol + 1)):
            print " ERROR #1 ??? "
            sys.exit(-1)

        done = 0
        iR = 0
        numNA = 0
        while (not done):
            aLine = fh.readline()
            aLine = aLine.strip()
            tokenList = aLine.split('\t')
            if (len(tokenList) != (numCol + 1)):
                done = 1
            else:
                aLabel = tokenList[0]
                # print " label = <%s> " % aLabel
                labelTokens = aLabel.split('.')
                # print labelTokens
                featName = makeFeatureName(
                    labelTokens[0], labelTokens[1], metaData)
                # print featName
                rowLabels += [featName]

                for iC in range(numCol):
                    try:
                        fVal = float(tokenList[iC + 1])
                        dataMatrix[iR][iC] = fVal
                    except:
                        dataMatrix[iR][iC] = NA_VALUE
                        numNA += 1
                iR += 1
                print " iR=%d    numNA=%d " % (iR, numNA)

        dataD = {}
        dataD['rowLabels'] = rowLabels
        dataD['colLabels'] = hdrTokens[1:]
        dataD['dataMatrix'] = dataMatrix
        dataD['dataType'] = "N:MIRN"
        print ' writing out data matrix to ', outFilename

        newFeatureName = "C:SAMP:mirnPlatform:::::seq"
        newFeatureValue = zPlat
        dataD = tsvIO.addConstFeature(dataD, newFeatureName, newFeatureValue)

        sortRowFlag = 0
        sortColFlag = 0
        tsvIO.writeTSV_dataMatrix(
            dataD, sortRowFlag, sortColFlag, outFilename)

    print ' '
    print ' DONE !!! '
    print ' '


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
