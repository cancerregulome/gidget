# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscIO
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtHeaderTokens(aTokens):

    patientList = []
    typeDict = {}

    for a in aTokens:
        a = a.lower()
        if (a.startswith("tcga-")):
            patientID = a[8:12]
            if (patientID not in patientList):
                patientList += [patientID]
            if (len(a) >= 15):
                typeID = a[13:15]
                if (typeID not in typeDict.keys()):
                    typeDict[typeID] = 0
                typeDict[typeID] += 1
            else:
                print " WARNING : no typeID ??? <%s> " % a

    if (len(patientList) > 0):
        print " "
        print " # of unique patients : ", len(patientList)
        print " sample type counts   : ", typeDict
        print " "
        print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def lookAtLine(aLine):

    if (1):
        print len(aLine)

        numTab = 0
        numLF = 0
        numCR = 0
        numSpace = 0
        numDigit = 0
        numLetter = 0

        numLinesOut = 0

        i1 = 0
        for ii in range(len(aLine)):
            ordVal = ord(aLine[ii])
            if (1):
                if (ordVal == 9):
                    # this is a tab ...
                    numTab += 1
                elif (ordVal == 10):
                    numLF += 1
                elif (ordVal == 13):
                    numCR += 1
                elif (ordVal == 32):
                    numSpace += 1
                elif ((ordVal >= 48 and ordVal <= 57) or (ordVal == 46)):
                    numDigit += 1
                elif ((ordVal >= 65 and ordVal <= 90) or (ordVal >= 97 and ordVal <= 122)):
                    numLetter += 1
                elif (ordVal < 32 or ordVal > 126):
                    print " %6d     %3d " % (ii, ordVal)
                else:

                    # print " %6d <%s> %3d " % ( ii, aLine[ii], ord ( aLine[ii]
                    # ) )
                    doNothing = 1
            if (ordVal == 13):
                i2 = ii
                # print " --> writing out from %d to %d " % ( i1, i2 )
                # print " <%s> " % aLine[i1:i2]
                numLinesOut += 1
                ## if ( numLinesOut == 5 ): sys.exit(-1)
                ## fhOut.write ( "%s\n" % aLine[i1:i2] )
                i1 = i2 + 1

        print numTab, numLF, numCR, numSpace, numDigit, numLetter
        print numLinesOut

    sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print ' Usage : %s <input TSV> <output TSV> ' % sys.argv[0]
        print " ERROR -- bad command line arguments "
        sys.exit(-1)

    inFilename = sys.argv[1]
    outFilename = sys.argv[2]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    fhIn = file(inFilename)
    numLines = 10
    for iLine in range(numLines):

        aLine = fhIn.readline()
        # look for carriage return / line-feed ?
        ## lookAtLine ( aLine )

        ## aLine = aLine.strip()
        aTokens = aLine.split('\t')
        if (len(aTokens) > 15):
            print len(aTokens), aTokens[:5], aTokens[-5:]
        else:
            print len(aTokens), aTokens

    numLines = miscIO.num_lines(fhIn)
    print "\n\n total # of lines in file : %d " % numLines
    fhIn.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    fhIn = file(inFilename)
    aLine = fhIn.readline()
    aTokens = aLine.split('\t')
    numA = len(aTokens)
    print " number of header tokens : ", numA
    lookAtHeaderTokens(aTokens)

    done = 0
    iLine = 0
    numBlank = 0
    while not done:
        bLine = fhIn.readline()
        ## bLine = bLine.strip()
        iLine += 1
        # print bLine
        bTokens = bLine.split('\t')
        # print len(bTokens), bTokens
        numB = len(bTokens)
        if (numB < 2):
            done = 1
            continue
        if (numA != numB):
            print "     wrong number of tokens ??? ", numB, numA, iLine
            print bTokens[:5]
            # print bLine[:100]
            sys.exit(-1)
        for ii in range(numA):
            if (bTokens[ii] == ''):
                # print "     blank token ??? ", ii, numA
                # print bTokens[:5], bTokens[ii]
                numBlank += 1
                # print bLine[:100]
                # sys.exit(-1)
    fhIn.close()

    print " number of blank tokens : ", numBlank

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print " "
    print " opening input file <%s> " % inFilename
    print " opening output file <%s> " % outFilename
    fhIn = file(inFilename, 'r')
    fhOut = file(outFilename, 'w')

    minFval = 999999.
    maxFval = -999999.

    iLine = 0
    for aLine in fhIn:
        aTokens = aLine.split('\t')
        numT = len(aTokens)
        if (iLine == 0):
            keepNum = numT
        else:
            if (numT != keepNum):
                print " different number of tokens ??? ", numT, keepNum
        iLine += 1

        outLine = ''
        for ii in range(numT):
            if (len(outLine) > 1):
                outLine += '\t'
            tmpToken = aTokens[ii].strip()
            if (tmpToken == ''):
                outLine += 'NA'
            else:
                try:
                    fVal = float(tmpToken)
                    if (fVal < minFval):
                        minFval = fVal
                    if (fVal > maxFval):
                        maxFval = fVal
                except:
                    doNothing = 1
                outLine += tmpToken
        fhOut.write("%s\n" % outLine)

    print " "
    print iLine
    print minFval, maxFval
    print " "
    print " "

    fhIn.close()
    fhOut.close()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
