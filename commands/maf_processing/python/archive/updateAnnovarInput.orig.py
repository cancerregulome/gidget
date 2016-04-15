import shutil
import sys
import traceback

__author__ = 'xshu'


def showHelp():
    print\
    '''
    Prerequisite: This program MUST BE executed after updateMAF_addUniprotID.py completes its job

    This program prepares the input that ANNOVAR recognizes (see http://www.openbioinformatics.org/annovar/)

    Usage: %s
            Parameter                   Description
            -input                      A file containing extracted columns from MAF (Chr, Start Pos, End Pos, Variant Type, Ref Allele, Tumor Allele 2)
            -output                     Output folder

            (eg. %s -input    <<absolute data file containing a list of extracted fields from a maf file>>
                    -output   <<absolute output folder path>> )

    ''' % (sys.argv[0], sys.argv[0])


def update(input, output):
    if output.rfind("/") != len(output) - 1:
        output += "/"
    tempOutput = output + input[input.rfind("/") + 1:] + "_temp"
    tempOutputHandle = open(tempOutput, "w")

    inputHandle = open(input, "r")
    for line in inputHandle:
        line = line.rstrip("\n")
        fields = line.split("\t")

        chr = fields[0]
        startPos = fields[1]
        endPos = fields[2]
        refAllele = fields[3]
        tumorAllele2 = fields[4]
        lineNo = fields[5]
        variantType = fields[8]
        tumorAllele1 = fields[9]
        if variantType == "INS":
            startPos = endPos
            if tumorAllele2 == "-":
                tumorAllele2 = tumorAllele1
        tempOutputHandle.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
                               (chr, startPos, endPos, refAllele, tumorAllele2, lineNo, variantType))
    inputHandle.close()

    shutil.move(tempOutput, input)


def _mainFunc():
    try:
        input = ""
        output = ""

        for index in range(len(sys.argv)):
            if sys.argv[index] == "-input":
                input = sys.argv[index + 1].strip()
            elif sys.argv[index] == "-output":
                output = sys.argv[index + 1].strip()

        if input == "" or output == "":
            raise Exception("All parameters are required!")

        update(input, output)

    except Exception:
        traceback.print_exc()
        showHelp()


if __name__ == "__main__":
    _mainFunc()
