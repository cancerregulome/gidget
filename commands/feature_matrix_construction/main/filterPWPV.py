# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import math
import numpy
import random
import sys
import urllib

# these are my local modules
import miscIO
import path
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getLineInfo(aLine):

    lInfo = {}
    aTokens = aLine.split('\t')
    if (len(aTokens) < 1 or len(aTokens) > 3):
        if (1):
            print aLine
            print aLine.strip()
            print aTokens
            print len(aTokens)
            sys.exit(-1)
        return (lInfo)

    lInfo['TARG'] = {}
    lInfo['FEAT'] = {}
    bTarg = aTokens[0].split(',')
    bFeat = aTokens[1].split(',')
    if (len(aTokens) == 3):
        bFeat += aTokens[2].split(',')

    if (0):
        print bTarg
        print bFeat
        sys.exit(-1)

    for ii in range(len(bTarg)):
        cTmp = bTarg[ii].split('=')
        try:
            zVal = float(cTmp[1].strip())
            lInfo['TARG'][cTmp[0].strip()] = zVal
        except:
            try:
                lInfo['TARG'][cTmp[0].strip()] = cTmp[1].strip().upper()
            except:
                return ({})

    for ii in range(len(bFeat)):
        cTmp = bFeat[ii].split('=')
        try:
            zVal = float(cTmp[1].strip())
            lInfo['FEAT'][cTmp[0].strip()] = zVal
        except:
            try:
                lInfo['FEAT'][cTmp[0].strip()] = cTmp[1].strip().upper()
            except:
                return ({})

    if (0):
        print lInfo
        sys.exit(-1)

    return (lInfo)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCoordinates(aName):

    tokenList = aName.split(':')

    chrName = tokenList[3]
    startPos = -1
    endPos = -1
    try:
        startPos = int(tokenList[4])
        endPos = int(tokenList[5])
    except:
        doNothing = 1

    return (chrName, startPos, endPos)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def filterPWPV(pwpvOutFilename):

    print " "
    print " reading PWPV outputs from <%s> " % pwpvOutFilename
    fh = file(pwpvOutFilename, 'r')

    out0 = pwpvOutFilename + ".unmapd"
    out1 = pwpvOutFilename + ".mapped"

    fh0 = file(out0, 'w')
    fh1 = file(out1, 'w')

    n0 = 0
    n1 = 0

    # why didn't I put GNAB in this list ???
    # --> adding it to the list on 06sep12
    typeList = ["CNVR", "GEXP", "GNAB", "METH", "MIRN", "RPPA"]
    # --> taking it back out on 20sep12 ;-)
    typeList = ["CNVR", "GEXP", "METH", "MIRN", "RPPA"]

    typeCounts = {}

    for aLine in fh:

        # by default, we assume we will keep this line from the file
        keepLine = 1

        aLine = aLine.strip()
        tokenList = aLine.split('\t')

        # expected list of tokens for a PWPV pair :
        ## ['C:SAMP:miRNA_k5:::::', 'C:SAMP:miRNA_k7:::::', '0.398', '694', '-300.0', '1.7', '-300.0', '0', '0.0', '0', '0.0\n']
        if (len(tokenList) < 3):
            continue

        aType = tokenList[0][2:6]
        bType = tokenList[1][2:6]

        if (aType <= bType):
            aKey = (aType, bType)
        else:
            aKey = (bType, aType)

        if (aType in typeList):
            aTokens = tokenList[0].split(':')
            if (aTokens[3] == ""):
                keepLine = 0

        if (keepLine):
            if (bType in typeList):
                bTokens = tokenList[1].split(':')
                if (bTokens[3] == ""):
                    keepLine = 0

        if (keepLine):
            fh1.write("%s\n" % aLine)
            n1 += 1
        else:
            fh0.write("%s\n" % aLine)
            n0 += 1
            if (aKey not in typeCounts.keys()):
                typeCounts[aKey] = 0
            typeCounts[aKey] += 1

    fh.close()
    fh0.close()
    fh1.close()

    print " "
    print "     n1 = %9d    n0 = %9d " % (n1, n0)
    if ( (n1+n0) > 0 ):
        f1 = float(n1) / float(n1 + n0)
        f0 = float(n0) / float(n1 + n0)
        print "     f1 = %9.6f    f0 = %9.6f " % (f1, f0)
    print " "
    print typeCounts
    print " "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 2):
        print ' Usage : %s <pwpv results file> ' % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    pwpvOutFilename = sys.argv[1]

    filterPWPV(pwpvOutFilename)

    sys.exit(-1)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
