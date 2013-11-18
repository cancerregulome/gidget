import sys
import traceback

__author__ = 'xshu'

# global variables
gene2uniprotMapping = {}


def showHelp():
    print\
    '''
    This program updates gene2uniprot by adding more mappings with UniProt id mapping file

    Prerequisite: createGene2Uniprot.py MUST be executed first

    Usage: %s
            Parameter         Description
            -gene2uniprot     the mapping file to update
            -uniprot2gene     ID mapping file between uniprot and entrez gene from UniProt
            -output           Output file

            (eg. %s -gene2uniprot <<absolute gene2uniprot file path>>
                    -uniprot2gene <<absolute uniprot2gene file path>>
                    -output       <<absolute output file path>> )
    ''' % (sys.argv[0], sys.argv[0])


def isLong(str):
    try:
        long(str)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def loadUniprot2Gene(uniprot2gene):
    # load uniprot2gene file and add items to gene2uniprotMappings
    if uniprot2gene != "":
        uniprot2geneHandle = open(uniprot2gene, "r")
        for line in uniprot2geneHandle:
            line = line.rstrip("\n")
            fields = line.split("\t")
            if len(fields) == 2:
                geneIDList = fields[0].strip().split(";")
                uniprotID = fields[1].strip()
                for geneID in geneIDList:
                    if isLong(geneID):
                        if (geneID not in gene2uniprotMapping):
                            gene2uniprotMapping[geneID] = uniprotID
                        else:
                            uniprotIDList = gene2uniprotMapping[geneID]
                            if (uniprotIDList.find(uniprotID) == -1):
                                gene2uniprotMapping[geneID] += ";" + uniprotID
        uniprot2geneHandle.close()


def update(output, gene2uniprot):
    gene2uniprotUpdateHandle = open(output, "w")

    gene2uniprotHandle = open(gene2uniprot, "r")
    for line in gene2uniprotHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        geneID = fields[0].strip()
        geneSymbol = fields[1]
        geneAliases = fields[2]
        geneOld = fields[3]
        uniprotID = fields[4]
        if isLong(geneID) and geneID in gene2uniprotMapping:
            uniprotIDList = gene2uniprotMapping[geneID].split(";")
            for item in uniprotIDList:
                if uniprotID.find(item) == -1:
                    uniprotID += ";" + item
        gene2uniprotUpdateHandle.write("%s\t%s\t%s\t%s\t%s\n" % (
            geneID, geneSymbol, geneAliases, geneOld, uniprotID.rstrip(";")))
    gene2uniprotHandle.close()

    gene2uniprotUpdateHandle.close()


def _mainFunc():
    try:
        for index in range(len(sys.argv)):
            if sys.argv[index] == "-gene2uniprot":
                gene2uniprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot2gene":
                uniprot2gene = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if gene2uniprot == "" or uniprot2gene == "" or output == "":
            raise Exception("All parameters are required!")

        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        loadUniprot2Gene(uniprot2gene)
        update(output, gene2uniprot)

    except Exception:
        traceback.print_exc()
        showHelp()

        # Initialization and Execution
        # Direct invocation

if __name__ == "__main__":
    _mainFunc()
