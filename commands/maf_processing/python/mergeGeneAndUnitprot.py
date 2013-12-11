import sys
import traceback

__author__ = 'xshu'

# global variables
refseq2uniprotMapping = {}


def showHelp():
    print\
    '''
    This program updates MAF by adding a column of uniprot id list

    Usage: %s
            Parameter         Description
            -gene2refseq      gene id to refseq id mapping file
            -refseq2uniprot   refseq id to uniprot id mapping file
            -output           Output file

            (eg. %s -gene2refseq <<absolute gene2refseq file path>>  -refseq2uniprot <<absolute refseq2uniprot mapping file path>> \
                    -output <<absolute output file path>> )

    ''' % (sys.argv[0], sys.argv[0])


def loadMappings(refseq2uniprot):
    global refseq2uniprotMapping

    refseq2uniprotHandle = open(refseq2uniprot, "r")
    refseq2uniprotHandle.readline()
    for line in refseq2uniprotHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        pAssession = fields[0].strip()
        uniprotID = fields[1].strip()

        if pAssession not in refseq2uniprotMapping:
            refseq2uniprotMapping[pAssession] = uniprotID
        else:
            refseq2uniprotMapping[pAssession] += ";" + uniprotID

    refseq2uniprotHandle.close()


def merge(output, gene2refseq):
    gene2uniprotHandle = open(output, "w")

    gene2refseqHandle = open(gene2refseq, "r")
    for line in gene2refseqHandle:
        line = line.rstrip("\n")
        pAssession = line.split("\t")[0].strip()
        if pAssession in output:
            line += "\t" + refseq2uniprotMapping[pAssession]
        gene2uniprotHandle.write(line + "\n")

    gene2uniprotHandle.close()
    gene2refseqHandle.close()


def _mainFunc():
    try:
        for index in range(len(sys.argv)):
            if sys.argv[index] == "-gene2refseq":
                gene2refseq = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-refseq2uniprot":
                refseq2uniprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()
        loadMappings(refseq2uniprot)
        merge(output, gene2refseq)

    except Exception:
        traceback.print_exc()
        showHelp()

        # Initialization and Execution
        # Direct invocation

if __name__ == "__main__":
    _mainFunc()
