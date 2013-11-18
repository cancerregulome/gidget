import sys
import traceback
import shutil
import os

__author__ = 'xshu'

# global variables
g_id2uniprotMapping = {}
g_symbol2uniprotMapping = {}
g_alias_old_symbol2uniprotMapping = {}
g_mafList = []


def showHelp():
    print\
    '''
    This program updates MAF by adding a column of uniprot id list. All parameters are required

    Usage: %s
            Parameter               Description
            -g_mafList                a configuration file having a list of MAF files (one MAF absolute path per line)
            -gene2uniprot           this file contains a list of geneID, geneSymbol,geneAliaes and uniprotID
            -output                 Output folder


            (eg. %s -g_mafList        <<absolute configuration file containing a list of maf file paths. One maf path per line>>
                    -gene2uniprot   <<absolute gene2uniprot mapping file path>>
                    -output         <<absolute output folder path>> )

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
    value = str(value)
    if key not in mappingObj:
        mappingObj[key] = value
    else:
        oldValue = mappingObj[key]
        if oldValue.find(value) == -1:
            mappingObj[key] += ";"
            mappingObj[key] += value


def loadGene2Uniprot(datatype, gene2uniprot):
    global g_id2uniprotMapping
    global g_symbol2uniprotMapping
    global g_alias_old_symbol2uniprotMapping

    g_id2uniprotMapping = {}
    g_symbol2uniprotMapping = {}
    g_alias_old_symbol2uniprotMapping = {}

    # load gene2uniprot mapping
    if gene2uniprot != "":
        gene2uniprotHandle = open(gene2uniprot, "r")
        gene2uniprotHandle.readline()
        for line in gene2uniprotHandle:
            line = line.rstrip("\n")
            fields = line.split("\t")

            geneID = fields[0].strip()
            symbol = fields[1].strip()
            aliases = fields[2].strip().split(";")
            old = fields[3].strip().split(";")
            uniprotID = fields[4].strip()
            if uniprotID != "" and uniprotID != "-":
                # for now only the first available trembl id is included
                if datatype == DataType.TREMBL:
                    uniprotID = uniprotID.split(";")[0]

                if isLong(geneID):
                    addItemsToMapping(geneID, uniprotID, g_id2uniprotMapping)

                if symbol != "":
                    addItemsToMapping(
                        symbol, uniprotID, g_symbol2uniprotMapping)

                if len(aliases) >= 0:
                    for one_alias in aliases:
                        addItemsToMapping(one_alias, uniprotID,
                                          g_alias_old_symbol2uniprotMapping)

                if len(old) >= 0:
                    for one_old in old:
                        addItemsToMapping(one_old, uniprotID,
                                          g_alias_old_symbol2uniprotMapping)

        gene2uniprotHandle.close()


class UNMAPPED:
    REGULAR = 1
    UNKNOWN = 2
    QUESTION_MARK = 3
    NON_EXISTING_ENTREZ_GENE = 4


def outputUnmappedRecords(type, records):
    lenRecords = len(records)
    if lenRecords == 0:
        return

    if type == UNMAPPED.NON_EXISTING_ENTREZ_GENE:
        print str(lenRecords) + " Items whose Entrez Gene information (ID and Official Symbol) does not map to any UniProt protein information."
        print "Please check if the gene id is outdated or the included HGNC symbol uses an alias instead of the official symbol."
        print "Another possible reason is UniProt has not included any protein information for these genes:"
    elif type == UNMAPPED.UNKNOWN:
        print str(lenRecords) + " Items with HGNC Symbol = \"Unknown\":"
    elif type == UNMAPPED.QUESTION_MARK:
        print str(lenRecords) + " Items with HGNC Symbol = \"?\":"

    for item in records:
        print item

    print

# Assumption: always process sprot ahead of trembl. sprot contains
# reviewed data while the trembl does not


def update(datatype, output):
    entrezGeneUnMappedRecords = []
    unknownUnMappedRecords = []
    questionMarkUnMappedRecords = []
    updatedMafList = []

    if output.rfind("/") != len(output) - 1:
        output += "/"

    global g_mafList
    for maf in g_mafList:
        mafHandle = open(maf, "r")

        updatedMAF = output + maf[maf.rfind("/") + 1:]
        if datatype == DataType.SPROT:
            updatedMAF += "_stage" + str(DataType.SPROT)
        elif datatype == DataType.TREMBL:
            updatedMAF += "_stage" + str(DataType.TREMBL)
        updatedMafList.append(updatedMAF)

        updatedMAFHandle = open(updatedMAF, "w")

        # sometimes the randomly added columns are observed resulting in the incorrect positions of the uniprot output
        # so calculate the exact position where the uniprot output should be
        # placed.
        oldMAFHeaders = mafHandle.readline().rstrip("\n")
        updatedMAFHandle.write(oldMAFHeaders)

        maxNumTabsPerRecordInMAF = long(os.popen("awk 'BEGIN{FS=\"\t\"; maxNumFields = 0;}\
                                            {if (NF > maxNumFields) {maxNumFields = NF}}\
                                            END{print maxNumFields - 1}' " + maf).readline())
        numTabsInOldHeader = oldMAFHeaders.count("\t")
        numTabsToAddForOldHeader = maxNumTabsPerRecordInMAF - \
            numTabsInOldHeader
        if numTabsToAddForOldHeader > 0:
            for index in range(numTabsToAddForOldHeader):
                updatedMAFHandle.write("\t%s" % (""))

        # add two uniprot headers for the maf when sprot data are processed
        if datatype == DataType.SPROT:
            updatedMAFHandle.write("\tUniprot Sprot ID\tUniprot Trembl ID")
        updatedMAFHandle.write("\n")

        # Append either sprot-id or trembl-id
        for line in mafHandle:
            if line.startswith("#"):
                # comment line
                continue
            line = line.rstrip("\n")
            fields = line.split("\t")

            hgncSymbol = fields[0].strip()
            geneID = fields[1].strip()

            addID = True
            uniprotID = ""
            if datatype == DataType.TREMBL:
                # if sprot ids are included, then continue the loop
                # Only when no sprot id exists for the current record will the
                # first available trembl id be included
                sprotID = fields[len(fields) - 1].strip()
                if sprotID != "":
                    addID = False

            # changed this so that symbol is used first, then alias and old
            # symbols, then geneID
            if addID:
                if hgncSymbol in g_symbol2uniprotMapping:
                    uniprotID = g_symbol2uniprotMapping[hgncSymbol]
                elif hgncSymbol in g_alias_old_symbol2uniprotMapping:
                    uniprotID = g_alias_old_symbol2uniprotMapping[hgncSymbol]
                elif isLong(geneID) and geneID in g_id2uniprotMapping:
                    uniprotID = g_id2uniprotMapping[geneID]
                else:
                    unMappedRecord = hgncSymbol + "\t" + geneID
                    if hgncSymbol.upper() == "UNKNOWN":
                        unknownUnMappedRecords.append(unMappedRecord)
                    if hgncSymbol == "?":
                        questionMarkUnMappedRecords.append(unMappedRecord)
                    if hgncSymbol.upper() != "UNKNOWN" and hgncSymbol != "?" and unMappedRecord not in entrezGeneUnMappedRecords:
                        entrezGeneUnMappedRecords.append(unMappedRecord)

            updatedMAFHandle.write(line)

            # fill in the empty columns from the original MAF with tabs so that
            # the upcoming added columns will be positioned correctly
            if datatype == DataType.SPROT:
                numTabsToAdd = 0
                numTabsInCurLine = line.count("\t")
                if numTabsInOldHeader > maxNumTabsPerRecordInMAF:
                    numTabsToAdd = numTabsInOldHeader - numTabsInCurLine
                elif maxNumTabsPerRecordInMAF > numTabsInOldHeader:
                    numTabsToAdd = maxNumTabsPerRecordInMAF - numTabsInCurLine
                if numTabsToAdd > 0:
                    for index in range(numTabsToAdd):
                        updatedMAFHandle.write("\t%s" % (""))

            # output uniprot id into the MAF
            updatedMAFHandle.write("\t%s\n" % (uniprotID))

        updatedMAFHandle.close()
        mafHandle.close()

        # output the unmapped records after trembl data are processed
        if datatype == DataType.TREMBL:
            # print the unmapped records
            print "Unmapped Records in " + maf[:maf.find("_stage" + str(DataType.SPROT))]
            print
            outputUnmappedRecords(
                UNMAPPED.NON_EXISTING_ENTREZ_GENE, entrezGeneUnMappedRecords)
            outputUnmappedRecords(UNMAPPED.UNKNOWN, unknownUnMappedRecords)
            outputUnmappedRecords(
                UNMAPPED.QUESTION_MARK, questionMarkUnMappedRecords)
            print
            print

            # create file original_maf_name.with_uniprot
            updatedMAFFinal = updatedMAF[
                :updatedMAF.find("_stage" + str(DataType.SPROT))] + ".with_uniprot"
            shutil.move(updatedMAF, updatedMAFFinal)
            os.remove(maf)

    g_mafList = updatedMafList


def _mainFunc():
    try:
        mafInputList = ""
        output = ""
        gene2uniprot_sprot = ""
        gene2uniprot_trembl = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-mafInputList":
                mafInputList = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-gene2uniprot_sprot":
                gene2uniprot_sprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-gene2uniprot_trembl":
                gene2uniprot_trembl = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if mafInputList == "" or output == "" or gene2uniprot_sprot == "" or gene2uniprot_trembl == "":
            raise Exception("All parameters are required!")

        # update maf with sprot ids
        mafInputListHandle = open(mafInputList, "r")
        for maf in mafInputListHandle:
            candidateMaf = maf.rstrip("\n").strip()
            if candidateMaf.startswith("#"):
                continue  # skip comment lines
            if candidateMaf:  # skip blank lines
                g_mafList.append(candidateMaf)
        mafInputListHandle.close()

        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        loadGene2Uniprot(DataType.SPROT, gene2uniprot_sprot)
        update(DataType.SPROT, output)

        # update maf with trembl ids wherever no sprot id exists
        # todo: Memory is in an intensive use when the mappings are pre-loaded. Check if PyTables can offer an alternative whenever possible
        # turning off TREMBL
        loadGene2Uniprot(DataType.TREMBL, gene2uniprot_trembl)
        update(DataType.TREMBL, output)

    except Exception:
        traceback.print_exc()
        showHelp()


if __name__ == "__main__":
    _mainFunc()
