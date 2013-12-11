import sys
import traceback
import linecache
import shutil
import re
import updateMAF_addUniprotID
import updateMAF_addUniprotISO1

__author__ = 'xshu'


def showHelp():
    print\
    '''
    Prerequisite: This program MUST BE executed AFTER updateMAF_addUniprotID.py completes its job

    This program updates MAF by annotating protein changes. All parameters are required

    Usage: %s
            Parameter                                       Description
            -mafWithUniprotID                               MAF file with uniprot ids being added
            -knowngene2protein                              A mapping file between UCSC know genes and proteins
            -refseq2uniprot                                 A mapping file between refseq protein accession and uniprot protein accession
            -uniprot_sprot_human                            Uniprot Sprot human dat file
            -uniprot_trembl_human                           Uniprot Trembl human dat file
            -output                                         Output folder


            (eg. %s -mafWithUniprotID                       <<absolute MAF file carrying Uniprot IDs>>
                    -knowngene2protein                      <<absolute knowgenes to proteins mapping file path>>
                    -refseq2uniprot                         <<absolute path of the mapping file between refseq protein accession and uniprot protein accession>>
                    -uniprot_sprot_human                    <<absolute path of the Uniprot Sprot human dat file>>
                    -uniprot_trembl_human                   <<absolute path of the Uniprot Trembl human dat file>>
                    -output                                 <<absolute output folder path>> )

    ''' % (sys.argv[0], sys.argv[0])


def depeditate(string, suffix):
    x = len(suffix)
    if not x:
        return string
    if string[-x:] == suffix:
        return string[:-x]
    print >> sys.stderr, "failed depeditate:", string[-x:], "ain't", suffix
    return string


def loadTranscript2Uniprot(transcript2protein):
    result = {}

    transcript2proteinHandle = open(transcript2protein, "r")
    for line in transcript2proteinHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        knownGene = fields[0]
        protein = fields[1]

        updateMAF_addUniprotID.addItemsToMapping(knownGene, protein, result)
    transcript2proteinHandle.close()

    return result


def loadRefseq2Uniprot(refseq2uniprotFile):
    result = {}

    refseq2uniprotFileHandle = open(refseq2uniprotFile, "r")
    for line in refseq2uniprotFileHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        if len(fields) > 1:
            refseq = fields[0]
            uniprot = fields[1]
            updateMAF_addUniprotID.addItemsToMapping(refseq, uniprot, result)
    refseq2uniprotFileHandle.close()

    return result


def loadAnnovarExonicVariantOutput(annovarOutput):
    result = {}

    lineNo = 1
    annovarOutputHandle = open(annovarOutput, "r")
    for line in annovarOutputHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        mafLineNo = long(fields[0].lstrip("line"))
        updateMAF_addUniprotID.addItemsToMapping(mafLineNo, lineNo, result)
        lineNo += 1

    return result


def loadUniprotPrim2Sec(uniprot_human):
    result = {}

    # load uniprot_human file and build a map between primary and secondary
    # protein accession
    if uniprot_human != "":
        uniprot_humanHandle = open(uniprot_human, "r")

        lastID = ""
        currentID = ""
        curPrimaryAccession = ""
        curSecondaryAccessions = []

        for line in uniprot_humanHandle:
            line = line.rstrip("\n")

            idMatcher = re.match("^ID\s+([^\s]*)\s+(.*)", line)
            if idMatcher:
                currentID = idMatcher.group(1)

            if lastID != currentID and len(curSecondaryAccessions) > 0:
                result[curPrimaryAccession] = curSecondaryAccessions
                lastID = currentID
                curPrimaryAccession = ""
                curSecondaryAccessions = []

            acMatcher = re.match("^AC\s+(.*)", line)
            if acMatcher:
                accessions = acMatcher.group(1)
                if curPrimaryAccession == "":
                    curPrimaryAccession = accessions.split(";")[0]
                    accessions = re.sub(
                        "\s*", "", accessions[accessions.find(";") + 1:])
                curSecondaryAccessions.extend(accessions.split(";"))

        uniprot_humanHandle.close()

    return result


