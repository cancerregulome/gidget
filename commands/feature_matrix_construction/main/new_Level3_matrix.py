# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
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

# center/platform/data-type strings
# note that these are the 'new' centers and platforms -- this list does
# not necessarily include all of platforms that were used in the pilot
## phase (GBM and OV)
platformStrings = [
    # 'bcgsc.ca/miRNASeq/',			OBSOLETE !!!
    'bcgsc.ca/illuminaga_mirnaseq/mirnaseq/',
    'bcgsc.ca/illuminaga_rnaseq/rnaseq/',
    'bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/',
    'bcgsc.ca/illuminahiseq_rnaseq/rnaseq/',
    'broad.mit.edu/genome_wide_snp_6/snp/',
    'broad.mit.edu/ht_hg-u133a/transcriptome/',
    'genome.wustl.edu/genome_wide_snp_6/snp/',
    'jhu-usc.edu/humanmethylation27/methylation/',
    'jhu-usc.edu/humanmethylation450/methylation/',
    'mdanderson.org/mda_rppa_core/protein_exp/',
    'nationwidechildrens.org/microsat_i/fragment_analysis/',
    'unc.edu/agilentg4502a_07_1/transcriptome/',
    'unc.edu/agilentg4502a_07_2/transcriptome/',
    'unc.edu/agilentg4502a_07_3/transcriptome/',
    # 'unc.edu/RNASeq/',				OBSOLETE !!!
    'unc.edu/illuminaga_rnaseq/rnaseq/',
    'unc.edu/illuminaga_rnaseqv2/rnaseqv2/',
    'unc.edu/illuminahiseq_rnaseq/rnaseq/',
    'unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/',
    'unc.edu/h-mirna_8x15k/mirna/',
    'unc.edu/h-mirna_8x15kv2/mirna/']


dataTypeDict = {}
dataTypeDict["HT_HG-U133A"] = ["N", "GEXP", "array"]
dataTypeDict["AgilentG4502A_07_1"] = ["N", "GEXP", "array"]
dataTypeDict["AgilentG4502A_07_2"] = ["N", "GEXP", "array"]
dataTypeDict["AgilentG4502A_07_3"] = ["N", "GEXP", "array"]
dataTypeDict["H-miRNA_8x15K"] = ["N", "MIRN", "array"]
dataTypeDict["HumanMethylation27"] = ["N", "METH", "beadchip"]
dataTypeDict["HumanMethylation450"] = ["N", "METH", "beadchip"]
dataTypeDict["IlluminaGA_RNASeq"] = ["N", "GEXP", "seq"]
dataTypeDict["IlluminaGA_RNASeqV2"] = ["N", "GEXP", "seq"]
dataTypeDict["IlluminaHiSeq_RNASeq"] = ["N", "GEXP", "seq"]
dataTypeDict["IlluminaHiSeq_RNASeqV2"] = ["N", "GEXP", "seq"]
dataTypeDict["Genome_Wide_SNP_6"] = ["N", "CNVR", "array"]
dataTypeDict["IlluminaGA_miRNASeq"] = ["N", "MIRN", "seq"]
dataTypeDict["IlluminaHiSeq_miRNASeq"] = ["N", "MIRN", "seq"]
dataTypeDict["MDA_RPPA_Core"] = ["N", "RPPA", "array"]
dataTypeDict["microsat_i"] = ["C", "SAMP", "pcr"]

RPPAdict = {}

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

# Unifies the naming convention for X and Y chromosomes, and removes
# possible 'hs' and 'chr' prefixes


