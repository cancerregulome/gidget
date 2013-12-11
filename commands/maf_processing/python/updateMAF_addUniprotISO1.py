import os
import shutil
import sys
import linecache
import re
import traceback

__author__ = 'xshu'

# global variables
id2ISOForm1Mapping = {}
mafList = []


def showHelp():
    print\
    '''
    Prerequisite: This program MUST BE executed after updateMAF_addUniprotID.py completes its job

    This program updates MAF by adding a column of uniprot id list. All parameters are required

    Usage: %s
            Parameter                   Description
            -mafList                    a configuration file having a list of MAF files (one MAF absolute path per line)
            -uniprot_sprot_isoform1     this is a fasta containing isoform1 sequences for sprot entries
            -uniprot_trembl_isoform1    this is a fasta containing isoform1 sequences for trembl entries
            -output                     Output folder


            (eg. %s -mafList                    <<absolute configuration file containing a list of maf file paths. One maf path per line>>
                    -uniprot_sprot_isoform1     <<absolute path of the fasta containing isoform1 sequences for sprot entries>>
                    -uniprot_trembl_isoform1    <<absolute path of the fasta containing isoform1 sequences for trembl entries>>
                    -output                     <<absolute output folder path>> )

    ''' % (sys.argv[0], sys.argv[0])


def loadID2ISOForm1(id2isoform1):
    result = {}
    # load id2isoform1 mapping
    if id2isoform1 != "":
        preFileLineNo = 0
        sequenceStartLineNo = preFileLineNo
        id2isoform1Handle = open(id2isoform1, "r")
        for line in id2isoform1Handle:
            line = line.rstrip("\n")

            seqHeaderMatcher = re.match("^>sp\|([^-]+)([-1]*)\|*.*", line)
            if seqHeaderMatcher:
                if preFileLineNo != 0:
                    # save the start and end line # for the previous record
                    result[accessionId] = (sequenceStartLineNo, preFileLineNo)
                accessionId = seqHeaderMatcher.group(1)
                sequenceStartLineNo = preFileLineNo + 2
            preFileLineNo += 1
        id2isoform1Handle.close()
    return result


def update(mafWithUniprotIDList, uniprot_sprot_isoform1, uniprot_trembl_isoform1, output):
    if output.rfind("/") != len(output) - 1:
        output += "/"

    mafWithUniprotIDListHandle = open(mafWithUniprotIDList, "r")
    for maf in mafWithUniprotIDListHandle:
        maf = maf.rstrip("\n")
        updatedMAF = output + maf[maf.rfind("/") + 1:] + "_with_isoform1"
        updatedMAFHandle = open(updatedMAF, "w")

        # write the maf header when sprot data are processed
        mafHandle = open(maf, "r")
        updatedMAFHandle.write(mafHandle.readline().rstrip("\n"))
        updatedMAFHandle.write("\tisoform 1\n")

        # Append isoform 1 to either sprot-id or trembl-id
        for line in mafHandle:
            line = line.rstrip("\n")
            fields = line.split("\t")
            if len(fields) < 34:
                continue

            uniprotID = ""
            IS_SPROT_RECORD = False
            IS_TREMBL_RECORD = False
            sprotID = fields[33].strip()
            tremblID = fields[34].strip()
            if sprotID != "":
                uniprotID = sprotID
                IS_SPROT_RECORD = True
            elif tremblID != "":
                uniprotID = tremblID
                IS_TREMBL_RECORD = True

            if uniprotID != "":
                idList = uniprotID.split(";")
                line += "\t"
                for index in range(0, len(idList)):
                    if index > 0:
                        line += "; "
                    id = idList[index]
                    if id in id2ISOForm1Mapping:
                        posTuple = id2ISOForm1Mapping.get(id)
                        startLine = posTuple[0]
                        endLine = posTuple[1]
                        line += id + ":"
                        for step in range(0, endLine - startLine + 1):
                            if IS_SPROT_RECORD:
                                line += linecache.getline(
                                    uniprot_sprot_isoform1,
                                    startLine + step).rstrip("\n")
                            elif IS_TREMBL_RECORD:
                                line += linecache.getline(
                                    uniprot_trembl_isoform1,
                                    startLine + step).rstrip("\n")
            updatedMAFHandle.write(line + "\n")

        updatedMAFHandle.close()
        mafHandle.close()

        updatedMAFFinal = updatedMAF[:updatedMAF.find(".with_isoform1")]
        os.remove(maf)
        shutil.move(updatedMAF, updatedMAFFinal)


def _mainFunc():
    try:
        mafWithUniprotIDList = ""
        uniprot_sprot_isoform1 = ""
        uniprot_trembl_isoform1 = ""
        output = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-mafWithUniprotIDList":
                mafWithUniprotIDList = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_sprot_isoform1":
                uniprot_sprot_isoform1 = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_trembl_isoform1":
                uniprot_trembl_isoform1 = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if mafWithUniprotIDList == "" or uniprot_sprot_isoform1 == "" or uniprot_trembl_isoform1 == "" or output == "":
            raise Exception("All parameters are required!")

        id2ISOForm1Mapping = loadID2ISOForm1(uniprot_sprot_isoform1)
        id2ISOForm1Mapping.update(loadID2ISOForm1(uniprot_trembl_isoform1))
        update(mafWithUniprotIDList, uniprot_sprot_isoform1,
               uniprot_trembl_isoform1, output)

    except Exception:
        traceback.print_exc()
        showHelp()


if __name__ == "__main__":
    _mainFunc()