def loadReferencesForANNOVARExonicLevel(*refArgTup):
    knowngene2protein = refArgTup[0]
    refseq2uniprot = refArgTup[1]
    uniprot_sprot_human = refArgTup[2]
    uniprot_trembl_human = refArgTup[3]
    annovarExonicVariantOutput = refArgTup[4]

    knowngene2proteinMapping = loadTranscript2Uniprot(knowngene2protein)
    refseq2uniprotMapping = loadRefseq2Uniprot(refseq2uniprot)
    mafLine2annovarOutputLine = loadAnnovarExonicVariantOutput(
        annovarExonicVariantOutput)
    uniprotPrim2Sec = loadUniprotPrim2Sec(uniprot_sprot_human)
    uniprotPrim2Sec.update(loadUniprotPrim2Sec(uniprot_trembl_human))

    return knowngene2proteinMapping, refseq2uniprotMapping, mafLine2annovarOutputLine, uniprotPrim2Sec


def retriveNewAnnoations(*arguments):
    uniprotID = arguments[0]
    oldAnnotationStr = arguments[1]
    uniprotid2Isoform1Mapping = arguments[2]
    uniprot_isoform1 = arguments[3]

    resultMain = ""
    resultOthers = ""
    if oldAnnotationStr.strip() != "":
        oldAnnotations = oldAnnotationStr.split(",")
        for annotation in oldAnnotations:
            if annotation != "":
                sections = annotation.split(":")
                proteinChangePosStr = sections[len(sections) - 1]
                proteinChangePos = ""

                changedAminoAcidFromAnnovar = ""
                for char in proteinChangePosStr:
                    try:
                        int(char)
                        proteinChangePos += char
                    except ValueError:
                        if proteinChangePos == "":
                            changedAminoAcidFromAnnovar = char
                        continue

                if proteinChangePos != "":
                    proteinChangePos = long(proteinChangePos)
                    annotationMatched = True

                    if uniprotID in uniprotid2Isoform1Mapping:
                        posTuple = uniprotid2Isoform1Mapping.get(uniprotID)
                        startLine = posTuple[0]
                        endLine = posTuple[1]
                        isoform1Seq = ""
                        for step in range(0, endLine - startLine + 1):
                            isoform1Seq += linecache.getline(uniprot_isoform1,
                                                             startLine + step).rstrip("\n")

                        if len(isoform1Seq) >= proteinChangePos:
                            changedAminoAcidInIsoform1 = isoform1Seq[
                                proteinChangePos - 1]

                            if changedAminoAcidFromAnnovar == changedAminoAcidInIsoform1:
                                resultMain += annotation + ","
                            else:
                                annotationMatched = False
                        else:
                            annotationMatched = False
                    else:
                        annotationMatched = False

                    if not annotationMatched:
                        resultOthers += annotation + ","

    return resultMain, resultOthers


