import sys
import traceback
import re
import linecache

__author__ = 'xshu'

# global variables
unprocessedIDs = []
iso12PosInFileMapping = {}


def showHelp():
    print\
    '''
    This program updates gene2uniprot by adding more mappings with the records combined from
    uni_sprot and uni_trembl dat files (downloaded from UniProt)

    Usage: %s
            Parameter               Description
            -uniprot_sprot_human    gene info 2 uniprot sprot mapping extracted from uniprot_sprot dat file
            -uniprot_trembl_human   gene info 2 uniprot trembl mapping extracted from uniprot_trembl dat file
            -uniprot_isoform        the isoform file from UniProt
            -output_sprot           updated gene info 2 uniprot sprot mapping
            -output_trembl          updated gene info 2 uniprot trembl mapping

            (eg. %s -uniprot_sprot_human   <<absolute uniprot sprot human file path>>
                    -uniprot_trembl_human  <<absolute uniprot trembl human file path>>
                    -uniprot_isoform       <<absolute uniprot isoform file>>
                    -output_sprot          <<absolute sprot output file path>>
                    -output_trembl         <<absolute trembl output file path>> )
    ''' % (sys.argv[0], sys.argv[0])


class DataType:
    SPROT = 1
    TREMBL = 2


def processUniprotDAT(uniprot_human, output):
    # get isoform1 sequences from uniprot_human dat files
    if output != "" and uniprot_human != "":
        # suppose a sequence is always needed UNLESS the field "IsoId=XXXX-1" is explicitly shown in the uniprot dat files AND
        # its following field "Sequence" has a value other than "Displayed". For example in the section for "ID  ARHG7_HUMAN"
        # these lines appear:
        # CC       Name=4;
        # CC       IsoId=Q14155-4; Sequence=Displayed;
        # CC       Name=1;
        # CC       IsoId=Q14155-1; Sequence=VSP_011032, VSP_011035;
        # In the above case. The sequence presented for this section belongs to isoform4 NOT isoform1. So this program
        # will grab isoform1 from "uniprot_sprot_varsplic.fasta" instead (Check for more details in the method
        # processUniprotIsoformFasta(uniprot_isoform, output) that follows
        needSequence = True

        gettingSequence = False
        primAccession = ""
        sequence = ""

        outputHandle = open(output, "w")
        uniprot_humanHandle = open(uniprot_human, "r")
        for line in uniprot_humanHandle:
            line = line.rstrip("\n")

            idMatcher = re.match("^ID\s+([^\s]*)\s+(.*)", line)
            if idMatcher:
                needSequence = True
                gettingSequence = False
                primAccession = ""
                sequence = ""

            acMatcher = re.match("^AC\s+(.*)", line)
            if acMatcher:
                accessions = acMatcher.group(1)
                if primAccession == "":
                    primAccession = accessions.split(";")[0]

            # removed the condition of -1 primAccession.   Now all displayed
            # sequences are shown
            iso1Matcher = re.match(
                "^CC\s+IsoId=(" + primAccession + ");\s*Sequence=([^;]*);", line)
            if iso1Matcher:
                iso1Id = iso1Matcher.group(1)
                if iso1Matcher.group(2) != "Displayed":
                    unprocessedIDs.append(iso1Id)
                    needSequence = False
            elif needSequence:
                if not gettingSequence:
                    sequenceMatcher = re.match("^SQ\s+.*SEQUENCE\s+.*", line)
                    if sequenceMatcher:
                        gettingSequence = True
                else:
                    sequenceEndMatcher = re.match("^//.*", line)
                    if not sequenceEndMatcher:
                        sequence += line.replace(" ", "") + "\n"
                    else:
                        outputHandle.write(">sp|%s\n" % (primAccession))
                        outputHandle.write(sequence)

        uniprot_humanHandle.close()
        outputHandle.close()


def processUniprotIsoformFasta(uniprot_isoform, output):
    # get isoform1 sequences from uniprot_isoform file
    if output != "" and uniprot_isoform != "":
        # first map isoform1 accession number to the position range in the file
        isoId = ""
        getPreRecord = False
        preFileLineNo = 0
        recordStartLineNo = preFileLineNo

        uniprot_isoformHandle = open(uniprot_isoform, "r")
        for line in uniprot_isoformHandle:
            line = line.rstrip("\n")

            seqHeaderMatcher = re.match("^>sp\|([^\|]+)\|.*", line)
            if seqHeaderMatcher:
                if getPreRecord:
                    # save the start and end line # for the previous record
                    iso12PosInFileMapping[isoId] = (
                        recordStartLineNo, preFileLineNo)

                isoId = seqHeaderMatcher.group(1)
                iso1Matcher = re.match("^.*-1$", isoId)
                if iso1Matcher:
                    getPreRecord = True
                else:
                    getPreRecord = False

                recordStartLineNo = preFileLineNo + 1

            preFileLineNo += 1
        uniprot_isoformHandle.close()

        # output the sequences for the proteins not displayed in uniprot human
        # dat
        outputHandle = open(output, "a")
        for item in unprocessedIDs:
            if item in iso12PosInFileMapping:
                linesRange = iso12PosInFileMapping[item]
                startLine = linesRange[0]
                endLine = linesRange[1]
                for step in range(0, endLine - startLine):
                    outputHandle.write(
                        linecache.getline(uniprot_isoform, startLine + step))
        outputHandle.close()


def _mainFunc():
    try:
        uniprot_sprot_human = ""
        uniprot_trembl_human = ""
        uniprot_isoform = ""
        output_sprot = ""
        output_trembl = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-uniprot_sprot_human":
                uniprot_sprot_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_trembl_human":
                uniprot_trembl_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_isoform":
                uniprot_isoform = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output_sprot":
                output_sprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output_trembl":
                output_trembl = sys.argv[index + 1].strip()

        if uniprot_sprot_human == "" or uniprot_trembl_human == "" or uniprot_isoform == "" or output_sprot == "" or output_trembl == "":
            raise Exception("All parameters are required!")

        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        processUniprotDAT(uniprot_sprot_human, output_sprot)
        processUniprotIsoformFasta(uniprot_isoform, output_sprot)

        global iso12PosInFileMapping
        iso12PosInFileMapping = {}
        global unprocessedIDs
        unprocessedIDs = []

        # todo: Memory is in an intensive use when the mappings are pre-loaded.
        # Check if PyTables can offer an alternative whenever possible
        processUniprotDAT(uniprot_trembl_human, output_trembl)
        processUniprotIsoformFasta(uniprot_isoform, output_trembl)

    except Exception:
        traceback.print_exc()
        showHelp()

if __name__ == "__main__":
    _mainFunc()
