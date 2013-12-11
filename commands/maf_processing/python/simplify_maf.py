import sys
import tsv
import csv
import optparse

NCBI_BUILD_LUT = {
    "36": "hg18",
    "37": "hg19",
}

TABLE_SCHEMA = [
    "Chromosome",
    ["Start_Position", "Start_position"],
    ["End_Position", "End_position"],
    "Reference_Allele",
    "Tumor_Seq_Allele2",
    "LineNo",
    "Hugo_Symbol",
    "Entrez_Gene_Id",
    "Variant_Type",
    "Tumor_Seq_Allele1"
]

# Must be aligned with LineNo, which has no real backing column
LINENUM_INDEX = 5


def main(argv):
    if len(argv) != 4:
        raise Exception(
            "Wrong number of arguments. Usage: input output buildID-file")
    inPath = argv[1]
    outPath = argv[2]
    buildIdPath = argv[3]

    build_number = None

    inFile = open(inPath, "rb")
    try:
        table = tsv.TsvReader(inFile, TABLE_SCHEMA)
    except csv.Error:
        print "Warning: ragged table. Assuming excel_tab and correcting"
        inFile.close()
        inFile = open(inPath, "rb")
        outPath = inPath + ".fixed_raggedness"
        outFile = open(outPath, "wb")
        tsv.fixRaggedTable(inFile, outFile, csv.excel_tab)
        outFile.flush()
        outFile.close()
        del outFile
        inFile = open(outPath)
        try:
            table = tsv.TsvReader(inFile, TABLE_SCHEMA)
        except:
            print "Well, that didn't work"
            raise
    # end handler for ragged table

    line = 0
    output = open(outPath, "w")
    for record in table:
        line += 1
        bNum = record["NCBI_Build"]
        if (build_number is not None) and (bNum != build_number):
            raise Exception(
                "Inconsistent NCBI_Build values; cleave table first")
        build_number = bNum

        # TSV rows can't be written into, only read. thus...
        writableRecord = [cell for cell in record]
        writableRecord[LINENUM_INDEX] = "line" + str(line)

        output.write("\t".join(writableRecord))
        output.write("\n")

    output.flush()
    output.close()
    del output

    buildIdOut = open(buildIdPath, "w")
    buildIdOut.write(NCBI_BUILD_LUT[build_number])
    buildIdOut.flush()
    buildIdOut.close()
    del buildIdOut
    return 0

if __name__ == "__main__":
    main(sys.argv)
