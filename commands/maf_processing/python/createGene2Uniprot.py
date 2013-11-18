import sys
import traceback

__author__ = 'xshu'

# global variables
symbolsFound = []
geneSymbol2IDMapping = {}
geneSymbol2SynonymsMapping = {}


def showHelp():
    print\
    '''
    This program creates the initial gene2uniprot by updating aliases in hgncSymbolAlias2Uniprot with NCBI gene-info file

    Usage: %s
            Parameter         Description
            -geneInfo         gene_info file from NCBI
            -hgnc2uniprot     hgnc symbols to uniprot id downloaded from HUGO
            -output           Output file

            (eg. %s -geneInfo <<absolute gene_info file path>>
                    -hgnc2uniprot <<absolute hgnc2uniprot file path>>
                    -output <<absolute output file path>> )

    ''' % (sys.argv[0], sys.argv[0])


def loadGeneInfo(geneInfo):
    if geneInfo != "":
        geneInfoHandle = open(geneInfo, "r")
        for line in geneInfoHandle:
            line = line.rstrip("\n")
            fields = line.split("\t")

            geneID = (long)(fields[0].strip())
            geneSymbol = fields[1].strip()
            geneSynonyms = fields[2].strip().replace("|", ";")

            if geneSymbol not in geneSymbol2IDMapping:
                geneSymbol2IDMapping[geneSymbol] = geneID
            if geneSymbol not in geneSymbol2SynonymsMapping:
                geneSymbol2SynonymsMapping[geneSymbol] = geneSynonyms

# new hgnc file format
# hgnc2uniprot download has been changed to include approved symbols, previous symbols, synonyms, and uniprot IDs
# now including previous HGNC symbols


def create(output, hgnc2uniprot):
    gene2uniprotHandle = open(output, "w")

    hgnc2uniprotHandle = open(hgnc2uniprot, "r")
    hgnc2uniprotHandle.readline()
    for line in hgnc2uniprotHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        if len(fields) == 4:
            hgncSymbol = fields[0].strip()
            hgncPreviousSymbol = fields[1].strip().split(", ")
            hgncAliases = fields[2].strip().split(", ")
            unitprotID = fields[3].strip()

            if hgncSymbol in geneSymbol2SynonymsMapping and hgncSymbol in geneSymbol2IDMapping:
                symbolsFound.append(hgncSymbol)
                geneID = geneSymbol2IDMapping[hgncSymbol]
                ncbiSynonyms = geneSymbol2SynonymsMapping[hgncSymbol]
                if len(hgncAliases) >= 0:
                    for alias in hgncAliases:
                        if ncbiSynonyms.find(alias) == -1:
                            alias.strip()
                            ncbiSynonyms += ";"
                            ncbiSynonyms += alias

            # this is new code for adding previous HGNC symbols
            if hgncSymbol in geneSymbol2IDMapping:
                hgncOLD = ""
                if len(hgncPreviousSymbol) >= 0:
                    for old in hgncPreviousSymbol:
                        if hgncOLD.find(old) == -1:
                            old.strip()
                            hgncOLD += old
                            hgncOLD += ";"

                gene2uniprotHandle.write(
                    "%s\t%s\t%s\t%s\t%s\n" % (geneID, hgncSymbol, ncbiSynonyms, hgncOLD, unitprotID.rstrip(";")))
    hgnc2uniprotHandle.close()

    # append genes that are NOT included in the hgnc2uniprot file
    for hgncSymbol in geneSymbol2IDMapping:
        if hgncSymbol not in symbolsFound:
            geneID = geneSymbol2IDMapping[hgncSymbol]
            synonyms = geneSymbol2SynonymsMapping[hgncSymbol]
            gene2uniprotHandle.write("%s\t%s\t%s\t%s\t%s\n" %
                                     (geneID, hgncSymbol, synonyms, "", ""))

    gene2uniprotHandle.close()


def _mainFunc():
    try:
        for index in range(len(sys.argv)):
            if sys.argv[index] == "-geneInfo":
                geneInfo = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-hgnc2uniprot":
                hgnc2uniprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if geneInfo == "" or hgnc2uniprot == "" or output == "":
            raise Exception("All parameters are required!")

        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        loadGeneInfo(geneInfo)
        create(output, hgnc2uniprot)

    except Exception:
        traceback.print_exc()
        showHelp()

        # Initialization and Execution
        # Direct invocation

if __name__ == "__main__":
    _mainFunc()
