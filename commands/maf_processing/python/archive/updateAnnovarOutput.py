import linecache
import os
import math
import shutil
import sys
import re
import traceback

__author__ = 'xshu'


def showHelp():
    print\
    '''
    This program updates the exonic output from ANNOVAR (see http://www.openbioinformatics.org/annovar/).
    1. For DNP add the normal nucleotides into CDS change for instance c.TT111_112AG
    2. For those that do not include protein change information (form example p.AE111_112IP) add the information

    Usage: %s
            Parameter                   Description
            -annovaroutput              annovar exonic output

            (eg. %s -input    <<absolute data file containing a list of extracted fields from a maf file>>
                    -output   <<absolute output folder path>> )

    ''' % (sys.argv[0], sys.argv[0])


def addNormalNucleotides(annovaroutput):
    tempUpdated = annovaroutput + "_temp"
    tempUpdatedHandle = open(tempUpdated, "w")

    annovaroutputHandle = open(annovaroutput, "r")
    for line in annovaroutputHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        transcripts = fields[2]
        lenFields = len(fields)

        if not transcripts == "":
            transcriptList = transcripts.split(",")
            if len(transcriptList) > 0:
                newTranscripts = ""

                # check and update transcripts accordingly
                for transcript in transcriptList:
                    dnpMatcher = re.match(
                        "^(.+:.+:.+):c\.(\d*_*\d+[T,C,G,A]+.*)", transcript)
                    normalNucleotide = fields[lenFields - 4]
                    if dnpMatcher and not normalNucleotide == "":
                        newTranscript = "%s:%s%s%s" % (
                            dnpMatcher.group(1), "c.", normalNucleotide, dnpMatcher.group(2))
                        newTranscripts += newTranscript + ","
                    elif not transcript == "":
                        newTranscripts += transcript + ","

                line = line.replace(transcripts, newTranscripts)

        tempUpdatedHandle.write("%s\n" % (line))

    tempUpdatedHandle.close()
    annovaroutputHandle.close()

    shutil.move(tempUpdated, annovaroutput)


def loadNonSNPCodingChanges(nonSNPCodingChanges):
    result = {}

    # load a map between
    # 1. line# on the first column in the original annovar output
    # 2. protein sequences start/end line # in this coding change file
    seqStartLine = 0
    seqEndLine = 0
    curLineNo = 1
    nonSNPCodingChangesHandle = open(nonSNPCodingChanges, "r")
    for line in nonSNPCodingChangesHandle:
        headerMatcher = re.match("^>(line\d+)\s+([^\s]*)\s+(.*)", line)
        if headerMatcher:
            seqEndLine = curLineNo - 1

            if curLineNo != 1:
                key = "%s,%s" % (mafLine, transcript)
                result[key] = (seqStartLine, seqEndLine)

            seqStartLine = curLineNo + 1
            mafLine = headerMatcher.group(1)
            transcript = headerMatcher.group(2)
            cchange = headerMatcher.group(3)

        curLineNo += 1

    return result


def getProteinChange(cchange, pchange, translation):
    startCodon = "M"
    stopCodon = "*"
    finalPChange = ""

    prangeMatcher = re.match("^(\d+)_(\d+)", pchange)
    crangeMatcher = re.match("^(\d+)_(\d+)", cchange)

    if prangeMatcher:
        pChangeStartPos = prangeMatcher.group(1)
        pChangeEndPos = prangeMatcher.group(2)
        curAminoacidPos = 1
        record = False
        for char in translation:
            if char == startCodon:
                record = True
            if record:
                if char != stopCodon:
                    if curAminoacidPos >= pChangeStartPos and curAminoacidPos <= pChangeEndPos:
                        finalPChange = finalPChange.join(char)
                else:
                    break
                curAminoacidPos += 1

        if finalPChange != "":
            finalPChange += "%d_%d" % (pChangeStartPos, pChangeEndPos)
    elif crangeMatcher:
        cChangeStartPos = long(crangeMatcher.group(1))
        cChangeEndPos = long(crangeMatcher.group(2))

        # find the protein change range
        offsetStart = long(cChangeStartPos) % 3
        offsetEnd = long(cChangeEndPos) % 3
        aminoacidChangeStartPos = cChangeStartPos / 3
        if offsetStart != 0:
            aminoacidChangeStartPos += 1
        aminoacidChangeEndPos = cChangeEndPos / 3
        if offsetEnd != 0:
            aminoacidChangeEndPos += 1

        # get the protein sequence
        curAminoacidPosInTranslation = 1
        curAminoacidPosInProtein = 0
        pChangeStartPos = 0
        pChangeEndPos = 0
        record = False
        for char in translation:
            if char == startCodon:
                curAminoacidPosInProtein = 1
                record = True
            if record:
                if char != stopCodon:
                    if curAminoacidPosInTranslation >= aminoacidChangeStartPos and curAminoacidPosInTranslation <= aminoacidChangeEndPos:
                        if finalPChange == "":
                            pChangeStartPos = curAminoacidPosInProtein
                        finalPChange = finalPChange.join(char)
                    elif finalPChange != "":
                        pChangeEndPos = curAminoacidPosInProtein - 1
                        break
                    curAminoacidPosInProtein += 1
                else:
                    pChangeEndPos = curAminoacidPosInProtein - 1
                    break
            curAminoacidPosInTranslation += 1

        if finalPChange != "":
            posChangeStr = "%d_%d" % (pChangeStartPos, pChangeEndPos)
            if pChangeStartPos == pChangeEndPos:
                posChangeStr = "%d" % (pChangeStartPos)
            finalPChange = "%s%s" % (posChangeStr, finalPChange)

    return finalPChange


