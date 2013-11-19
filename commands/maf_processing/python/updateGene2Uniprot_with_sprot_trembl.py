import sys
import traceback
import re

__author__ = 'xshu'

# global variables
id2symbolMapping = {}
primary2secondaryMapping = {}
id2uniprotMapping = {}
symbol2uniprotMapping = {}
idsFound = []


def showHelp():
    print\
    '''
    This program updates gene2uniprot by adding more mappings with the records combined from
    uni_sprot and uni_trembl dat files (downloaded from UniProt)

    Prerequisite: updateGene2Uniprot_with_uniprotIDMapping.py MUST be executed first

    Usage: %s
            Parameter               Description
            -gene2uniprot           gene_info file from NCBI
            -uniprot_sprot_human    gene info 2 uniprot sprot mapping extracted from uniprot_sprot dat file
            -uniprot_trembl_human   gene info 2 uniprot trembl mapping extracted from uniprot_trembl dat file
            -output_sprot           updated gene info 2 uniprot sprot mapping
            -output_trembl          updated gene info 2 uniprot trembl mapping

            (eg. %s -gene2uniprot          <<absolute gene2uniprot file path>>
                    -uniprot_sprot_human   <<absolute uniprot sprot human file path>>
                    -uniprot_trembl_human  <<absolute uniprot trembl human file path>>
                    -output_sprot          <<absolute sprot output file path>>
                    -output_trembl         <<absolute trembl output file path>> )
    ''' % (sys.argv[0], sys.argv[0])


class DataType:
    SPROT = 1
    TREMBL = 2


def isLong(str):
    try:
        long(str)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def addItemsToMapping(key, value, mappingObj):
    if key == "":
        return
    value = str(value)

    if key not in mappingObj:
        mappingObj[key] = value
    else:
        oldValue = mappingObj[key]
        if oldValue.find(value) == -1:
            mappingObj[key] += ";" + value


def loadUniprotHuman(uniprot_human):
    # load uniprot_human file and add items to gene 2 uniprot Mappings
    if uniprot_human != "":
        uniprot_humanHandle = open(uniprot_human, "r")

        lastID = ""
        currentID = ""
        curPrimaryAccession = ""
        curSecondaryAccessions = []
        curGeneName = ""
        curGeneID = ""

        for line in uniprot_humanHandle:
            line = line.rstrip("\n")

            idMatcher = re.match("^ID\s+([^\s]*)\s+(.*)", line)
            if idMatcher:
                currentID = idMatcher.group(1)

            if lastID != currentID:
                if curGeneID != "" and isLong(curGeneID):
                    addItemsToMapping(
                        curGeneID, curPrimaryAccession, id2uniprotMapping)

                if curGeneName != "":
                    addItemsToMapping(
                        curGeneName, curPrimaryAccession, symbol2uniprotMapping)
                    if curGeneID != "" and isLong(curGeneID):
                        addItemsToMapping(
                            curGeneID, curGeneName, id2symbolMapping)

                if len(curSecondaryAccessions) > 0:
                    primary2secondaryMapping[
                        curPrimaryAccession] = curSecondaryAccessions

                lastID = currentID
                curPrimaryAccession = ""
                curSecondaryAccessions = []
                curGeneName = ""
                curGeneID = ""

            acMatcher = re.match("^AC\s+(.*)", line)
            nameMatcher = re.match(r'([^=]*Name)=([^=]*);(.*)', line)
            drMatcher = re.match("^DR\s+GeneID;\s*(.*);", line)

            if acMatcher:
                accessions = acMatcher.group(1)
                if curPrimaryAccession == "":
                    curPrimaryAccession = accessions.split(";")[0]
                    accessions = re.sub(
                        "\s*", "", accessions[accessions.find(";") + 1:])
                curSecondaryAccessions.extend(accessions.split(";"))
            elif nameMatcher:
                curGeneName = nameMatcher.group(2)
            elif drMatcher:
                curGeneID = drMatcher.group(1)

        uniprot_humanHandle.close()


