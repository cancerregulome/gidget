# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys

from env import gidgetConfigVars
import miscTCGA
import path
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getListName(fName, tumorString):

    i1 = len(fName) - 1
    while (fName[i1] != '/'):
        i1 -= 1

    s1 = fName[i1 + 1:]
    s2 = s1[:-8]
    # print s1, s2

    s3 = s2.lower()
    s4 = tumorString.lower()

    if (s3.startswith(s4)):
        s2 = s2[len(s4):]
        if (s2[0] == '-'):
            s2 = s2[1:]
        # print s2

    return (s2)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getSampleList(fName):

    sList = []

    fh = file(fName)
    for aLine in fh:
        aLine = aLine.strip()
        aLine = aLine.upper()
        if (not aLine.startswith("TCGA-")):
            continue
        # print aLine
        if aLine not in sList:
            sList += [aLine]

    sList.sort()
    return (sList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if ( (len(sys.argv)==3) or (len(sys.argv)==4) ):
            tumorString = sys.argv[1]
            dateString = sys.argv[2]
            if ( len(sys.argv) == 4 ):
                auxName = sys.argv[3]
            else:
                auxName = "aux"
        else:
            print " "
            print " Usage: %s <tumorString> <dateString> [auxName] "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

    print " "
    print " Running : %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2])
    print " "
    print " "

    listDict = {}

    # find all of the .ids.txt files and build up the various named lists ...
    topDir = "%s/%s/%s" % (gidgetConfigVars['TCGAFMP_DATA_DIR'], tumorString, dateString)
    d1 = path.path(topDir)
    for f1 in d1.files():
        if (f1.endswith(".ids.txt")):
            print " "
            print f1
            listName = getListName(f1, tumorString)
            print listName
            listDict[listName] = getSampleList(f1)
            print len(listDict[listName])

    listNames = listDict.keys()
    listNames.sort()

    # now create a union list
    uList = []
    for aName in listNames:
        for aSample in listDict[aName]:
            if (aSample not in uList):
                uList += [aSample]

    uList.sort()
    print " "
    print len(uList)

    # ok and now we can write out the indicator features ...
    outFile = "%s/%s/$s/namedLists.forXmlMerge.tsv" % ( gidgetConfigVars['TCGAFMP_DATA_DIR'], tumorString, auxName )
    fh = file(outFile, 'w')

    outLine = "bcr_patient_barcode"
    for aName in listNames:
        outLine += "\tB:SAMP:I(%s)" % aName
    outLine += "\n"
    fh.write(outLine)

    for aSample in uList:
        outLine = aSample
        for aName in listNames:
            outLine += "\t%d" % (int(aSample in listDict[aName]))
        outLine += "\n"
        fh.write(outLine)

    fh.close()


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