def unifychr(chr):
    if chr[0:2] == 'hs':
        chr = chr[2:]
    elif chr[0:3] == 'chr':
        chr = chr[3:]
    if (chr == '23'):
        chr = 'X'
    elif (chr == '24'):
        chr = 'Y'
    return chr

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def sanityCheckSDRF(sdrfFilename):

    try:
        fh = file(sdrfFilename)
    except:
        print " ERROR in sanityCheckSDRF ??? failed to open file ??? "
        print sdrfFilename
        sys.exit(-1)

    nl = miscIO.num_lines(fh)
    nr = min(nl / 2, 5)
    nt = [0] * nr
    for ii in range(nr):
        aLine = fh.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        nt[ii] = len(tokenList)

    ntMin = min(nt)
    ntMax = max(nt)
    for jj in range(nl - nr):
        aLine = fh.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        ntCur = len(tokenList)
        if (ntCur == 0):
            continue
        if (ntCur < ntMin):
            print " ERROR in sanityCheckSDRF ??? file appears to have been truncated ??? "
            print ntCur, ntMin, ntMax
            print tokenList
            sys.exit(-1)

    fh.close()

    return (1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getSDRFinfo(sdrfFilename):

    print ' '
    print ' in getSDRFinfo ... <%s> ' % sdrfFilename

    okFlag = sanityCheckSDRF(sdrfFilename)

    # figure out which platform it is based on the SDRF file ...
    platformList = [
        "HT_HG-U133A", "AgilentG4502A_07_1", "AgilentG4502A_07_2", "AgilentG4502A_07_3",
        "H-miRNA_8x15K", "HumanMethylation27", "HumanMethylation450",
        "IlluminaGA_RNASeq", "IlluminaGA_RNASeqV2",
        "IlluminaHiSeq_RNASeq", "IlluminaHiSeq_RNASeqV2",
        "Genome_Wide_SNP_6",
        "IlluminaGA_miRNASeq", "IlluminaHiSeq_miRNASeq",
        "MDA_RPPA_Core", "microsat_i"]

    zPlat = "unknown"
    for aPlat in platformList:
        if (sdrfFilename.find(aPlat) > 0):
            zPlat = aPlat
    if (zPlat == "unknown"):
        print " ERROR ??? unknown platform ??? "
        print sdrfFilename
        print platformList
        sys.exit(-1)
    else:
        print " Platform : ", zPlat

    sdrfDict = {}

    fh = file(sdrfFilename)
    print " reading SDRF file : ", sdrfFilename
    hdrLine = fh.readline()
    hdrLine = hdrLine.strip()
    hdrTokens = hdrLine.split('\t')
    numTokens = len(hdrTokens)

    if (0):
        print '     header tokens: ', numTokens
        for ii in range(numTokens):
            print '             %2d : <%s> ' % (ii, hdrTokens[ii])
        sys.exit(-1)

    done = 0
    lineNum = 0
    while not done:
        aLine = fh.readline()
        aLine = aLine.strip()
        aTokens = aLine.split('\t')
        if (len(aTokens) < numTokens):
            done = 1
            continue
        else:

            lineNum += 1

            if (0):
                print zPlat
                print '     header tokens: ', numTokens
                for ii in range(numTokens):
                    print '             %2d : <%35s>   <%s> ' % (ii, hdrTokens[ii], aTokens[ii])
                sys.exit(-1)

            # print " in getSDRFinfo:   line # %4d    zPlat=<%s>
            # numTokens=%d " % ( lineNum, zPlat, numTokens )

            if (zPlat == "HT_HG-U133A"):
                if (numTokens == 34):
                    iLevel3 = 31
                    iBarcode = 1
                    iFilename = 28
                    iArchive = 29
                    iYes = 32
                    iOther = 27
                else:
                    iLevel3 = 30
                    iBarcode = 0
                    iFilename = 27
                    iArchive = 28
                    iYes = 31
                    iOther = 26

            elif (zPlat == "AgilentG4502A_07_1"):
                if (numTokens == 44):
                    iLevel3 = 41
                    iBarcode = 0
                    iFilename = 39
                    iArchive = 43
                    iYes = 42
                    iOther = 17
                else:
                    iLevel3 = 40
                    iBarcode = 0
                    iFilename = 38
                    iArchive = 42
                    iYes = 41
                    iOther = 16

            elif (zPlat == "AgilentG4502A_07_2"):
                if (numTokens == 44):
                    iLevel3 = 41
                    iBarcode = 0
                    iFilename = 39
                    iArchive = 43
                    iYes = 42
                    iOther = 17
                else:
                    iLevel3 = 40
                    iBarcode = 0
                    iFilename = 38
                    iArchive = 42
                    iYes = 41
                    iOther = 16

            elif (zPlat == "AgilentG4502A_07_3"):
                if (numTokens == 47):
                    iLevel3 = 43
                    iBarcode = 0
                    iFilename = 41
                    iArchive = 45
                    iYes = 44
                    iOther = 17
                elif (numTokens == 43):
                    iLevel3 = 40
                    iBarcode = 0
                    iFilename = 38
                    iArchive = 42
                    iYes = 41
                    iOther = 16
                elif (numTokens == 46):
                    iLevel3 = 42
                    iBarcode = 0
                    iFilename = 40
                    iArchive = 44
                    iYes = 43
                    iOther = 16
                elif (numTokens == 44):
                    iLevel3 = 41
                    iBarcode = 0
                    iFilename = 39
                    iArchive = 43
                    iYes = 42
                    iOther = 17  # iOther is supposed to be the cy3/cy5 label
                else:
                    print " ERROR ??? incorrect number of tokens for Agilent SDRF ??? "
                    print numTokens, lineNum
                    print aTokens
                    sys.exit(-1)

            elif (zPlat == "H-miRNA_8x15K"):
                if (numTokens == 32):
                    iLevel3 = 29
                    iBarcode = 26
                    iFilename = 27
                    iArchive = 31
                    iYes = 30
                    iOther = 28
                else:
                    iLevel3 = 28
                    iBarcode = 25
                    iFilename = 26
                    iArchive = 30
                    iYes = 29
                    iOther = 27

            elif (zPlat == "HumanMethylation27"):
                # looks like the new data has 33 tokens, and the indices should be 30, 1, 27, 28, 31, 29
                # whereas before that there were also 33 tokens, but the
                # indices are: 29, 0, 28, 32, 31, 30
                if (numTokens == 33):
                    if (aTokens[0].startswith("TCGA-")):
                        iLevel3 = 29
                        iBarcode = 27
                        iFilename = 28
                        iArchive = 32
                        iYes = 31
                        iOther = 30
                    elif (aTokens[1].startswith("TCGA-")):
                        iLevel3 = 30
                        iBarcode = 1
                        iFilename = 27
                        iArchive = 28
                        iYes = 31
                        iOther = 29
                    else:
                        print " ERROR parsing tokens for <%s> ??? " % zPlat
                        sys.exit(-1)
                elif (numTokens == 34):
                    if (aTokens[1].startswith("TCGA-")):
                        iLevel3 = 30
                        iBarcode = 1
                        iFilename = 29
                        iArchive = 33
                        iYes = 32
                        iOther = 31
                    else:
                        print " ERROR parsing tokens for <%s> ??? " % zPlat
                        sys.exit(-1)

                elif (numTokens == 31):
                    iLevel3 = 29
                    iBarcode = 25
                    iFilename = 26
                    iArchive = 27
                    iYes = 30
                    iOther = 28
                elif (numTokens == 35):
                    iLevel3 = 29
                    iBarcode = 27
                    iFilename = 28
                    iArchive = 32
                    iYes = 31
                    iOther = 30
                else:
                    print " ERROR ??? incorrect number of tokens for Methylation27 SDRF ??? "
                    print numTokens, lineNum
                    print aTokens
                    sys.exit(-1)

            elif (zPlat == "HumanMethylation450"):
                # new block for the newest methylation SDRF data which now includes
                # the UUIDs as well as mention of hg19
                if (numTokens == 33):
                    iLevel3 = 30
                    iBarcode = 26
                    iFilename = 27
                    iArchive = 28
                    iYes = 31
                    iOther = 29
                elif (numTokens > 30):
                    iLevel3 = 29
                    iBarcode = 25
                    iFilename = 26
                    iArchive = 27
                    iYes = 30
                    iOther = 28
                else:
                    # if there are not enough tokens, that probably means that there is
                    # no level-3 data described in this SDRF ...
                    print " ERROR ??? too few tokens for Methylation450 SDRF ??? "
                    print numTokens, lineNum
                    print aTokens
                    return (sdrfDict, [], [], zPlat)
                    # sys.exit(-1)

            elif (zPlat == "IlluminaGA_RNASeq"):
                if (numTokens == 26):
                    # this should be correct BOTH for UNC BCGSC Illumina GA
                    # RNAseq data ...
                    iLevel3 = 24
                    iBarcode = 1
                    iFilename = 21
                    iArchive = 25
                    iYes = 22
                    iOther = 23
                    print " "
                    print aTokens
                    if (aTokens[iOther].find("Expression-Gene") < 0):
                        continue
                else:
                    # this is old ...
                    iLevel3 = 23
                    iBarcode = 0
                    iFilename = 20
                    iArchive = 24
                    iYes = 21
                    iOther = 19
                    if (aTokens[iOther].find("gene_expression") < 0):
                        # print " IlluminaGA_RNASeq : not including <%s> " %
                        # aTokens[iFilename]
                        continue

            elif (zPlat == "IlluminaHiSeq_RNASeq"):
                # this platform is in use at both UNC and BCGSC ... although it looks
                # like the mage-tab files are the same or nearly so ...
                if (aTokens[2].startswith("unc.edu") or aTokens[3].startswith("unc.edu")):
                    if (len(aTokens) == 25):
                        iLevel3 = 23
                        iBarcode = 0
                        iFilename = 20
                        iArchive = 24
                        iYes = 21
                        iOther = 19
                    else:
                        iLevel3 = 24
                        iBarcode = 1
                        iFilename = 21
                        iArchive = 25
                        iYes = 22
                        iOther = 20
                    if (aTokens[iOther].find("gene_expression") < 0):
                        # print " IlluminaHiSeq_RNASeq : not including <%s> " %
                        # aTokens[iFilename]
                        continue
                elif (aTokens[2].startswith("bcgsc.ca") or aTokens[3].startswith("bcgsc.ca")):
                    if (len(aTokens) == 26):
                        iLevel3 = 24
                        iBarcode = 1
                        iFilename = 21
                        iArchive = 25
                        iYes = 22
                        iOther = 20
                        if (aTokens[iOther].find("gene_expression") < 0):
                            # print " IlluminaHiSeq_RNASeq : not including <%s>
                            # " % aTokens[iFilename]
                            continue
                    else:
                        iLevel3 = 23
                        iBarcode = 0
                        iFilename = 20
                        iArchive = 24
                        iYes = 21
                        iOther = 19
                        if (aTokens[iOther].find("gene_expression") < 0):
                            # print " IlluminaHiSeq_RNASeq : not including <%s>
                            # " % aTokens[iFilename]
                            continue

            elif (zPlat == "IlluminaHiSeq_RNASeqV2"):
                if (len(aTokens) == 26):
                    iLevel3 = 24
                    iBarcode = 1
                    iFilename = 21
                    iArchive = 25
                    iYes = 22
                    iOther = 23
                else:
                    iLevel3 = 23
                    iBarcode = 0
                    iFilename = 20
                    iArchive = 24
                    iYes = 21
                    iOther = 22
                # there are several types of files coming out of the V2 pipeline:
                # RSEM_genes		-->	*.rsem.genes.results
                # RSEM_genes_normalized	-->	*.rsem.genes.normalized_results
                # RSEM_isoforms		-->	*.rsem.isoforms.results
                # RSEM_isoforms_normalized-->	*.rsem.isoforms.normalized_results
                # exon_quantification	-->	*.exon_quantification.txt
                # junction_quantification	-->	*.junction_quantification.txt
                # for now we will take the RSEM_genes_normalized results only:
                if (aTokens[iOther] != "RSEM_genes_normalized"):
                    # print " IlluminaHiSeq_RNASeqV2 : not including <%s> " %
                    # aTokens[iFilename]
                    continue

            elif (zPlat == "IlluminaGA_RNASeqV2"):
                if (len(aTokens) == 26):
                    iLevel3 = 24
                    iBarcode = 1
                    iFilename = 21
                    iArchive = 25
                    iYes = 22
                    iOther = 23
                else:
                    print " ERROR ??? wrong number of tokens in SDRF ??? "
                    sys.exit(-1)

                # same as above -- taking the RSEM_genes_normalized file
                if (aTokens[iOther] != "RSEM_genes_normalized"):
                    # print " IlluminaGA_RNASeqV2 : not including <%s> " %
                    # aTokens[iFilename]
                    continue

            elif (zPlat == "IlluminaGA_miRNASeq"):
                if (len(aTokens) == 26):
                    iLevel3 = 24
                    iBarcode = 1
                    iFilename = 21
                    iArchive = 25
                    iYes = 22
                    iOther = 23
                else:
                    iLevel3 = 23
                    iBarcode = 0
                    iFilename = 20
                    iArchive = -1  # no archive information ???
                    iYes = 21
                    iOther = 22
                if (aTokens[iOther].find("Expression-miRNA Isoform") >= 0):
                    # print " IlluminaGA_miRNASeq : not including <%s> " %
                    # aTokens[iFilename]
                    continue

            elif (zPlat == "IlluminaHiSeq_miRNASeq"):
                if (len(aTokens) == 26):
                    iLevel3 = 24
                    iBarcode = 1
                    iFilename = 21
                    iArchive = 25
                    iYes = 22
                    iOther = 23
                else:
                    iLevel3 = 23
                    iBarcode = 0
                    iFilename = 20
                    iArchive = -1  # no archive information ???
                    iYes = 21
                    iOther = 22
                if (aTokens[iOther].find("Expression-miRNA Isoform") >= 0):
                    # print " IlluminaHiSeq_miRNASeq : not including <%s> " %
                    # aTokens[iFilename]
                    continue

            elif (zPlat == "Genome_Wide_SNP_6"):

                # just discovered that there is some SNP6 data from WashU for LAML,
                # so am now splitting here according to center name ...

                if (sdrfFilename.find("broad.mit.edu") > 0):

                    # 16-aug: the newest '2003' mage-tab files seem to be differet ...
                    # these exist as of now for brca, cesc and dlbc ... all other tumor types have '2002'
                    # 66 should be the file ending in .hg18.seg.txt
                    # and #75 should be the file ending in .hg19.seg.txt
                    # and #84 should be the file ending in .nocnv_hg18.seg.txt
                    # and #93 should be the file ending in .nocnv_hg19.seg.txt

                    # ( all of these indices used to be 67, 76, etc )

                    # this platform is a bit of a problem right now because of
                    # the barcode to UUID transition ...

                    if (len(aTokens) == 101):
                        ## iFilename = 76
                        iFilename = 94
                    elif (len(aTokens) == 100):
                        ## iFilename = 75
                        iFilename = 93
                    else:
                        print " ERROR ??? unexpected number of tokens in SNP6 SDRF ??? "
                        sys.exit(-1)

                    iArchive = iFilename + 1
                    iOther = iFilename + 2
                    iLevel3 = iFilename + 3
                    iYes = iFilename + 4

                    # the above I think is fairly consistent, but where the barcode is is not ...
                    # 0123456789012345678901234567
                    # TCGA-06-0152-02A-01D-2002-01
                    iBarcode = -1
                    found = 0
                    quitNow = 0
                    while (not found and not quitNow):
                        iBarcode += 1
                        try:
                            tstToken = aTokens[iBarcode]
                            if (miscTCGA.looks_like_barcode(tstToken)):
                                found = 1
                        except:
                            if (iBarcode >= len(aTokens)):
                                quitNow = 1

                    if (not found):
                        print " ERROR ??? failed to find barcode in SNP6 SDRF ??? "
                        sys.exit(-1)

                    print " --> using iBarcode=%d ... <%s> <%s> " % (iBarcode, aTokens[iBarcode], aTokens[iFilename])

                elif (sdrfFilename.find("genome.wustl.edu") > 0):

                    print len(aTokens)
                    print aTokens

                    iFilename = 51
                    iArchive = 52
                    iOther = 53
                    iLevel3 = 54
                    iYes = 55

                    iBarcode = 1

            elif (zPlat == "MDA_RPPA_Core"):
                iLevel3 = 60
                iBarcode = 4  # this is actually the UUID not a barcode
                iFilename = 57
                iArchive = 61
                iYes = 58
                iOther = 59

                # grab the UUID and translate it to a barcode ...
                barcode = aTokens[iBarcode]
                if (miscTCGA.looks_like_uuid(barcode)):
                    barcode = miscTCGA.uuid_to_barcode(barcode)
                else:
                    if (barcode.startswith("Control")):
                        continue
                    else:
                        print " ERROR in handling RPPA data ??? this field in the SDRF should be a UUID ??? <%s> " % barcode
                        continue

                if (not barcode.startswith("TCGA-")):
                    # print " MDA_RPPA_Core : not including <%s> " %
                    # aTokens[iFilename]
                    continue

            elif (zPlat == "microsat_i"):
                if (len(aTokens) == 14):
                    iLevel1 = 6
                    iLevel3 = -1
                    iBarcode = 1
                    iFilename = 9
                    iArchive = 10
                    iYes = 13
                    iOther = 11
                else:
                    iLevel1 = 5
                    iLevel3 = -1
                    iBarcode = 0
                    iFilename = 8
                    iArchive = 9
                    iYes = 12
                    iOther = 10

            else:
                print " "
                print " FATAL ERROR !!! should not get here !!! where did this platform come from ??? "
                print zPlat
                print " "
                sys.exit(-1)

            # a few more checks before we include this ...
            includeFlag = 1

            # verify that the correct token says "level 3" (or "level 1" for
            # microsat_i data)
            try:
                if (aTokens[iLevel3].lower() != "level 3"):
                    if (aTokens[iLevel3] != "->"):
                        print ' bad token ??? should say Level 3 ??? ', iLevel3, aTokens[iLevel3]
                        print aTokens
                        sys.exit(-1)
                    if (aTokens[iFilename] != "->"):
                        print ' (a) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes]
                        includeFlag = 0
            except:
                try:
                    if (aTokens[iLevel1].lower() != "level 1"):
                        print ' bad token ??? should say Level 1 ??? ', iLevel1, aTokens[iLevel1]
                        print aTokens
                        sys.exit(-1)
                except:
                    print " ERROR in getSDRFinfo ??? "
                    print len(aTokens), zPlat
                    print aTokens
                    sys.exit(-1)

            # verify that the "include for analysis" column says "yes"
            # print iYes, len(aTokens)
            # print aTokens
            if (includeFlag and (aTokens[iYes].lower() == "yes")):
                barcode = aTokens[iBarcode]

                # typical full barcode looks like this:
                # TCGA-A1-A0SE-01A-11R-A085-13
                # need 12 characters to identify patient
                # 16 characters to identify sample
                # 20 characters to ientify aliquot
                # 25 characters to include plate id
                # 28 characters to include cgcc id

                # added some functionality to miscTCGA and this step here on 21jun2012 ...
                # and a typical UUID looks like this:
                # 6d41d8c9-f2bf-4440-8b8d-907e3b2682f5
                if (miscTCGA.looks_like_uuid(barcode)):
                    barcode = miscTCGA.uuid_to_barcode(barcode)
                    # if this fails to map the UUID to a barcode it will return "NA"
                    # which will fail the next trap ...

                # adding this trap 03May2012 ...
                if (1):
                    if (not barcode.startswith("TCGA-")):
                        if (1):
                            print ' (a) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes]
                            includeFlag = 0
                        else:
                            print " ERROR in getSDRFinfo ??? this is supposed to be a barcode: <%s> " % barcode
                            sys.exit(-1)

                if (len(barcode) > 28):
                    barcode = barcode[:28]
                filename = aTokens[iFilename]
                if (iArchive >= 0):
                    archive = aTokens[iArchive]
                else:
                    archive = "unknown"
                otherInfo = aTokens[iOther]
            else:
                print ' (b) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes]
                includeFlag = 0

            # if this is an Agilent platform, then we only want this if it is
            # the cy5 channel ...
            if (includeFlag and (zPlat.startswith("AgilentG4502") and otherInfo != "cy5")):
                print ' (c) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes], zPlat, otherInfo
                includeFlag = 0

            # if this is the SNP platform, we're only keeping tumor samples ...
            # (which means they can be 01, 02, 06 ... I think anything that starts with a '0' basically)
            if (includeFlag and (zPlat == "Genome_Wide_SNP_6")):
                if (aTokens[iBarcode][13] != "0"):
                    print ' (d) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes], zPlat, otherInfo
                    includeFlag = 0
                else:
                    print ' (d) YES including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes], zPlat, otherInfo

            # sanity check that we don't have duplicate barcodes ...
            if (includeFlag and (barcode in sdrfDict.keys())):
                if (1):
                    print " WARNING ??? this key is already being used in this dictionary ??? ", barcode
                    print lineNum, barcode, archive, filename
                    print aTokens
                includeFlag = 0
                # sys.exit(-1)

            # sanity check that the barcode looks like a TCGA barcode
            if (includeFlag and (not barcode.startswith("TCGA-"))):
                print " non-TCGA barcode ??? ", barcode, " --> NOT including "
                # print lineNum, barcode, archive, filename
                # print aTokens
                includeFlag = 0
                # sys.exit(-1)

            if (includeFlag):
                sdrfDict[barcode] = (archive, filename, otherInfo)
                print ' YES including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes]
            else:
                if (aTokens[iFilename] != "->"):
                    print ' (e) NOT including this file ... ', iFilename, aTokens[iFilename], iBarcode, aTokens[iBarcode], iYes, aTokens[iYes]

    print ' --> returning from getSDRFinfo ... %d ' % (len(sdrfDict))
    if (len(sdrfDict) > 1):
        keyList = sdrfDict.keys()
        keyList.sort()
        print keyList[0], sdrfDict[keyList[0]]

    # now we want to build a list of archives and a list of files from the
    # sdrfDict ...
    archiveList = []
    fileList = []
    for aKey in sdrfDict.keys():
        if (sdrfDict[aKey][0] not in archiveList):
            archiveList += [sdrfDict[aKey][0]]
        if (sdrfDict[aKey][1] not in fileList):
            fileList += [sdrfDict[aKey][1]]

    archiveList.sort()
    fileList.sort()
    print '             have %d archives and %d data files ' % (len(archiveList), len(fileList))
    if (len(archiveList) == 0):
        print " ERROR ??? why are there no archives to be processed ??? "
    if (len(fileList) == 0):
        print " ERROR ??? why are there no files to be processed ??? "

    if (0):
        print ' '
        print ' list of archives : (%d) ' % (len(archiveList))
        print archiveList
        print ' '
        print ' list of files : (%d) ' % (len(fileList))
        # print fileList
        sys.exit(-1)

    return (sdrfDict, archiveList, fileList, zPlat)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def cleanString_OLD(aString):

    ii = aString.find("'")
    if (ii >= 0):
        bString = aString[:ii] + aString[ii + 1:]
        # print " in cleanString : <%s> <%s> " % ( aString, bString )
        aString = bString

    ii = aString.find('"')
    if (ii >= 0):
        bString = aString[:ii] + aString[ii + 1:]
        # print " in cleanString : <%s> <%s> " % ( aString, bString )
        aString = bString

    return (aString)

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
    if (bString == "stage_0"):
        # print " Transforming <STAGE 0> to <TIS> "
        bString = "tis"

    if (bString.startswith("stage_")):
        bString = bString[6:]
    if (bString.startswith("grade_")):
        bString = bString[6:]

    try:
        while (bString[-1] == "_"):
            bString = bString[:-1]
    except:
        doNothing = 1

    # print "     returning bString <%s> " % bString
    return (bString)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# the feature name is to be of the form:
# DTYPE:FTYPE:FNAME:CHR:START:STOP:STRAND:EXTRA
# for example:
# N:GEXP:BRCA2:chr13:31787617:31871809:+:U133A


def makeFeatureName(dType, fType, fName, chr='', start=-1, stop=-1, strand='', xName=''):

    # start out with LOTS of sanity checking of these input values ...

    if (dType != 'N' and dType != 'C' and dType != 'B'):
        print " ERROR in makeFeatureName ... dType should be B or C or N ", dType
        sys.exit(-1)

    if (fType.find(":") > 0):
        print " ERROR in makeFeatureName ... fType contains colon ???!!! ", fType
        sys.exit(-1)

    if (0):
        if (fName.find(":") > 0):
            print " WARNING in makeFeatureName ... fName contains colon ???!!! ", fName
            ii = fName.find(":")
            fName = fName[:ii] + fName[ii + 1:]

    fType = cleanString(fType)
    fName = cleanString(fName)

    if (chr != ''):
        try:
            iChr = int(chr)
            if (iChr < 0 or iChr > 22):
                print " ERROR in makeFeatureName ... invalid chromosome ??? ", chr
                sys.exit(-1)
        except:
            aChr = chr.upper()
            if (aChr != 'X' and aChr != 'Y' and aChr != 'M'):
                print " ERROR in makeFeatureName ... invalid chromosome ??? ", chr
                sys.exit(-1)

    if (strand != '+' and strand != '-' and strand != ''):
        print " ERROR in makeFeatureName ... invalid strand ??? ", strand
        sys.exit(-1)

    if (fType == "RPPA"):
        if (len(RPPAdict) == 0):
            print " reading in RPPA annotation file ... "
            fh = file( gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] + "/tcga_platform_genelists/MDA_antibody_annotation_2014_03_04.txt" )
            for aLine in fh:
                aLine = aLine.strip()
                aLine = aLine.split('\t')
                if (len(aLine) == 2):
                    if (aLine[0] != "Gene Name"):
                        if (aLine[1] not in RPPAdict.keys()):
                            RPPAdict[aLine[1]] = aLine[0]
            fh.close()
        # move the 'gene name' to the 'extra stuff', and then get the gene name
        # from RPPAdict
        xName = fName
        fName = RPPAdict[xName]
        print " mapped %s to %s " % (xName, fName)

    # paste the first few pieces of information together ...
    tmpName = dType + ":" + fType + ":" + fName + ":"

    # add chromosome string
    if (chr != ''):
        tmpName += "chr" + chr
    tmpName += ":"

    # add (start) position
    if (start >= 0):
        tmpName += "%d" % start
    tmpName += ":"

    # add stop position
    if (stop >= 0):
        tmpName += "%d" % stop
    tmpName += ":"

    if (strand != ''):
        tmpName += "%s" % strand
    tmpName += ":"

    if (xName != ''):
        tmpName += "%s" % xName

    # print " --> feature name <%s> " % tmpName

    # double-check that there are no question marks ...
    while (tmpName.find("?") >= 0):
        ii = tmpName.find("?")
        tmpName = tmpName[:ii] + tmpName[ii + 1:]

    return (tmpName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readOneDataFile(fName, geneList, zPlat, metaData):

    print " "

    try:
        fh = file(fName)
        print " in readOneDataFile ... ", zPlat, len(geneList)
        print fName
    except:
        print " ERROR in readOneDataFile ... ", zPlat
        print " failed to open input file !?!?! ", fName
        sys.exit(-1)

    try:
        dType = dataTypeDict[zPlat][0]
        fType = dataTypeDict[zPlat][1]
    except:
        print " ERROR in readOneDataFile ... ", zPlat
        print dataTypeDict
        sys.exit(-1)

    # for the Agilent level-3 data, there are two header rows that look like this:
    # Hybridization REF       TCGA-13-0888-01A-01R-0406-07
    # Composite Element REF   log2 lowess normalized (cy5/cy3) collapsed by
    # gene symbol

    # for the Affy U133A data, there are also two header rows that look like this:
    # Hybridization REF       5500024056197041909864.A11
    # Composite Element REF   Signal

    # for the Illumina HumanMethylation27 data, there are also two header rows, but
    # a few more columns:
    # Hybridization REF       TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05    TCGA-04-1655-01A-01D-0563-05
    # Composite Element REF   Beta_Value      Gene_Symbol     Chromosome
    # Genomic_Coordinate

    # for the IlluminaGA RNASeq data, there is one header row and a total of 4 columns:
    # gene	raw_counts	median_length_normalized	RPKM

    # for the Genome Wide SNP 6 chip, the level-3 data consists of segments, with a
    # single header row like this:
    # ID                                                  chrom       loc.start         loc.end num.mark   seg.mean
    # SONGS_p_TCGAb36_SNP_N_GenomeWideSNP_6_G04_585364        1       150822330       150853218       35      1.594
    # the big difference in this case is that each sample will have it's own segmentation
    # which we will need to store for later re-segmentation ...

    if (len(geneList) == 0):
        makeGeneList = 1
        print " --> making gene list ", zPlat
    else:
        makeGeneList = 0

    # this is a bit of a hack to handle the unique per-tumor segmentations ...
    if (zPlat == "Genome_Wide_SNP_6"):
        makeGeneList = 1
        geneList = []

    dataVec = []

    # for each tumor, under the cgcc directory, there is data from different
    # centers:
    # bcgsc.ca
    # miRNA data ... ONE header row
    # mRNAseq data ... ONE header row
    # broad.mit.edu
    # SNP chip data ... segmented ... ONE header row
    # jhu-usc.edu
    # methylation data ... TWO header rows
    # 27K data has 5 columns : REF / beta / gene / chr / pos
    # 450K data has only 3   : REF / beta / p-value
    # unc.edu
    # microarray gene expression data ... TWO header rows
    # Agilent data has 2 columns : gene / log2(exp)
    # mRNAseq gene expression data ... ONE header row
    # gene quantification data has 4 columns : gene / counts / length_norm /
    # RPKM

    aLine = fh.readline()

    # for those files with an additional header row, read one more line ...
    # platformList = [ "HT_HG-U133A", "AgilentG4502A_07_1", "AgilentG4502A_07_2", "AgilentG4502A_07_3",
    ##		        "H-miRNA_8x15K", "HumanMethylation27", "IlluminaGA_RNASeq",
    # "Genome_Wide_SNP_6", "IlluminaGA_miRNASeq", "HumanMethylation450" ]

    if (zPlat == "AgilentG4502A_07_1" or zPlat == "AgilentG4502A_07_2" or zPlat == "AgilentG4502A_07_3" or
        zPlat == "HumanMethylation27" or zPlat == "HumanMethylation450" or zPlat == "HT_HG-U133A" or
            zPlat == "H-miRNA_8x15K" or zPlat == "MDA_RPPA_Core"):
        bLine = fh.readline()
    elif (zPlat == "IlluminaGA_miRNASeq" or zPlat == "IlluminaHiSeq_miRNASeq" or
          zPlat == "Genome_Wide_SNP_6" or
          zPlat == "IlluminaGA_RNASeq" or zPlat == "IlluminaGA_RNASeqV2" or
          zPlat == "IlluminaHiSeq_RNASeq" or zPlat == "IlluminaHiSeq_RNASeqV2" or
          zPlat == "microsat_i"):
        doNothing = 1
    else:
        print " need to double check what to do with this platform <%s> " % zPlat
        sys.exit(-1)

    done = 0
    iGene = 0
    while not done:

        cLine = fh.readline()
        cLine = cLine.strip()
        cTokens = cLine.split('\t')
        if (len(cLine) < 3):
            done = 1
            continue

        # the microsat_i data is a special case that we're hacking in here ...
        # there is only one value for each sample ...
        if (zPlat == "microsat_i"):
            featName = "C:SAMP:" + cTokens[1] + ":::::"
            geneList = [featName]
            dataVec = [cTokens[2]]
            done = 1
            return (geneList, dataVec)

        # if we are supposed to create a gene list then do so ...
        if (makeGeneList):

            # for the methylation data, we want to use the gene symbol but we need to also
            # make a unique identifier using the chr and genomic coordinate and
            # CpG id
            if (zPlat == "HumanMethylation27_OBSOLETE_CODE"):
                aCG = cTokens[0]
                geneName = cTokens[2]
                if (geneName.startswith("DISCONT")):
                    geneName = ""
                elif (geneName == "1-Mar"):
                    geneName = "MARCH1"
                elif (geneName == "2-Apr"):
                    geneName = "C17orf88"
                aChr = unifychr(cTokens[3])
                iPos = int(cTokens[4])
                # print " (a) ", geneName, aChr, iPos, aCG
                featureName = makeFeatureName(
                    "N", "METH", geneName, aChr, iPos, -1, '', aCG)
                geneList += [featureName]

            # for the new 450k methylation data ...
            elif (zPlat == "HumanMethylation27" or zPlat == "HumanMethylation450"):
                # print cTokens
                aCG = cTokens[0]
                try:
                    # print metaData[aCG]
                    ## metaData[probeID] = ( probeID, geneName, chrName, chrPos, chrStrand, lastToken )
                    geneName = metaData[aCG][1]
                    aChr = unifychr(metaData[aCG][2])
                    iPos = int(metaData[aCG][3])
                    lastToken = metaData[aCG][5]
                    featureName = makeFeatureName(
                        "N", "METH", geneName, aChr, iPos, -1, '', lastToken)
                    geneList += [featureName]
                    print featureName, len(geneList)
                except:
                    # print " (x) this probe is not on the 27K platform ",
                    # cTokens
                    continue

            # for the RNASeq data, the gene name unfortunately looks like this: "BRCA1|672"
            # and sometimes "?|100130426"
            # and sometimes "5s_rRNA|?|100of139_calculated"
            # --> at first I was just using the first part of the name if it was not "?"
            # but it turns out that there is one case where that first part is not unique
            # SLC35E2|728661 and SLC35E2|9906, so I will instead concatenate the two
            # parts of the name
            # --> new as of 7/18/12: the gene symbol is used in the feature name, and the
            # numeric id is added on as the 'extra' information at the end of
            # the feature name
            elif (zPlat == "IlluminaGA_RNASeq" or zPlat == "IlluminaGA_RNASeqV2" or
                  zPlat == "IlluminaHiSeq_RNASeq" or zPlat == "IlluminaHiSeq_RNASeqV2"):
                if (cTokens[0].endswith("_calculated")):
                    cTokens[0] = cTokens[0][:-11]

                # split up the 'gene' name by the delimiter '|'
                tmpTokens = cTokens[0].split('|')
                if (tmpTokens[0] != "?"):
                    # if the first part of the gene name is NOT '?' then use both parts of
                    # the name in building the feature name ...
                    # also, the BCGSC gene names can look like this:
                    # AMY1A|276|1of3_calculated
                    geneName = tmpTokens[0]
                    if (len(tmpTokens) == 1):
                        xName = ''
                    elif (len(tmpTokens) == 2):
                        xName = tmpTokens[1]
                    elif (len(tmpTokens) == 3):
                        if (tmpTokens[1] != "?"):
                            xName = tmpTokens[1] + "," + tmpTokens[2]
                        else:
                            xName = tmpTokens[2]
                    else:
                        print " FATAL ERROR ??? !!! ", tmpTokens
                        print cTokens
                        sys.exit(-1)

                else:
                    if (len(tmpTokens) == 1):
                        print " FATAL ERROR ??? !!! ", tmpTokens
                        print cTokens
                        sys.exit(-1)
                    elif (len(tmpTokens) == 2):
                        geneName = tmpTokens[1]
                        xName = tmpTokens[1]
                    elif (len(tmpTokens) == 3):
                        geneName = tmpTokens[1]
                        if (tmpTokens[1] != "?"):
                            xName = tmpTokens[1] + "," + tmpTokens[2]
                        else:
                            xName = tmpTokens[2]
                    else:
                        print " FATAL ERROR ??? !!! ", tmpTokens
                        print cTokens
                        sys.exit(-1)

                # print " (b) "
                featureName = makeFeatureName(
                    dType, fType, geneName, '', -1, -1, '', xName)
                geneList += [featureName]

            # for the GWS6 chip data, we don't have "genes" but segments, which we will
            # assemble using the chrom/start/end information from the file
            elif (zPlat == "Genome_Wide_SNP_6"):
                aChr = unifychr(cTokens[1])
                iStart = int(cTokens[2])
                try:
                    iStop = int(cTokens[3])
                except:
                    try:
                        iStop = int(float(cTokens[3]))
                    except:
                        print " FATAL ERROR: failed to parse segment stop position from <%s> " % cTokens[3]
                        sys.exit(-1)
                # print " (c) "
                segName = makeFeatureName(
                    dType, fType, "", aChr, iStart, iStop)
                geneList += [segName]

            # for the RPPA data we need to map the "composite element REF" to a proper
            # gene name ...
            elif (zPlat == "MDA_RPPA_Core"):
                print cTokens
                geneName = cTokens[0]
                featureName = makeFeatureName("N", "RPPA", geneName)
                geneList += [featureName]

            # otherwise these are gene expression data files, and we assume that
            # the first token is the gene name ...
            else:
                print " maybe should check platform name explicitly here ??? ", zPlat, dType, fType, cTokens
                # sys.exit(-1)
                # print " (d) "
                featureName = makeFeatureName(dType, fType, cTokens[0])
                geneList += [featureName]

        # otherwise, make sure that the gene names still match what we already
        # had ...
        else:

            if (zPlat == "HumanMethylation27_OBSOLETE_CODE"):
                try:
                    aCG = cTokens[0]
                    geneName = cTokens[2]
                    if (geneName.startswith("DISCONT")):
                        geneName = ""
                    elif (geneName == "1-Mar"):
                        geneName = "MARCH1"
                    elif (geneName == "2-Apr"):
                        geneName = "C17orf88"
                    aChr = unifychr(cTokens[3])
                    iPos = int(cTokens[4])
                    # print " (e) ", dType, fType, geneName, aChr, iPos, aCG
                    tmpName = makeFeatureName(
                        dType, fType, geneName, aChr, iPos, -1, '', aCG)
                except:
                    print " (a) this should not happen should it ??? "
                    print cLine
                    print cTokens
                    sys.exit(-1)

            elif (zPlat == "HumanMethylation27" or zPlat == "HumanMethylation450"):
                try:
                    aCG = cTokens[0]
                    try:
                        geneName = metaData[aCG][1]
                        aChr = unifychr(metaData[aCG][2])
                        iPos = int(metaData[aCG][3])
                        lastToken = metaData[aCG][5]
                        tmpName = makeFeatureName(
                            dType, fType, geneName, aChr, iPos, -1, '', lastToken)
                    except:
                        # print " (y) this probe is not on the 27K platform "
                        continue
                except:
                    continue

            elif (zPlat == "IlluminaGA_RNASeq" or zPlat == "IlluminaGA_RNASeqV2" or
                  zPlat == "IlluminaHiSeq_RNASeq" or zPlat == "IlluminaHiSeq_RNASeqV2"):

                if (cTokens[0].endswith("_calculated")):
                    cTokens[0] = cTokens[0][:-11]

                tmpTokens = cTokens[0].split('|')
                if (tmpTokens[0] != "?"):
                    geneName = tmpTokens[0]
                    if (len(tmpTokens) == 1):
                        xName = ''
                    elif (len(tmpTokens) == 2):
                        xName = tmpTokens[1]
                    elif (len(tmpTokens) == 3):
                        if (tmpTokens[1] != "?"):
                            xName = tmpTokens[1] + "," + tmpTokens[2]
                        else:
                            xName = tmpTokens[2]
                    else:
                        print " FATAL ERROR ???? !!!! ", tmpTokens, cTokens
                        sys.exit(-1)

                else:
                    if (len(tmpTokens) == 1):
                        print " FATAL ERROR ???? !!!! ", tmpTokens, cTokens
                        sys.exit(-1)
                    elif (len(tmpTokens) == 2):
                        geneName = tmpTokens[1]
                        xName = tmpTokens[1]
                    elif (len(tmpTokens) == 3):
                        geneName = tmpTokens[1]
                        if (tmpTokens[1] != "?"):
                            xName = tmpTokens[1] + "," + tmpTokens[2]
                        else:
                            xName = tmpTokens[2]
                    else:
                        print " FATAL ERROR ????? !!!!! ", tmpTokens, cTokens
                        sys.exit(-1)

                # print " (f) "
                tmpName = makeFeatureName(
                    dType, fType, geneName, '', -1, -1, '', xName)

            elif (zPlat == "MDA_RPPA_Core"):
                print cTokens
                geneName = cTokens[0]
                tmpName = makeFeatureName("N", "RPPA", geneName)

            else:
                # print " (g) "
                tmpName = makeFeatureName(dType, fType, cTokens[0])

            if (geneList[iGene] != tmpName):
                print " ERROR ??? feature name not as expected ??? <%s> <%s> <%s> " % (geneList[iGene], tmpName, cTokens[0])
                sys.exit(-1)

        try:
            # for most platforms, the data value we are interested in is in
            # the last column, but sometimes not ... best to make this decision
            # for each platform carefully

            # IlluminaGA_miRNASeq    --> [-2]
            # IlluminaHiSeq_miRNASeq --> [-2]
            # IlluminaGA_RNASeq      --> [-1]
            # IlluminaHiSeq_RNASeq   --> [-1]
            # IlluminaHiSeq_RNASeqV2 --> [-1]
            # Genome_Wide_SNP_6      --> [-1]
            # HT_HG-U133A            --> [-1]
            # MDA_RPPA_Core          --> [-1]
            # AgilentG4502A_07_1     --> [-1]
            # AgilentG4502A_07_2     --> [-1]
            # AgilentG4502A_07_3     --> [-1]
            # H-miRNA_8x15K          --> [-1]
            # HumanMethylation27     --> [1]
            # HumanMethylation450    --> [1]

            if (zPlat == "IlluminaGA_RNASeq" or zPlat == "IlluminaGA_RNASeqV2" or
                zPlat == "IlluminaHiSeq_RNASeq" or zPlat == "IlluminaHiSeq_RNASeqV2" or
                zPlat == "Genome_Wide_SNP_6" or zPlat == "HT_HG-U133A" or
                zPlat == "MDA_RPPA_Core" or zPlat == "H-miRNA_8x15K" or
                    zPlat == "AgilentG4502A_07_1" or zPlat == "AgilentG4502A_07_2" or zPlat == "AgilentG4502A_07_3"):
                dataVec += [float(cTokens[-1])]

            elif (zPlat == "IlluminaGA_miRNASeq" or zPlat == "IlluminaHiSeq_miRNASeq"):
                dataVec += [float(cTokens[-2])]

            elif (zPlat == "HumanMethylation27" or zPlat == "HumanMethylation450"):
                dataVec += [float(cTokens[1])]

            else:
                print " double check platform data location ??? "
                print zPlat, cTokens
                sys.exit(-1)
                dataVec += [float(cTokens[1])]

        except:
            if (len(cTokens) == 1):
                dataVec += [NA_VALUE]
            elif (cTokens[1] == 'null'):
                dataVec += [NA_VALUE]
            elif (cTokens[1] == 'NA'):
                dataVec += [NA_VALUE]
            else:
                print ' ERROR converting token to float ??? ', zPlat
                print cLine
                print cTokens, len(cTokens)
                sys.exit(-1)

        iGene += 1

    # print dataVec[:10]

    print " --> returning ", len(geneList), len(dataVec)
    print geneList[:5]
    print dataVec[:5]

    return (geneList, dataVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def mergeSegments(segList, dataVec):

    print " in mergeSegments ... ", len(segList), len(dataVec)
    print "     THIS HAS NOT BEEN IMPLEMENTED !!! "
    sys.exit(-1)

    return (segList, dataVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtSegs(segMatrix):

    maxNumSeg = len(segMatrix)
    numSamples = len(segMatrix[0])
    twnSeg = []
    segLen = []

    numChr = 24
    for iChr in range(numChr):
        # FIXME !!!
        pref = '%d_' % (iChr + 1)
        for jS in range(numSamples):
            lastSegEnd = -1
            for iS in range(maxNumSeg):
                if (segMatrix[iS][jS] == ''):
                    continue
                if (not segMatrix[iS][jS].startswith(pref)):
                    continue
                tokenList = segMatrix[iS][jS].split(':')
                segStart = int(tokenList[3])
                segEnd = int(tokenList[4])
                segLength = (segEnd - segStart + 1)
                segLen += [segLength]
                if (lastSegEnd >= 0):
                    delLength = (segStart - lastSegEnd)
                    twnSeg += [delLength]
                lastSegEnd = segEnd

    segLen.sort()
    twnSeg.sort()

    nSegLen = len(segLen)
    nTwnSeg = len(twnSeg)

    print " "
    print nSegLen, segLen[:10], segLen[-10:]
    print nTwnSeg, twnSeg[:10], twnSeg[-10:]
    print " "
    print segLen[nSegLen / 10], segLen[nSegLen / 4], segLen[nSegLen / 2], segLen[3 * nSegLen / 4], segLen[9 * nSegLen / 10]
    print twnSeg[nTwnSeg / 10], twnSeg[nTwnSeg / 4], twnSeg[nTwnSeg / 2], twnSeg[3 * nTwnSeg / 4], twnSeg[9 * nTwnSeg / 10]

    # based on a quick look at COAD data, the median segment length is 145kb,
    # (max = 151Mb), and the median between-segments gap is 1500bp (max = 20Mb)

    # 10th %ile of segment lengths is 472bp, 90th %ile is 13Mb
    # 10th %ile of segment gaps    is  78bp, 90th %ile is  8Kb

    print " "
    print " "
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def prettyPrint(aVec, skipFlag=1):

    if (len(aVec) < 1):
        print " WARNING: in prettyPrint ... empty vector ... "
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


def prettyPrint2(aDict):

    startKeys = aDict.keys()
    startKeys.sort()
    # print startKeys

    print " number of start keys : ", len(startKeys), startKeys[:3], startKeys[-3:]
    for iStart in startKeys:
        stopKeys = aDict[iStart].keys()
        if (len(stopKeys) != 1):
            print " ERROR ??? in prettyPrint2 ... how can there by multiple stop keys ??? "
            print aDict
            sys.exit(-1)
        iStop = stopKeys[0]
        try:
            print " [ (%d,%d) : %.3f ]   " % (int(iStart), int(iStop), aDict[iStart][iStop])
        except:
            print " ERROR in prettyPrint2 ??? "
            print " startKeys : ", startKeys
            print " contents for current startKey : ", iStart, aDict[iStart]
            print " stopKeys : ", stopKeys
            print " number of stopKeys : ", len(aDict[iStart])
            sys.exit(-1)

    # sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this used to be done with a single numpy.subtract call but now we need
# to handle the NA_VALUEs ...
##	 diffvec[k] = cnvsum[k+1] - cnvsum[k]
##	 diffvec = numpy.subtract ( cnvsum[1::1], cnvsum[0:-1:1] )


def computeFirstDiffVec(cnvsum):

    diffvec = numpy.zeros(len(cnvsum) - 1)

    minDiff = 999999.
    maxDiff = -999999.
    for kk in range(len(diffvec)):

        # if either of the two values to be differenced are NA, then
        # we set the diffvec value to NA
        if (cnvsum[kk] == NA_VALUE):
            diffvec[kk] = NA_VALUE
        elif (cnvsum[kk] == abs(NA_VALUE)):
            diffvec[kk] = NA_VALUE
        elif (cnvsum[kk + 1] == NA_VALUE):
            diffvec[kk] = NA_VALUE
        elif (cnvsum[kk + 1] == abs(NA_VALUE)):
            diffvec[kk] = NA_VALUE

        # only if we have two valid values do we compute the difference
        else:
            diffvec[kk] = cnvsum[kk + 1] - cnvsum[kk]
            if (minDiff > diffvec[kk]):
                minDiff = diffvec[kk]
            if (maxDiff < diffvec[kk]):
                maxDiff = diffvec[kk]

    # sanity check ...
    if (0):
        if (maxDiff > 1000):
            print " ERROR ??? how did we get this value ??? "
            print " "
            for ii in range(len(diffvec)):
                print ii, cnvsum[ii + 1], cnvsum[ii], diffvec[ii]
            sys.exit(-1)

    # print " done computing diffvec "
    return (diffvec, minDiff, maxDiff)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeZerosNAs(diffvec):

    # print " "
    # print " in removeZerosNAs ... "
    # print diffvec[:10]
    # print diffvec[-10:]
    # print " "

    n1 = len(diffvec)
    if (n1 < 1):
        print " in removeZerosNAs ... zero length vector ??? "
        sys.exit(-1)

    # print n1, min(diffvec), max(diffvec)
    n0 = 0
    for kk in range(n1):
        if (abs(diffvec[kk]) < 0.0001):
            n0 += 1
        elif (abs(diffvec[kk]) > (abs(NA_VALUE) - 1)):
            n0 += 1
        else:
            doNothing = 1
        # print kk, diffvec[kk], abs(diffvec[kk]), n0

    # print " "
    # print " "

    n2 = n1 - n0
    # print " starting with %d values, removing %d values, left with %d values
    # " % ( n1, n0, n2 )
    if (n2 < 10):
        print " ERROR ??? "
        print " in removeZerosNAs ... ", len(diffvec), n1, n0, n2
        prettyPrint(diffvec)
        sys.exit(-1)

    diffvec_nz = numpy.zeros(n2)

    nn = 0
    for kk in range(n1):
        if (abs(diffvec[kk]) < 0.0001):
            doNothing = 1
        elif (abs(diffvec[kk]) > (abs(NA_VALUE) - 1)):
            doNothing = 1
        else:
            diffvec_nz[nn] = diffvec[kk]
            nn += 1

    # print " returning diffvec_nz ... ", len(diffvec_nz), nn,
    # min(diffvec_nz), max(diffvec_nz)
    return (diffvec_nz)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def initializeVec(veclen, value=NA_VALUE):

    aVec = numpy.zeros((veclen, 1))
    for kk in range(veclen):
        aVec[kk] = value

    return (aVec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# accumulate the current binned vector into the summed vector ...
# 25may12: changing this to operate on absolute values so that large positive
# values and large negative values don't cancel each other out!!!


def add2CNVsum(cnvsum, cnvvec):

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


def getLocalMean(tv):

    # we only want to sum values that are not NA
    b1 = (tv != NA_VALUE)
    num = numpy.sum(b1)
    if (num > 0):
        sum1 = numpy.sum(tv[b1])
        mu = sum1 / float(num)
        return (mu, num)
    else:
        return (NA_VALUE, num)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this is now the most time-intensive function call according to profile ...


def copyInto(cnvvec, start, stopPlus1, value):

    # if the input value is NA, nothing to do ...
    if (value == NA_VALUE):
        return (cnvvec)

    if (stopPlus1 == len(cnvvec)):
        stopPlus1 -= 1
    if (start >= stopPlus1):
        return (cnvvec)

    if (start < 0):
        print " ERROR in copyInto ??? ", len(cnvvec), start, stopPlus1, value
        sys.exit(-1)
        start = 0
    if (start >= len(cnvvec)):
        print " ERROR in copyInto ??? ", len(cnvvec), start, stopPlus1, value
        sys.exit(-1)
        start = len(cnvvec) - 1
    if (stopPlus1 < 1):
        print " ERROR in copyInto ??? ", len(cnvvec), start, stopPlus1, value
        sys.exit(-1)
        stopPlus1 = 1
    if (stopPlus1 >= len(cnvvec)):
        print " ERROR in copyInto ??? ", len(cnvvec), start, stopPlus1, value
        sys.exit(-1)
        stopPlus1 = len(cnvvec)

    if (start >= stopPlus1):
        print " ERROR in copyInto ??? ", len(cnvvec), start, stopPlus1, value
        sys.exit(-1)

    # any values that are NA in cnvvec should just be set to
    # whatever the new value is, so we need a boolean representation
    # of this fact:
    b1 = (cnvvec == NA_VALUE)

    # and we also need a boolean vector that defines the start/stop range
    b0 = numpy.zeros_like(b1)
    b0[start:stopPlus1] = True

    # set any values that are in the start/stop range and NA to 'value'
    cnvvec[b0 & b1] = value

    # and now set values that are smaller (absolute value sense) than value
    b2 = (abs(cnvvec) < abs(value))
    cnvvec[b0 & b2] = value

    if (debugON):
        numSet = 0
        for ii in range(len(cnvvec)):
            if (abs(cnvvec[ii] - value) < 0.001):
                numSet += 1
        print " number of values set to %f : %d " % (value, numSet)

    return (cnvvec)

    # OLD slower code: (which was about 6 times slower)

    for kk in range(start, stopPlus1):
        if (cnvvec[kk] == NA_VALUE):
            cnvvec[kk] = value
        elif (abs(cnvvec[kk]) < abs(value)):
            cnvvec[kk] = value

    return (cnvvec)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this is Timo's resegmentation code (mostly)


def resegmentCNdata(sampleList, segMatrix, dataMatrix,
                    steplength=1000, cutFrac=0.01):

    # when we get to this point, we have:
    # sampleList: list of sample barcodes, eg TCGA-74-6575-01A-11D-1842-01
    # segMatrix:  matrix, eg 25000 x 538
    # dataMatrix: matrix, eg 25000 x 538
    # steplength: bin size, eg 1000 bp
    # cutFrac:    fraction to keep, eg 0.01

    # segMatrix[i][j] contains the ith segment label for the jth patient
    # for example: N:CNVR::chr5:32994916:36107278::

    # dataMatrix[i][j] contains the log2(CN/2) copy-number value for the
    # ith segment for the jth patient, eg: -0.447

    print " "
    print " STARTING resegmentCNdata ... ", len(sampleList), steplength, cutFrac

    if (debugON):
        print sampleList[:5], sampleList[-5:]
        print len(segMatrix), len(dataMatrix)
        print len(segMatrix[0]), len(dataMatrix[0])
        print " "
        print segMatrix[0][0], segMatrix[0][-1]
        print segMatrix[1][0], segMatrix[1][-1]
        print segMatrix[200][0], segMatrix[200][-1]
        print segMatrix[201][0], segMatrix[201][-1]
        print segMatrix[2000][0], segMatrix[2000][-1]
        print segMatrix[2001][0], segMatrix[2001][-1]
        print " "
        print dataMatrix[0][0], dataMatrix[0][-1]
        print dataMatrix[1][0], dataMatrix[1][-1]
        print dataMatrix[200][0], dataMatrix[200][-1]
        print dataMatrix[201][0], dataMatrix[201][-1]
        print dataMatrix[2000][0], dataMatrix[2000][-1]
        print dataMatrix[2001][0], dataMatrix[2001][-1]

    maxNumSeg = len(segMatrix)
    numSamples = len(segMatrix[0])

    barcodeList = [0] * numSamples
    for jS in range(numSamples):
        barcodeList[jS] = sampleList[jS]
    barcodeList.sort()

    # the output matrix will initially be samples x segments but will
    # then be flipped just before returning from this function ...
    newMatrix = [0] * numSamples
    for jS in range(numSamples):
        newMatrix[jS] = []
    segList = []

    if (0):
        # FIXME: the function 'lookAtSegs' now out of date and needs to be fixed
        # if I want to use it again ...
        lookAtSegs(segMatrix)

    numChr = 24
    breakpoints_total = 0

    # outermost loop is over chromosomes:
    # TEMP HACK
    # for iChr in [6]:
    # for iChr in range(21,numChr):
    for iChr in range(numChr):

        chr = unifychr(str(iChr + 1))
        pref = "N:CNVR::chr" + chr + ":"

        print " "
        print " *************************************************************** "
        print " OUTER LOOP : ", chr, pref, numSamples, maxNumSeg

        # in this loop, we grab only those segments from the input segMatrix/dataMatrix
        # that pertain to the current chromosome, and we put ths information into a
        # new temporary 'data' dictionary so that we have:
        ##	data[barcode]['CNVorig'][chr][start][stop] = dataMatrix[iS][jS]
        # where	barcode = sampleList[jS]
        # and	(chr,start,stop) are extracted from segMatrix[iS][jS]

        data = AutoVivification()
        for jS in range(numSamples):

            barcode = sampleList[jS]
            # print jS, barcode

            for iS in range(maxNumSeg):

                if (segMatrix[iS][jS] == ''):
                    continue
                if (not segMatrix[iS][jS].startswith(pref)):
                    continue

                tokenList = segMatrix[iS][jS].split(':')
                start = int(tokenList[4])
                stop = int(tokenList[5])
                # print start, stop, tokenList
                try:
                    value = float(dataMatrix[iS][jS])
                except:
                    print " error in accessing dataMatrix ???  segment %d (%d)  sample %d (%d) " % (iS, maxNumSeg, jS, numSamples)
                    print len(dataMatrix), len(dataMatrix[0])
                    print len(segMatrix), len(segMatrix[0])
                    print segMatrix[iS][jS]
                    sys.exit(-1)

                data[barcode]['CNVorig'][chr][start][stop] = value
        # end of loop over numSamples

        # so at this point, we have 'data' that looks like this, for example:
        # {'TCGA-06-0189-01A-01D-0236-01': {'CNVorig': {'1': {25534592: {65646460: 0.0325}, 72532097: {72543731: 0.855}, ...
        # barcode                  'CNVRorig'  chr     start       stop
        # value,   start      stop     value, ...

        # NOTE that building this deeply nested dictionary is probably an
        # unnecessarily inefficient approach to this ...

        # now that we have all the data for this chromosome, re-segment it

        # first, figure out how long of a vector we're going to need given the highest genomic
        # coordinate referenced by a segment and the specified 'steplength'
        # (this requres a loop over all of the samples)
        maxchrcoord = 0
        for jS in range(numSamples):
            barcode = barcodeList[jS]
            startKeys = data[barcode]['CNVorig'][chr].keys()
            startKeys.sort()
            for start in startKeys:
                for stop in data[barcode]['CNVorig'][chr][start].keys():
                    stopcoord = int(int(stop) / steplength)  # floor
                    maxchrcoord = max(maxchrcoord, stopcoord)

        maxchrcoord += 1
        print ' maxchrcoord : ', maxchrcoord
        # and then allocate a vector of that length, initialized to NA_VALUE
        # this vector will contain the sum, across all segments, of the binned
        # CN values
        cnvsum = initializeVec(maxchrcoord, abs(NA_VALUE))

        print " --> B0 looping over %d barcodes ... " % numSamples

        # now we loop again over all of the samples (jS: 0 to numSamples-1)
        # and for each sample, loop over all of the segments, sorted by start
        # position

        for jS in range(numSamples):
            barcode = barcodeList[jS]

            # print " B ", barcode, " allocating vector of zeros of length ",
            # maxchrcoord
            cnvvec = initializeVec(maxchrcoord, NA_VALUE)

            # if we have no segments, there is nothing to be done ...
            if (len(startKeys) == 0):
                continue

            # print " C      --> looping over %d start keys ... " % (
            # len(startKeys) )
            startKeys = data[barcode]['CNVorig'][chr].keys()
            startKeys.sort()
            for start in startKeys:
                startcoord = int(int(start) / steplength)  # floor
                if (len(data[barcode]['CNVorig'][chr][start].keys()) != 1):
                    print " D              how can there be more than one stop key ??? "
                    print barcode
                    print start
                    print data[barcode]['CNVorig'][chr][start].keys()
                    sys.exit(-1)
                for stop in data[barcode]['CNVorig'][chr][start].keys():
                    stopcoord = int(int(stop) / steplength)  # floor
                    # using a "smarter" copy here so that 'extreme' values are not over-written
                    # by segments that overlap within a single bin ...
                    # print " "
                    # print " calling copyInto ... ", startcoord, stopcoord+1,
                    # data[barcode]['CNVorig'][chr][start][stop]
                    cnvvec = copyInto(
                        cnvvec, startcoord, (stopcoord + 1), data[barcode]['CNVorig'][chr][start][stop])

            data[barcode]['CNVtemp'][chr] = cnvvec.copy()
            cnvsum = add2CNVsum(cnvsum, cnvvec)
            # print min(cnvvec), max(cnvvec), min(cnvsum), max(cnvsum)

        # end of loop over barcodes ...
        # print " "
        # print " *********************************** "
        # print " "
        if (debugON):
            print ' '
            print ' cnvsum : ', len(cnvsum), min(cnvsum), max(cnvsum)
            prettyPrint(cnvsum)

        # compute the first difference (slope) vector:
        (diffvec, minDiff, maxDiff) = computeFirstDiffVec(cnvsum)
        if (len(diffvec) == 0):
            print " WARNING: zero length diffvec "
            continue

        # sanity check on value range ...
        if (max(abs(minDiff), abs(maxDiff)) > numSamples):
            print " "
            print " ************************************ "
            print " WARNING !!! extreme values found ??? "
            print "     numSamples = %6d " % numSamples
            print "     difference vector range : %.1f to %.1f " % (minDiff, maxDiff)
            print " ************************************ "
            print " "

        if (debugON):
            print ' '
            print ' diffvec : ', len(diffvec), min(diffvec), max(diffvec)
            prettyPrint(diffvec)

        # NEW: taking the absolute value here ...
        diffvec = abs(diffvec)
        if (debugON):
            print ' '
            print ' diffvec : ', len(diffvec), min(diffvec), max(diffvec)
            prettyPrint(diffvec)

        # remove the zeros and the NAs ...
        diffvec_nz = removeZerosNAs(diffvec)
        if (debugON):
            print ' '
            print ' diffvec_nz : ', len(diffvec_nz), min(diffvec_nz), max(diffvec_nz)
            prettyPrint(diffvec_nz)

        min(diffvec_nz)
        max(diffvec_nz)

        diffvec_nz = numpy.sort(diffvec_nz, axis=0)
        if (debugON):
            print ' '
            print ' diffvec_nz : ', len(diffvec_nz), min(diffvec_nz), max(diffvec_nz)
            prettyPrint(diffvec_nz)

        # get the number of rows in diffvec and in diffvec_nz (the first is just the number of
        # bins for this chromosome, and the second is the # of bins with
        # non-zero slope)
        ndiff = diffvec.shape[0]
        # print ndiff, len(diffvec)
        ndiff_nz = diffvec_nz.shape[0]
        # print ndiff_nz, len(diffvec_nz)

        # determine the cutoff beyond which we will create segment boundaries
        # ( hmmmm ... note that this cutoff is being chosen separately for each chromosome )
        cutoff_hi = diffvec_nz[int((1 - cutFrac - cutFrac) * ndiff_nz)]
        print " F2 cutoff : ", cutoff_hi, ndiff, ndiff_nz, int(2 * cutFrac * ndiff_nz)

        breakpoints_per_chr = 0
        lastcoord = -1

        # print " "
        # print " F3 --> now looping over %d difference bins ... " % ndiff

        # NOTE: when there is a significant difference at the kth bin in diffvec, that means that
        # there was a big jump between the kth and the (k+1)th bin in the original binning
        # of the chromosome

        # print " looping over diffvec ... ", ndiff

        # start at 0
        diffcoord = 0
        lastDiff = abs(NA_VALUE)
        makeBreakPoint = 0

        while (diffcoord < ndiff):

            diff = diffvec[diffcoord]
            # print " diffcoord=%6d    diff=%.1f  (%.1f) " % ( diffcoord, diff,
            # lastDiff )

            # if the current diff is NA, but the previous was not, then force a
            # break-point
            if (diff == abs(NA_VALUE)):
                if (lastDiff < abs(NA_VALUE)):
                    makeBreakPoint = 1

            # OR if the current diff exceeds the threshold, then force a
            # break-point
            elif (abs(diff) >= cutoff_hi):
                makeBreakPoint = 1

            # OR if we have reached the end of this chromosome
            elif (diffcoord == (ndiff - 1)):
                makeBreakPoint = 1

            lastDiff = diff

            # make a break-point now ...
            if (makeBreakPoint):
                makeBreakPoint = 0

                breakpoints_per_chr += 1
                breakpoints_total += 1

                startcoord = lastcoord + 1
                stopcoord = diffcoord
                lastcoord = diffcoord

                startpos = startcoord * steplength
                stoppos = stopcoord * steplength + steplength
                if (diffcoord < (ndiff - 1)):
                    stoppos -= 1

                # print " F4  diffcoord=%2d  startcoord=%2d  stopcoord=%2d  startpos=%8d stoppos=%8d " % ( diffcoord, startcoord, stopcoord, startpos, stoppos )
                # print "             difference is significant", diff,
                # startcoord, stopcoord, startpos, stoppos

                # print " F5  looping over barcodes ... ", barcodeList[:5], "
                # ... ", barcodeList[-5:]

                for jS in range(numSamples):
                    barcode = barcodeList[jS]
                    if ('CNVtemp' in data[barcode].keys()):
                        # print " getLocalMean ... ", barcode, chr, startcoord, stopcoord+1
                        # print
                        # data[barcode]['CNVtemp'][chr][startcoord:(stopcoord+1)]
                        (mu, numMu) = getLocalMean(
                            data[barcode]['CNVtemp'][chr][startcoord:(stopcoord + 1)])
                        # print " --> mu=%f  numMu=%d " % ( mu, numMu )
                        data[barcode]['CNV'][chr][startpos][stoppos] = mu

                        if (jS == 0):
                            segName = makeFeatureName(
                                "N", "CNVR", "", chr, startpos, stoppos)
                            segList += [segName]

                        newMatrix[jS] += [mu]
                    else:
                        print " HOW DID THIS HAPPEN ??? "
                        print barcode
                        print data[barcode].keys()
                        sys.exit(-1)

            # else:
            # print " diffcoord=%2d  startcoord=%2d  stopcoord=%2d
            # startpos=%8d stoppos=%8d " % ( diffcoord, startcoord, stopcoord,
            # startpos, stoppos )

            # if we did not make a break-point but the diff was NA, then reset
            # the lastcoord ...
            if (not makeBreakPoint):
                if (diff == abs(NA_VALUE)):
                    lastcoord = diffcoord

            diffcoord += 1

        # end of loop over diffcoord ...

        # print " H   %d breakpoints in chr %s (total: %d) " % ( breakpoints_per_chr, chr, breakpoints_total )
        # print len(newMatrix), len(newMatrix[0])
        # print len(segList), segList[:10], segList[-10:]

        # print " total number of barcodes : ", numSamples
        # print barcodeList[:4]
        # print barcodeList[-4:]
        # print " "
        # print data[barcodeList[0]].keys()
        # print data[barcodeList[0]]['CNV'].keys(), chr
        # print data[barcodeList[0]]['CNVorig'].keys(), chr
        # print data[barcodeList[0]]['CNVtemp'].keys(), chr
        # print " "
        # print barcodeList[0]
        ## prettyPrint2 ( data[barcodeList[0]]['CNV'][chr] )
        # print barcodeList[1]
        ## prettyPrint2 ( data[barcodeList[1]]['CNV'][chr] )

        # print " "
        # print " "

        # this is the end of processing for a single chromosome ('chr')
        # sys.exit(-1)

    # now we flip the 'newMatrix' and return it as the output 'dataMatrix'
    numSeg = len(newMatrix[0])
    dataMatrix = [0] * numSeg
    # print " looping over %d segments and %d samples ... flipping matrix ...
    # " % ( numSeg, numSamples )
    numNA = 0
    for kS in range(numSeg):
        dataMatrix[kS] = [0] * numSamples
        for jS in range(numSamples):
            dataMatrix[kS][jS] = newMatrix[jS][kS]
            if (abs(dataMatrix[kS][jS]) > abs(NA_VALUE / 2)):
                # print kS, jS, dataMatrix[kS][jS]
                numNA += 1

    print " number of NA samples found while flipping : ", numNA
    print " "
    # print " "
    # print " now we should finally be done "

    # take a look at the barcodes ... tumor only? mix?
    miscTCGA.lookAtBarcodes(barcodeList)

    # print " segList : ", len(segList), segList[:4], segList[-4:]
    sampleList = barcodeList
    # print len(sampleList), sampleList[:4], sampleList[-4:]
    # print len(dataMatrix), len(dataMatrix[0])

    print " RETURNING from resegmentCNdata ... "
    print " "

    return (segList, sampleList, dataMatrix)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getLastBit(aName):

    ii = len(aName) - 1
    while (aName[ii] != '/'):
        ii -= 1

    # print ' <%s>    <%s> ' % ( aName, aName[ii+1:] )

    return (aName[ii + 1:])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def hackBarcode(barcode):

    if (barcode.startswith("TCGA-")):

        # RPPA barcodes are unfortunately ~different~
        # 012345678901234567890123456
        # TCGA-A8-A09E-01A-21-A13A-20
        # TCGA-24-1466-01A-21-1562-20
        # TCGA-24-1416-01A-21A-20.P

        # will probably need to FIX this somehow ...

        if (barcode[19] == '-'):
            tmp = barcode[:19] + 'A' + barcode[19:27]
            return (tmp)

    return (barcode)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getSampleID(sdrfDict, fileName):

    keyList = sdrfDict.keys()
    for aKey in keyList:
        if (sdrfDict[aKey][1] == fileName):
            barcode = aKey
            # need to take this out (21feb13) because we need to keep
            # the barcodes that the DCC reports in the UUID-to-barcode
            # mapping metadata file ...
            #### barcode = hackBarcode ( barcode )
            print "         returning from getSampleID ... <%s> <%s> " % (barcode, sdrfDict[aKey][2])
            return (barcode, sdrfDict[aKey][2])

    print ' '
    print ' how did I get here ??? ', fileName
    print ' looking for something like <%s> ... <%s> ' % (fileName, sdrfDict[keyList[0]][1])
    print ' '
    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getArchiveRevision(dName):

    print ' in getArchiveRevision ... '
    print dName

    i1 = dName.find('mage-tab')
    i2 = i1 + 9
    i3 = dName.find('.', i2)
    i4 = dName.find('.', i3 + 1)
    # print i1, i2, i3, i4
    # print dName[i1:]
    # print dName[i2:i3]
    # print dName[i3+1:i4]

    iArch = int(dName[i2:i3])
    iRev = int(dName[i3 + 1:i4])

    print iArch, iRev

    return (iArch, iRev)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getDataType(aLabel):

    tokenList = aLabel.split(':')
    if (len(tokenList) != 7 and len(tokenList) != 8):
        print " ERROR in getDataType ??? improper label ??? ", aLabel
        print len(tokenList), tokenList
        sys.exit(-1)

    dataType = "%s:%s" % (tokenList[0], tokenList[1])
    return (dataType)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getSDRFilename(topDir):

    print " in getSDRFilename ... "
    # print topDir

    if (os.path.exists(topDir)):
        d1 = path.path(topDir)
        if (not d1.isdir()):
            print ' <%s> is not a directory, skipping ... ' % d1
            return ('NA')
    else:
        print ' <%s> does not exist, skipping ... ' % topDir
        return ('NA')

    # first we need to gather up all of the mage-tab directory names, with the proper
    # archive and revision numbers ... and at the same time, find he highest
    # archive #
    mageTabDict = {}
    maxArch = 0
    mageTabFound = 0
    for dName in d1.dirs():
        if (dName.find("mage-tab") >= 0):
            mageTabFound = 1
            print dName
            (iArch, iRev) = getArchiveRevision(dName)
            mageTabDict[dName] = (iArch, iRev)
            if (iArch > maxArch):
                maxArch = iArch

    if (mageTabFound == 0):
        print " WARNING ... in getSDRFilename ... failed to find mage-tab directory "
        print topDir

    print mageTabDict

    # now we need to get the highest revision number for this archive
    maxRev = -1
    for aKey in mageTabDict.keys():
        if (mageTabDict[aKey][0] == maxArch):
            if (mageTabDict[aKey][1] > maxRev):
                maxRev = mageTabDict[aKey][1]
                zKey = aKey

    if (maxRev < 0):
        print "     --> FAILED to find SDRF file !!! ", topDir
        # return ( "NA" )
        print " FATAL ERROR in getSDRFilename ??? "
        print mageTabDict.keys()
        print mageTabDict
        print maxArch, maxRev
        sys.exit(-1)

    # and now we have the proper mage-tab directory
    print ' have zKey: ',  zKey
    d2 = path.path(zKey)
    for fName in d2.files():
        print ' looking at fName <%s> ' % fName
        if (fName.endswith("sdrf.txt")):
            print '             ', fName
            return (fName)

    return ("NA")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def pickGeneName(geneList):

    if (len(geneList) == 1):
        return (geneList[0])
    elif (len(geneList) == 0):
        return ('')

    tmpDict = {}
    maxCount = 0
    for aName in geneList:
        if aName in tmpDict.keys():
            tmpDict[aName] += 1
        else:
            tmpDict[aName] = 1
        if (tmpDict[aName] > maxCount):
            maxCount = tmpDict[aName]
            pickGene = aName

    return (pickGene)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def loadPlatformMetaData(zString):

    # --------------------------------------------------------------------------#
    if (zString == "jhu-usc.edu/humanmethylation450/methylation/" or
            zString == "jhu-usc.edu/humanmethylation27/methylation/"):

        if (1):
            metaDataFilename = gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES'] + "/tcga_platform_genelists/featNames.15oct13.hg19.txt"
            fh = file(metaDataFilename)
            metaData = {}
            done = 0
            while not done:
                aLine = fh.readline()
                aLine = aLine.strip()
                tokenList = aLine.split(':')
                if (len(tokenList) < 8):
                    done = 1
                    continue

                # feature names can now look like this:
                # N:METH:A2BP1:chr16:6068831:::cg03586879_TSS1500_NShore
                # 0 1    2     3     4         7

                lastToken = tokenList[7]
                lastSplit = lastToken.split('_')
                probeID = lastSplit[0]

                chrName = tokenList[3]
                chrPos = tokenList[4]
                chrStrand = ''
                geneName = tokenList[2]

                metaData[probeID] = (
                    probeID, geneName, chrName, chrPos, chrStrand, lastToken)

            fh.close()

        probeList = metaData.keys()
        probeList.sort()
        print probeList[:10]
        print metaData[probeList[0]]

        return (metaData)

    else:
        print " ERROR in loadPlatformData ??? ", zString
        sys.exit(-1)

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


def openDataFreezeLogFile(tumorType, outSuffix, platformStrings):

    print " in openDataFreezeLogFile ... "
    print " <%s> " % tumorType
    print " <%s> " % outSuffix

    if (len(platformStrings) != 1):
        print " ERROR in openDataFreezeLogFile ... there should only be one platform string "
        print platformStrings
        sys.exit(-1)
    print " <%s> " % platformStrings[0]

    dflFilename = tumorType + "." + outSuffix + "."
    tokenList = platformStrings[0].split('/')
    print len(tokenList), tokenList

    for ii in range(len(tokenList) - 1, 0, -1):
        if (len(tokenList[ii]) > 0):
            dflFilename += tokenList[ii]
            dflFilename += "__"
    dflFilename += tokenList[0]

    dflFilename += ".data_freeze.log"

    print " opening log file at: ", dflFilename
    fh = file(dflFilename, 'w')

    return (fh)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def writeDataFreezeLog(fhLog, fName, barcode):

    # print " "
    # print " in writeDataFreezeLog ... "
    # print " "

    tokenList = fName.split('/')
    # print len(tokenList)
    # print tokenList

    justFile = tokenList[-1]
    justArchive = tokenList[-2]

    # print " barcode           : <%s> " % barcode
    # print " filename stripped : <%s> " % justFile
    # print " archive stripped  : <%s> " % justArchive

    # print " "
    # print " "

    fhLog.write("%s\t%s\t%s\n" % (barcode, justFile, justArchive))

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
    # NEW SPECIAL CASE ... if we are dealing with the new 450K methylation
    # platform, we need to grab the extra information from Illumina
    if (platformID == "jhu-usc.edu/humanmethylation27/methylation/" or
            platformID == "jhu-usc.edu/humanmethylation450/methylation/"):
        metaData = loadPlatformMetaData(platformID)
    else:
        metaData = {}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # in the first pass, we are just going to go through the proper SDRF for each
    # tumor type and figure out which files we need to process ...

    mergeSdrfDict = {}
    mergeArchiveList = []
    mergeFileList = []

    for zCancer in tumorList:
        print ' '
        print ' ********************************** '
        print ' LOOP over %d CANCER TYPES ... %s ' % (len(tumorList), zCancer)
        logFlag = 0

        # piece together the directory name ...
        ## topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/dcc-snapshot/public/tumor/" + zCancer + "/cgcc/" + platformID
        topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/" + \
            snapshotName + "/public/tumor/" + zCancer + "/cgcc/" + platformID

        # HACK: the microsat_instability data is in the "secure" branch ...
        if (platformID.find("microsat_i") > 0):
            topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/" + \
                snapshotName + "/secure/tumor/" + \
                zCancer + "/cgcc/" + platformID

        print " topDir : ", topDir

        # get the correct SDRF filename (highest archive #, highest revision #)
        print " calling getSDRFilename ... "
        sdrfFilename = getSDRFilename(topDir)

        if (sdrfFilename == "NA"):
            zPlat = "NA"
            continue

        # load up the information from the SDRF file ...
        (sdrfDict, archiveList, fileList, zPlat) = getSDRFinfo(sdrfFilename)

        print " BACK from getSDRFinfo ... ", zPlat, len(sdrfDict), len(archiveList), len(fileList)
        print len(fileList)
        print fileList[:3]
        print fileList[-3:]

        numSamples = len(fileList)
        print " --> setting numSamples ... ", numSamples, len(fileList), len(sdrfDict)

        # here we need to merge stuff ...
        if (len(mergeSdrfDict) == 0):
            mergeSdrfDict = sdrfDict
            mergeArchiveList = archiveList
            mergeFileList = fileList

        else:

            # example key and contents of sdrfDict:
            # TCGA-G4-6309-01A-21D-1834-01
            # ('broad.mit.edu_COAD.Genome_Wide_SNP_6.Level_3.138.2001.0',
            # 'BAIZE_p_TCGA_b138_SNP_N_GenomeWideSNP_6_G10_808888.hg19.seg.txt',
            # 'Copy Number Results-SNP')
            aKey = mergeSdrfDict.keys()[0]
            print aKey, mergeSdrfDict[aKey]
            print " "
            for aKey in sdrfDict.keys():
                if (aKey in mergeSdrfDict.keys()):
                    print " (b) this should not happen, right ??? "
                    print aKey
                    sys.exit(-1)
                else:
                    mergeSdrfDict[aKey] = sdrfDict[aKey]

            # example list of archive names ...
            # [ 'broad.mit.edu_COAD.Genome_Wide_SNP_6.Level_3.116.2001.0', 'broad.mit.edu_COAD.Genome_Wide_SNP_6.Level_3.123.2001.0', ... ]
            print len(mergeArchiveList), mergeArchiveList[:3], mergeArchiveList[-3:]
            for aArchive in archiveList:
                if (aArchive in mergeArchiveList):
                    if (aArchive == "unknown"):
                        continue
                    print " (c) this should not happen, right ??? "
                    print aArchive
                    sys.exit(-1)
                else:
                    mergeArchiveList += [aArchive]
            print len(mergeArchiveList), mergeArchiveList[:3], mergeArchiveList[-3:]
            print " "

            # example list of file names ...
            # [ 'BAIZE_p_TCGA_b138_SNP_N_GenomeWideSNP_6_A02_808774.hg19.seg.txt', 'BAIZE_p_TCGA_b138_SNP_N_GenomeWideSNP_6_A03_808754.hg19.seg.txt', ... ]
            print len(mergeFileList), mergeFileList[:3], mergeFileList[-3:]
            for aFile in fileList:
                if (aFile in mergeFileList):
                    print " (d) this should not happen, right ??? "
                    print aFile
                    sys.exit(-1)
                else:
                    mergeFileList += [aFile]
            print len(mergeFileList), mergeFileList[:3], mergeFileList[-3:]
            print " "
            print " "

    if (len(mergeSdrfDict) == 0):
        print " ERROR ??? nothing returned from SDRFs ... "
        sys.exit(-1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # now we need to get set up for writing the output ...
    # NEW: 21dec12 ... assuming that we will write to current working directory
    outDir = "./"
    outFilename = makeOutputFilename(
        outDir, tumorList, platformID, outSuffix)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # in the second pass, we actually *process* all of the files ...

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

        # HACK: the microsat_instability data is in the "secure" branch ...
        if (platformID.find("microsat_i") > 0):
            topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/" + \
                snapshotName + "/secure/tumor/" + \
                zCancer + "/cgcc/" + platformID

        numSamples = len(mergeFileList)
        print " --> setting numSamples ... ", numSamples, len(mergeFileList), len(mergeSdrfDict)

        print ' starting from top-level directory ', topDir

        dMatch = "Level_3"
        if (zPlat == "microsat_i"):
            dMatch = "Level_1"

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
                print '     archiveList : ', mergeArchiveList

                if (len(mergeArchiveList) == 0):
                    print " WARNING: in make_Level3_matrix:  empty archive list ??? "
                    continue

                # we only look into archives that are in our archive list ... this
                # should take care of the problem of grabbing old data ...
                # (assuming that we *have* an archive list!)
                if (mergeArchiveList[0] != 'unknown'):
                    if (archiveName not in mergeArchiveList):
                        continue

                d2 = path.path(dName)
                print '     looking for txt files in list of length %d ' % (len(d2.files()))
                for fName in d2.files():

                    if (fName.endswith(".txt") >= 0):
                        fileName = getLastBit(fName)
                        # similarly, we only read files that are in our file
                        # list ...
                        if (fileName not in mergeFileList):
                            print '     SKIP: this file is not in our list (%s) ' % (fileName)
                            continue

                        if (fileName in gotFiles):
                            print '     SKIP: already read this file (%s) ' % (fileName)
                            continue

                        print " processing file : iS=%d %s " % (iS, fileName)
                        gotFiles += [fileName]
                        numProc += 1

                        # -----------------------------------------------------
                        # these platforms have just one sample's worth of data
                        # per file
                        if ((zPlat == "HT_HG-U133A") or (zPlat == "AgilentG4502A_07_1") or (zPlat == "AgilentG4502A_07_2")
                            or (zPlat == "AgilentG4502A_07_3") or (zPlat == "H-miRNA_8x15K")
                            or (zPlat == "IlluminaGA_RNASeq") or (zPlat == "IlluminaGA_miRNASeq")
                            or (zPlat == "IlluminaGA_RNASeqV2")
                            or (zPlat == "IlluminaHiSeq_RNASeq") or (zPlat == "IlluminaHiSeq_RNASeqV2")
                            or (zPlat == "IlluminaHiSeq_miRNASeq")
                            or (zPlat == "HumanMethylation27") or (zPlat == "Genome_Wide_SNP_6")
                            or (zPlat == "HumanMethylation450") or (zPlat == "MDA_RPPA_Core")
                                or (zPlat == "microsat_i")):
                            (barcode, info) = getSampleID(
                                mergeSdrfDict, fileName)
                            print barcode, info
                            sampleList += [barcode]
                            (geneList, dataVec) = readOneDataFile(fName,
                                                                  geneList, zPlat, metaData)
                            # print geneList[:10]
                            # print dataVec[:10]

                            if (numGenes == 0):

                                # for Genome_Wide_SNP_6 segmentations, we don't have a fixed
                                # number of genes but rather a variable number
                                # of segmentations ...
                                if (zPlat == "Genome_Wide_SNP_6"):
                                    # looking at the current set of ~3500 TCGA level-3 segmentations,
                                    # the # of segments per sample is quite highly variable ...
                                    # 50th %ile ~  700
                                    # 90th %ile ~ 1100
                                    # 97th %ile ~ 3000
                                    # but a few samples far exceed 30,000 ... we will set an upper
                                    # limit at 25000 and then just deal with the samples that exceed that ...
                                    # (though perhaps these are the files that have "do not use" in
                                    # the SDRF file???)
                                    numGenes = 25000
                                    # trying to handle LAML ??? 22feb13
                                    numGenes = 60000
                                else:
                                    numGenes = len(geneList)

                                print " --> allocating dataMatrix ... %d x %d " % (numGenes, numSamples)
                                dataMatrix = [0] * numGenes
                                for iG in range(numGenes):
                                    dataMatrix[iG] = [0] * numSamples

                                if (zPlat == "Genome_Wide_SNP_6"):
                                    print " --> allocating segMatrix ... %d x %d " % (numGenes, numSamples)
                                    segMatrix = [0] * numGenes
                                    for iG in range(numGenes):
                                        segMatrix[iG] = [''] * numSamples

                            if (len(dataVec) > numGenes):
                                if (zPlat == "Genome_Wide_SNP_6"):
                                    (geneList, dataVec) = mergeSegments(
                                        geneList, dataVec)
                                else:
                                    print " ERROR ??? should not be here ... now what ? "
                                    sys.exit(-1)

                            print "      getting data from <%s> for barcode <%s> and iS=%3d " % (fName, barcode, iS)

                            # and write out what we are using to the log file
                            # ...
                            if (not logFlag):
                                # open a log file to which we will write the
                                # specs for all of the files used ...
                                fhLog = openDataFreezeLogFile(
                                    zCancer, outSuffix, platformStrings)
                                logFlag = 1

                            writeDataFreezeLog(fhLog, fName, barcode)

                            # for iG in range(numGenes):
                            for iG in range(len(dataVec)):
                                try:
                                    dataMatrix[iG][iS] = dataVec[iG]
                                except:
                                    print " PROBLEM ???  iG=%d  iS=%d " % (iG, iS)
                                    sys.exit(-1)

                            # if this is the GWS6 snp chip, we need to copy the
                            # segment positions too ...
                            if (zPlat == "Genome_Wide_SNP_6"):
                                for iG in range(len(dataVec)):
                                    segMatrix[iG][iS] = geneList[iG]

                            iS += 1

                        # -----------------------------------------------------
                        # we should never get here ...
                        else:
                            print " ERROR !!! ??? how did this happen ? unknown platform ? ", zPlat
                            sys.exit(-1)

                print " --> got %d files processed " % numProc
                print ' '

    print " what do we have here ??? "
    print len(sampleList)
    print len(gotFiles)
    print len(geneList)
    print numGenes, numProc, iS

    # print ' '
    print '         have data matrix of size %d genes x %d samples \n' % (numGenes, numSamples)
    print ' '
    # print sampleList[:10]

    if ((numGenes * numSamples) < 10):
        print " ERROR ??? we have essentially no data ??? "
        sys.exit(-1)

    if (numSamples != len(sampleList)):
        print " ERROR ??? how can the number of samples not match the length of the sample list ??? "
        print numSamples, len(sampleList)
        sys.exit(-1)

    # if we get this far, we should make sure that the output directory we
    # want exists
    print " --> testing that we have an output directory ... <%s> " % outDir
    tsvIO.createDir(outDir)
    print "     output file name will be called <%s> " % outFilename

    # finally we write out the data (if it is CN data, first we need to resegment it)
    # at this stage, we set a very high level for dropping rows or columns due to missing
    # data ... 80% is the value I'm trying out now (3pm Fri 11Feb)

    if (zPlat == "Genome_Wide_SNP_6"):

        if (1):
            # this is better for producing variable-length, hopefully
            # uncorrelated, features
            steplength = 1000
            cutFrac = 0.01
            cutFrac = 0.02  # 26may12 : trying ~ 2x as many segments
        if (0):
            # this is to force all bins to be the same length and for all bins to be
            # written to the output file
            steplength = 100000
            cutFrac = 1.00
        (segList, sampleList, dataMatrix) = resegmentCNdata(
            sampleList, segMatrix, dataMatrix, steplength, cutFrac)

        try:
            dataD = {}
            dataD['rowLabels'] = segList
            dataD['colLabels'] = sampleList
            dataD['dataMatrix'] = dataMatrix
            dataD['dataType'] = getDataType(segList[0])

            newFeatureName = "C:SAMP:" + \
                dataTypeDict[zPlat][1].lower() + "Platform" + ":::::" + \
                dataTypeDict[zPlat][2]
            newFeatureValue = zPlat
            dataD = tsvIO.addConstFeature(
                dataD, newFeatureName, newFeatureValue)

            sortRowFlag = 0
            sortColFlag = 0
            tsvIO.writeTSV_dataMatrix(
                dataD, sortRowFlag, sortColFlag, outFilename)
        except:
            print " FATAL ERROR: failed to write out any resegmented copy-number data "

    else:
        dataD = {}
        dataD['rowLabels'] = geneList
        dataD['colLabels'] = sampleList
        dataD['dataMatrix'] = dataMatrix
        dataD['dataType'] = getDataType(geneList[0])
        print ' writing out data matrix to ', outFilename

        newFeatureName = "C:SAMP:" + \
            dataTypeDict[zPlat][1].lower() + "Platform" + ":::::" + \
            dataTypeDict[zPlat][2]
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