def removeSecondaryAccessions(primaryAccessions, oldUniprotID):
    finalAccessions = []
    updatedUniprotID = ""

    # get rid of secondary accessions
    if oldUniprotID != "":
        oldIDList = oldUniprotID.split(";")
        for id in oldIDList:
            secondaryAccessionFound = False
            for primAccession in primaryAccessions:
                if id in primary2secondaryMapping[primAccession]:
                    secondaryAccessionFound = True
                    break
            if not secondaryAccessionFound:
                updatedUniprotID += id + ";"

    # keep the primary accession
    for primAccession in primaryAccessions:
        if updatedUniprotID.find(primAccession) == -1:
            finalAccessions.append(primAccession)

    return finalAccessions


def update(datatype, output, gene2uniprot):
    gene2uniprotUpdateHandle = open(output, "w")
    gene2uniprotUpdateHandle.write(
        "geneID\tgeneSymbol\tgeneAliases\tgeneOld\tUniprotID\n")

    gene2uniprotHandle = open(gene2uniprot, "r")
    for line in gene2uniprotHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")

        geneID = fields[0].strip()
        geneSymbol = fields[1]
        geneAliases = fields[2]
        geneOld = fields[3]
        uniprotID = ""
        if datatype == DataType.SPROT:
            uniprotID = fields[4]

        idFound = False
        checkSymbol = False
        primAccessionList = []

        # update uniprot id using the gene id 2 uniprot accession mapping
        if isLong(geneID) and geneID in id2uniprotMapping:
            idFound = True
            primaryAccessions = id2uniprotMapping[geneID]
            if primaryAccessions != "":
                primAccessionList = removeSecondaryAccessions(
                    primaryAccessions.split(";"), uniprotID)
                # Normally one gene maps to one uniprot swissprot id
                if len(primAccessionList) > 1:
                    if geneID in id2symbolMapping and geneSymbol == id2symbolMapping[geneID]:
                        checkSymbol = True

        # update uniprot id using the gene name 2 uniprot mapping
        if checkSymbol and geneSymbol in symbol2uniprotMapping:
            primaryAccessions = symbol2uniprotMapping[geneSymbol]
            if primaryAccessions != "":
                primAccessionList = removeSecondaryAccessions(
                    primaryAccessions.split(";"), uniprotID)

        for accession in primAccessionList:
            if uniprotID == "":
                uniprotID = accession
            else:
                uniprotID += ";" + accession
        gene2uniprotUpdateHandle.write("%s\t%s\t%s\t%s\t%s\n" %
                                       (geneID, geneSymbol, geneAliases, geneOld, uniprotID))

        # record the navigated gene id
        if idFound and geneID not in idsFound:
            idsFound.append(geneID)

    # add the gene info that is not included in the original gene2uniprot file
    for geneID in id2symbolMapping:
        if geneID not in idsFound:
            symbols = id2symbolMapping[geneID]
            uniprotID = ""
            if geneID in id2uniprotMapping:
                uniprotID = id2uniprotMapping[geneID]
            if uniprotID != "":
                gene2uniprotUpdateHandle.write(
                    "%s\t%s\t%s\t%s\t%s\n" % (geneID, symbols, "", "", uniprotID))

    gene2uniprotHandle.close()
    gene2uniprotUpdateHandle.close()


def _mainFunc():
    try:
        gene2uniprot = ""
        uniprot_sprot_human = ""
        uniprot_trembl_human = ""
        output_sprot = ""
        output_trembl = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-gene2uniprot":
                gene2uniprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_sprot_human":
                uniprot_sprot_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_trembl_human":
                uniprot_trembl_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output_sprot":
                output_sprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output_trembl":
                output_trembl = sys.argv[index + 1].strip()

        if gene2uniprot == "" or uniprot_sprot_human == "" or uniprot_trembl_human == "" or output_sprot == "" or output_trembl == "":
            raise Exception("All parameters are required!")

        # process uniprot_sprot_human
        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        loadUniprotHuman(uniprot_sprot_human)
        update(DataType.SPROT, output_sprot, gene2uniprot)

        # clear up mappings and lists
        global id2symbolMapping
        global primary2secondaryMapping
        global id2uniprotMapping
        global symbol2uniprotMapping
        global idsFound

        id2symbolMapping = {}
        primary2secondaryMapping = {}
        id2uniprotMapping = {}
        symbol2uniprotMapping = {}
        idsFound = []

        # process uniprot_trembl_human
        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        loadUniprotHuman(uniprot_trembl_human)
        update(DataType.TREMBL, output_trembl, gene2uniprot)

    except Exception:
        traceback.print_exc()
        showHelp()

if __name__ == "__main__":
    _mainFunc()