def updateOnSpecialVariantLevel(mafWithUniprotID, updatedMAF, *refArgTup):
    newlyAnnotatedLinesInMAF = []
    unAnnotatedLinesInMAF = refArgTup[0]
    annovarVariantOutput = refArgTup[1]

    updatedMAFHandle = open(updatedMAF, "a")
    annovarVariantOutputHandle = open(annovarVariantOutput, "r")
    for line in annovarVariantOutputHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        variantType = fields[0]
        gene = fields[1]
        chr = fields[2]
        mafLineNo = long(fields[3].lstrip("line"))

        if mafLineNo in unAnnotatedLinesInMAF:
            if mafLineNo not in newlyAnnotatedLinesInMAF:
                newlyAnnotatedLinesInMAF.append(mafLineNo)

            # mafWithUniprotID has a header line so need to account for this
            newmafLineNo = mafLineNo + 1
            originalMAFLine = linecache.getline(
                mafWithUniprotID, newmafLineNo).rstrip("\n")
            annovarInfo = "variant_type=" + variantType + \
                "|gene=" + gene + "|chromosome=" + chr
            updatedMAFHandle.write("%s\t%s\t%s\t%s\n" %
                                   (originalMAFLine, "", "", annovarInfo))
    annovarVariantOutputHandle.close()

    # for lines in the MAF that are still not annotated:
    # 1. append them to MAF
    # 2. print out lines
    lenFinalUnAnnotatedLines = len(
        unAnnotatedLinesInMAF) - len(newlyAnnotatedLinesInMAF)
    print ("%s %s %s %s %s %s\n\n" % ("Among", str(len(unAnnotatedLinesInMAF)), "records that are the \
Non-coding exonic levels (ncRNA, splicing, UTR5, UTR3, downstream, upstream, intronic and intergenic) there are",
                                      str(lenFinalUnAnnotatedLines), "records ANNOVAR cannot annotate for", mafWithUniprotID))

    if lenFinalUnAnnotatedLines > 0:
        for mafLineNo in unAnnotatedLinesInMAF:
            if mafLineNo not in newlyAnnotatedLinesInMAF:
                # mafWithUniprotID has a header line so need to account for
                # this
                newmafLineNo = mafLineNo + 1
                originalMAFLine = linecache.getline(
                    mafWithUniprotID, newmafLineNo)
                updatedMAFHandle.write(originalMAFLine)
                print ("%s%d\t%s" %
                       ("line", mafLineNo, linecache.getline(mafWithUniprotID, newmafLineNo).rstrip("\n")))
        print

    updatedMAFHandle.close()
    return updatedMAF


def filterNonIsoform1Entries(updatedMAF, uniprot_sprot_isoform1, uniprot_trembl_isoform1):
    unprotid2Isoform1Mapping = updateMAF_addUniprotISO1.loadID2ISOForm1(
        uniprot_sprot_isoform1)
    unprotid2Isoform1Mapping.update(
        updateMAF_addUniprotISO1.loadID2ISOForm1(uniprot_trembl_isoform1))

    updatedMAFTemp = updatedMAF + "_isoform1"
    updatedMAFTempHandler = open(updatedMAFTemp, "w")

    updatedMAFHandle = open(updatedMAF, "r")
    updatedMAFTempHandler.write(updatedMAFHandle.readline())

    for line in updatedMAFHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")
        lenFields = len(fields)

        uniprotIDList = []
        uniprot_isoform1 = ""
        sprotIDStr = fields[lenFields - 5]
        tremblIDStr = fields[lenFields - 4]
        if sprotIDStr != "":
            uniprotIDList = sprotIDStr.split(";")
            uniprot_isoform1 = uniprot_sprot_isoform1
        elif tremblIDStr != "":
            uniprotIDList = tremblIDStr.split(";")
            uniprot_isoform1 = uniprot_trembl_isoform1

        if len(uniprotIDList) == 0:
            updatedMAFTempHandler.write(line)
        else:
            newMainAnnotation = ""
            newOtherAnnotation = ""

            mainAnnotationStr = fields[lenFields - 3]
            otherAnnotationStr = fields[lenFields - 2]
            annovarNote = fields[lenFields - 1]

            for uniprotID in uniprotIDList:
                arguments = (uniprotID, mainAnnotationStr,
                             unprotid2Isoform1Mapping, uniprot_isoform1)
                resultMain, resultOthers = retriveNewAnnoations(*arguments)
                newMainAnnotation += resultMain
                newOtherAnnotation += resultOthers

                arguments = (uniprotID, otherAnnotationStr,
                             unprotid2Isoform1Mapping, uniprot_isoform1)
                resultMain, resultOthers = retriveNewAnnoations(*arguments)
                newMainAnnotation += resultMain
                newOtherAnnotation += resultOthers

            linePrefix = ""
            for index in range(lenFields):
                if index < lenFields - 3:
                    linePrefix += fields[index] + "\t"
            linePrefix = linePrefix[0:len(linePrefix) - 1]
            updatedMAFTempHandler.write("%s\t%s\t%s\t%s\n" % (
                linePrefix, newMainAnnotation, newOtherAnnotation, annovarNote))

    updatedMAFHandle.close()
    updatedMAFTempHandler.close()
    shutil.move(updatedMAFTemp, updatedMAF)

    return updatedMAF