def processDNP(annovarNonSNP, mafLine, annotation, mafline2proteinSeqMap):
    newAnnotation = ""

    if annovarNonSNP != "" and annotation != "":
        # DNP example -- COL6A6:uc010htl.1:exon4:c.1549_1550TT,
        DNPMatcher = re.match(
            "^([^:]+):([^\s:]+):([^\s:]+):c\.(\d+_\d+)([TCGA]+)(.*)", annotation)
        if DNPMatcher:
            transcript = DNPMatcher.group(2)
            cchange = DNPMatcher.group(4)
            translation = ""
            key = "%s,%s" % (mafLine, transcript)
            if key in mafline2proteinSeqMap:
                proteinSeqPosTuple = mafline2proteinSeqMap.get(key)
                proteinSeqStartLine = proteinSeqPosTuple[0]
                proteinSeqEndLine = proteinSeqPosTuple[1]
                for index in range(proteinSeqEndLine - proteinSeqStartLine + 1):
                    translation += linecache.getline(annovarNonSNP,
                                                     proteinSeqStartLine + index).rstrip("\n")
            pchange = getProteinChange(cchange, "", translation)
            cchange += DNPMatcher.group(5)
            newAnnotation = "%s:%s:%s:c.%s:p.%s%s" % (DNPMatcher.group(1), DNPMatcher.group(2), DNPMatcher.group(3),
                                                      cchange, pchange, DNPMatcher.group(6))

    return newAnnotation


def addProteinChanges(annovaroutput):
    nonSNPCodingChanges = annovaroutput + ".non_snp.protein_sequence"
    mafline2proteinSeqMap = loadNonSNPCodingChanges(nonSNPCodingChanges)

    tempUpdated = annovaroutput + "_temp"
    tempUpdatedHandle = open(tempUpdated, "w")

    annovaroutputHandle = open(annovaroutput, "r")
    for line in annovaroutputHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        mafLine = fields[0]
        annotations = fields[2]

        if annotations != "":
            annotationList = annotations.split(",")
            if len(annotationList) > 0:
                newAnnotations = ""
                # example single gene annotation from ANNOVAR:
                # AMPD1:uc001efe.1:exon7:c.C787T:p.R263C
                for annotation in annotationList:
                    transcriptMatcher = re.match(
                        "^([^:]+):([^\s:]+):(.*)", annotation)
                    if transcriptMatcher:
                        transcript = transcriptMatcher.group(2)
                        key = "%s,%s" % (mafLine, transcript)
                        # check and update transcripts accordingly
                        if key in mafline2proteinSeqMap:
                            # For now only DNP mutations are considered
                            newAnnotation = processDNP(
                                nonSNPCodingChanges, mafLine, annotation, mafline2proteinSeqMap)
                            if newAnnotation == "":
                                newAnnotation = annotation
                            newAnnotations += newAnnotation + ","

                if newAnnotations != "" and annotations != newAnnotations:
                    line = line.replace(annotations, newAnnotations)

        tempUpdatedHandle.write("%s\n" % (line))

    tempUpdatedHandle.close()
    annovaroutputHandle.close()

    shutil.move(tempUpdated, annovaroutput)


def update(annovaroutput):
    addProteinChanges(annovaroutput)
    addNormalNucleotides(annovaroutput)


def _mainFunc():
    try:
        annovaroutput = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-annovaroutput":
                annovaroutput = sys.argv[index + 1].strip()

        if annovaroutput == "":
            raise Exception("No ANNOVAR output file path presents!")

        update(annovaroutput)

    except Exception:
        traceback.print_exc()
        showHelp()


if __name__ == "__main__":
    _mainFunc()