def updateOnExonicLevel(mafWithUniprotID, output, *refArgTup):
    annovarExonicVariantOutput = refArgTup[4]

    # load references
    # todo: Memory is in an intensive use when the mappings are pre-loaded.
    # Check if PyTables can offer an alternative whenever possible
    knowngene2proteinMapping, refseq2uniprotMapping, mafLine2annovarOutputLine, uniprotPrim2Sec = loadReferencesForANNOVARExonicLevel(
        *refArgTup)

    # begin to update MAF
    mafWithUniprotIDHandle = open(mafWithUniprotID, "r")
    header = mafWithUniprotIDHandle.readline().rstrip("\n")
    numHeaders = header.count("\t") + 1

    if output.rfind("/") != len(output) - 1:
        output += "/"
    updatedMAF = output + \
        mafWithUniprotID[mafWithUniprotID.rfind("/") + 1:] + "_exonic"
    updatedMAFHandle = open(updatedMAF, "w")
    updatedMAFHandle.write("%s\t%s\t%s\t%s\n" % (
        header, "Mutation Annotation (uniprot isoform1)", "Mutation Annotation (Others)", "ANNOVAR"))

    lineNoWithoutHeader = 1
    unAnnotatedLines = []
    for line in mafWithUniprotIDHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")

        uniprotIDList = []
        sprotIDs = fields[numHeaders - 2]
        tremblIDs = fields[numHeaders - 1]
        if sprotIDs != "":
            uniprotIDList = sprotIDs.split(";")
        elif tremblIDs != "":
            uniprotIDList = tremblIDs.split(";")

        # collect the records that ANNOVAR cannot annotate on coding-exon level
        if lineNoWithoutHeader not in mafLine2annovarOutputLine and lineNoWithoutHeader not in unAnnotatedLines:
            unAnnotatedLines.append(lineNoWithoutHeader)
            lineNoWithoutHeader += 1
            continue

        # example annovar output line:
        # line1   nonsynonymous SNV
        # AMPD1:uc001efe.1:exon7:c.C787T:p.R263C,AMPD1:uc001eff.1:exon6:c.C775T:p.R259C,
        # 1       115023833       115023833       G       A       SNP
        annovarOutputLineNoList = mafLine2annovarOutputLine[
            lineNoWithoutHeader].split(";")
        numAnnovarLinesMappedToCurMAFLine = len(annovarOutputLineNoList)

        # Loop through each ANNOVAR output that associates with the current MAF line
        # ANNOVAR can have several lines of output for one single MAF record. When this happens for each ANNOVAR output
        # we list the variant type found by ANNOVAR
        for annovarOutputLineNo in annovarOutputLineNoList:
            annovarOutputLine = linecache.getline(
                annovarExonicVariantOutput, long(annovarOutputLineNo)).rstrip("\n")
            annovarOutputFields = annovarOutputLine.split("\t")
            variantType = annovarOutputFields[1]
            geneAnnotation = annovarOutputFields[2]

            # example gene annotations from ANNOVAR:
            # AMPD1:uc001efe.1:exon7:c.C787T:p.R263C,AMPD1:uc001eff.1:exon6:c.C775T:p.R259C,
            annotations = geneAnnotation.split(",")
            mainAnnotation = ""
            otherAnnotation = ""
            # a flag indicating if the current annotation matches any uniprot
            # accession or not
            curAnnotationMatched = False

            # look up and then save the mapping between a uniprot accession and
            # the first transcript found that maps to the uniprot accession
            for annotation in annotations:
                if annotation == "":
                    continue

                # example single gene annotation from ANNOVAR:
                # AMPD1:uc001efe.1:exon7:c.C787T:p.R263C
                knowngene = annotation.split(":")[0]
                if knowngene in knowngene2proteinMapping:
                    proteinForCurKnowngene = knowngene2proteinMapping[
                        knowngene]

                    for uniprotID in uniprotIDList:
                        # knowgene2protein example: uc001jss.1  Q8N9N2-2
                        # refseq2uniprot example: NP_001185727  Q8N9N2
                        # NOTE:
                        # 1. One uniprot protein can map to multiple transcripts(knowngenes) here we catch the first one
                        # 2. In knowngene table a transcript can map to a
                        # secondary, NOT the primary uniprot protein accession
                        if proteinForCurKnowngene == uniprotID or \
                           (proteinForCurKnowngene in refseq2uniprotMapping and refseq2uniprotMapping[proteinForCurKnowngene].find(uniprotID) != -1) or \
                           (uniprotID in uniprotPrim2Sec and proteinForCurKnowngene in uniprotPrim2Sec[uniprotID]):
                            mainAnnotation += annotation + ","
                            curAnnotationMatched = True

                # put aside any annotations that either do not match any
                # uniprot accessions or are not used
                if not curAnnotationMatched:
                    otherAnnotation += annotation + ","
                else:
                    curAnnotationMatched = False

            updatedMAFHandle.write("%s\t%s\t%s" %
                                   (line, mainAnnotation, otherAnnotation))
            if numAnnovarLinesMappedToCurMAFLine > 1:
                updatedMAFHandle.write("\t%s%s" %
                                       ("variant_type=", variantType))
            else:
                updatedMAFHandle.write("\t")
            updatedMAFHandle.write("\n")

        lineNoWithoutHeader += 1

    updatedMAFHandle.close()
    mafWithUniprotIDHandle.close()

    print ("%s %s %s %s\n\n" % ("There are", str(len(unAnnotatedLines)), "records that are on Non-coding exonic levels \
(ncRNA, splicing, UTR5, UTR3, downstream, upstream, intronic and intergenic) in ", mafWithUniprotID))

    return updatedMAF, unAnnotatedLines


def _mainFunc():
    try:
        mafWithUniprotID = ""
        knowngene2protein = ""
        refseq2uniprot = ""
        uniprot_sprot_human = ""
        uniprot_trembl_human = ""
        uniprot_sprot_isoform1 = ""
        uniprot_trembl_isoform1 = ""
        output = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-mafWithUniprotID":
                mafWithUniprotID = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-knowngene2protein":
                knowngene2protein = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-refseq2uniprot":
                refseq2uniprot = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_sprot_human":
                uniprot_sprot_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_trembl_human":
                uniprot_trembl_human = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_sprot_isoform1":
                uniprot_sprot_isoform1 = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-uniprot_trembl_isoform1":
                uniprot_trembl_isoform1 = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if mafWithUniprotID == "" or \
           knowngene2protein == "" or refseq2uniprot == "" or \
           uniprot_sprot_human == "" or uniprot_trembl_human == "" or \
           uniprot_sprot_isoform1 == "" or uniprot_trembl_isoform1 == "" or \
           output == "":
            raise Exception("All parameters are required!")

        # update MAF with ANNOVAR exonic variant output
        # XXX Oh god it's a hidden second-degree sacred filename
        # XXX FFFFFFFFFFFFFFFFFFFUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
        annovarExonicVariantOutput = depeditate(
            mafWithUniprotID, ".with_uniprot") + ".annovar_exonic_variant_function"
        refArgTup = (knowngene2protein, refseq2uniprot, uniprot_sprot_human,
                     uniprot_trembl_human, annovarExonicVariantOutput)
        updatedMAF, unAnnotatedLinesInMAF = updateOnExonicLevel(
            mafWithUniprotID, output, *refArgTup)

        # only keep the protein changes that correspond to isoform1 sequences
        #updatedMAF = filterNonIsoform1Entries(updatedMAF, uniprot_sprot_isoform1, uniprot_trembl_isoform1)

        # update MAF with ANNOVAR special events output
        if len(unAnnotatedLinesInMAF) > 0:
            annovarVariantOutput = depeditate(
                mafWithUniprotID, ".with_uniprot") + ".annovar_variant_function"
            refArgTup = (unAnnotatedLinesInMAF, annovarVariantOutput)
            updatedMAF = updateOnSpecialVariantLevel(
                mafWithUniprotID, updatedMAF, *refArgTup)

        shutil.move(updatedMAF, mafWithUniprotID)

    except Exception:
        traceback.print_exc()
        showHelp()


if __name__ == "__main__":
    _mainFunc()
