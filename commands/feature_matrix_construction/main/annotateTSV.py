# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# these are system modules
import sys

# these are my local ones
from env import gidgetConfigVars
import chrArms
import refData
import tsvIO

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# this function looks for the gene or genes that overlap the segment defined
# by the input 'curRowLabel' coordinates


def overlap(curRowLabel, GAF_geneCoordDict_bySymbol):

    tokenList = curRowLabel.split(':')
    geneList = []

    if (tokenList[3] != ''):

        # first try to parse out genomic coordinates from
        # the current row label ... it is possible that
        # the row label does not have coordinates
        try:
            chrName = tokenList[3]
            chrStart = int(tokenList[4])
            chrStop = int(tokenList[5])
            # print chrName, chrStart, chrStop
        except:
            return ([])

        # if we get here, then we have coordinates so we now
        # loop over the genes in our GAF_geneCoordDict_bySymbol and look for
        # any that overlap ...
        for aGene in GAF_geneCoordDict_bySymbol:

            # if this gene is not even on the same chromosome we're done ...
            if (not GAF_geneCoordDict_bySymbol[aGene].startswith(chrName + ':')):
                continue

            # but if it is, then we need to check start/stop
            posInfo = refData.parseCoordinates(GAF_geneCoordDict_bySymbol[aGene])
            if (chrStop < posInfo[1]):
                continue
            if (chrStart > posInfo[2]):
                continue
            # print posInfo

            # there seem to be some "bad" gene names ???
            if (aGene == '?'):
                continue

            if (len(aGene) == 1):
                print " how is this happening ??? "
                print curRowLabel, aGene, GAF_geneCoordDict_bySymbol[aGene]
                sys.exit(-1)

            geneList += [aGene]

        if (len(geneList) > 0):
            if (0):
                if (len(geneList) > 1):
                    print " got multiple genes ... ", geneList, tokenList
            return (geneList)
        else:
            # print " in overlap ... nada? ", curRowLabel
            return ([])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def stripLastNameFromDir(d1Name):

    ii = len(d1Name) - 1
    while (d1Name[ii] != '/'):
        ii -= 1
    tumorType = d1Name[ii + 1:]
    return (tumorType)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def read_pairs_from_file(SLpairsFile):

    genePairs = []
    fh = file(SLpairsFile)
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split()
        if (len(tokenList) != 2):
            continue
        if (tokenList[0] == tokenList[1]):
            continue

        if (tokenList[0] < tokenList[1]):
            curPair = (tokenList[0], tokenList[1])
        else:
            curPair = (tokenList[1], tokenList[0])

        if (curPair not in genePairs):
            genePairs += [curPair]

    return (genePairs)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def lookAtDict(pairAssocDict):

    print " "
    print " "
    print " in lookAtDict ... ", len(pairAssocDict)

    keyList = pairAssocDict.keys()
    keyList.sort()
    # print keyList[:5]
    # print keyList[-5:]

    maxCount = 0
    maxKeys = []

    for aKey in keyList:
        # print aKey, len(pairAssocDict[aKey])
        # print pairAssocDict[aKey]

        typeCounts = {}
        for aTuple in pairAssocDict[aKey]:
            aType = (aTuple[0], aTuple[1])
            if (aType not in typeCounts):
                typeCounts[aType] = 0
            typeCounts[aType] += 1
        curCount = len(pairAssocDict[aKey])

        if (0):
            if (curCount > 3):
                print curCount, aKey, typeCounts

        # write out the number of types of associations, then pair, and then
        # the typeCounts
        print len(typeCounts), aKey, typeCounts

        if (curCount > maxCount):
            maxCount = curCount
            maxKeys = [aKey]
        elif (curCount == maxCount):
            maxKeys += [aKey]

    if (0):
        # so, at first I was looking at the number of associations, but that
        # really depends mostly on the # of different features and in particular
        # there could be a lot of GNAB or CNVR or METH features for one gene
        # and only one of each for another ...

        print " "
        print " keys with the most associations: ", maxCount
        for aKey in maxKeys:
            typeCounts = {}
            for aTuple in pairAssocDict[aKey]:
                aType = (aTuple[0], aTuple[1])
                if (aType not in typeCounts):
                    typeCounts[aType] = 0
                typeCounts[aType] += 1
            curCount = len(pairAssocDict[aKey])

            print curCount, aKey, typeCounts

        print " "
        print " keys with at least %d associations: " % (maxCount / 2)
        for aKey in keyList:
            typeCounts = {}
            for aTuple in pairAssocDict[aKey]:
                aType = (aTuple[0], aTuple[1])
                if (aType not in typeCounts):
                    typeCounts[aType] = 0
                typeCounts[aType] += 1
            curCount = len(pairAssocDict[aKey])

            if (curCount >= (maxCount / 2)):
                print curCount, aKey, typeCounts

    print " "
    print " "


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def hasSpecialChar(aName):

    if (aName.find(":") >= 0):
        return (1)
    if (aName.find("?") >= 0):
        return (1)
    if (aName.find("'") >= 0):
        return (1)
    if (aName.find("|") >= 0):
        return (1)

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# curLabel : N:RPPA:ACACA:::::ACC1-R-C
# curGene  : ACACA
# posInfo  : chr17:32516040-32841015:-


def annotateLabel(curLabel, curGene, posString):

    print " in annotateLabel ... "
    print curLabel
    print curGene
    print posString

    i1 = posString.find(":")
    i2 = posString.find("-", i1 + 1)
    i3 = posString.find(":", i1 + 1)

    chrName = posString[:i1].lower()
    if (chrName.endswith('x')):
        chrName = chrName[:-1] + "X"
    elif (chrName.endswith('y')):
        chrName = chrName[:-1] + "Y"

    iStart = int(posString[i1 + 1:i2])
    iStop = int(posString[i2 + 1:i3])
    aStrand = posString[-1]

    # print chrName, iStart, iStop, aStrand

    if (0):
        # before, we were assuming that the gene name did not change ...
        i1 = curLabel.find(":", 7)
        newLabel = curLabel[:i1] + ":" + chrName + ":" + \
            str(iStart) + ":" + str(iStop) + \
            ":" + aStrand + curLabel[(i1 + 4):]
    else:
        # but now we are allowing for the incoming curGene to be a new symbol ...
        # print curLabel
        tokenList = curLabel.split(':')
        newLabel = tokenList[0]
        newLabel += ":" + tokenList[1]
        newLabel += ":" + curGene
        newLabel += ":" + chrName + ":" + \
            str(iStart) + ":" + str(iStop) + ":" + aStrand
        if (len(tokenList) > 7):
            newLabel += ":" + tokenList[7]
        # print newLabel
        if (len(tokenList) > 8):
            print " ERROR ??? too many tokens ??? "
            print curLabel
            print len(tokenList), tokenList
            print newLabel
            sys.exit(-1)

    print " --> newLabel : ", newLabel
    return (newLabel)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCytobandLabel(curLabel, cytoDict):

    tokenList = curLabel.split(':')
    chrName = tokenList[3].lower()
    if (not chrName.startswith("chr")):
        print " chrName does not start with chr ??? ", chrName
        sys.exit(-1)
        return ("")

    try:
        iStart = int(tokenList[4])
        if (tokenList[5] != ''):
            iStop = int(tokenList[5])
        else:
            iStop = iStart

        # print chrName, iStart, iStop
        # print cytoDict[chrName]

        tList = []
        oList = []
        for aTuple in cytoDict[chrName]:
            if (aTuple[1] > iStop):
                continue
            if (aTuple[2] < iStart):
                continue
            tList += [aTuple[0]]

            oLap = min(aTuple[2], iStop) - max(aTuple[1], iStart) + 1
            oList += [oLap]

    except:
        print " failed to find cytoband ??? ", curLabel
        print cytoDict.keys()
        print cytoDict[chrName]
        sys.exit(-1)
        return ("")

    if (0):
        print " "
        print " curLabel : ", curLabel
        print " tList : ", tList
        print " oList : ", oList

    if (len(tList) == 0):
        print " why didn't we find any cytobands ??? "
        print cytoDict.keys()
        print cytoDict[chrName]
        return ("")

    # print len(tList), tList, oList
    if (len(tList) == 1):
        cbName = tList[0]
        if (chrName.startswith("chr")):
            # tack on the chromosome # before returning ...
            if ( chrName[3].lower() == "x" ):
                cbName = "X" + cbName
            elif ( chrName[3].lower() == "y" ):
                cbName = "Y" + cbName
            else:
                cbName = chrName[3:] + cbName
            return (cbName)
        else:
            print " ERROR ??? ", chrName, cbName
            sys.exit(-1)

    # if we have more than one label, then we need to find the
    # shortest common substring ...
    cbName = ""
    minLen = len(tList[0])
    for aName in tList:
        if (minLen > len(aName)):
            minLen = len(aName)
    done = 0
    ii = 0
    while not done:
        sameFlag = 1
        for aName in tList:
            if (aName[ii] != tList[0][ii]):
                sameFlag = 0
                done = 1
        if (sameFlag):
            cbName += aName[ii]
        ii += 1
        if (ii >= minLen):
            done = 1

    if (len(cbName) > 1):
        if (cbName[-1] == '.'):
            cbName = cbName[:-1]
        ## elif (cbName.find('.') > 0):
        ##     print " CHECK THIS : ", cbName, tList
        ## elif (cbName.find('.') < 0):
        ##     print " AND THIS TOO : ", cbName, tList, len(cbName)

    # print " --> cbName : ", cbName
    if (len(cbName) < 3):
        # or if that didn't work well, then choose the one
        # cytoband with the largest overlap ...
        # FIXME: OR, we could just go down to 'p' or 'q' ???
        #        OR, if there is a list of several, try to remove one and 
        #            then look again for the common substring?
        maxOlap = 0
        for ii in range(len(tList)):
            if (maxOlap < oList[ii]):
                maxOlap = oList[ii]
                cbName = tList[ii]
        ## print "     SWITCHING TO: ", cbName, maxOlap

    if (chrName.startswith("chr")):
        # tack on the chromosome # before returning ...
        if ( chrName[3].lower() == "x" ):
            cbName = "X" + cbName
        elif ( chrName[3].lower() == "y" ):
            cbName = "Y" + cbName
        else:
            cbName = chrName[3:] + cbName
        return (cbName)
    else:
        print " ERROR ??? ", chrName, cbName
        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def hackMicroRNAname(oldName):

    if (not oldName.startswith("HSA-MIR-")):
        return (oldName)

    newName = "HSA-MIR-"
    i1 = 8
    i2 = oldName.find("-", i1)
    if (i2 < 0):
        i2 = len(oldName)
    try:
        iNum = int(oldName[i1:i2])
    except:
        return (oldName)

    newName = newName + ("%d" % iNum) + "A"
    if (i2 < len(oldName)):
        newName = newName + oldName[i2:]

    print " in hackMicroRNAname ... <%s> <%s> " % (oldName, newName)
    return (newName)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def chooseBestName(curGene, curID, curType, geneInfoDict, synMapDict, GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID):

    # we are missing a few dozen microRNAs ...
    if (curType == "MIRN"):
        if (curGene not in GAF_geneCoordDict_bySymbol):
            print " MIRN <%s> not found " % curGene
            tstGene = hackMicroRNAname(curGene)
            if (tstGene in GAF_geneCoordDict_bySymbol):
                print "     --> returning <%s> " % tstGene
                return (tstGene)
            else:
                print "     --> still not found ... oh well ... "
                return (curGene)

    # this approach does not seem to be a good idea ... it is resulting
    # in duplicate feature names, for example, the RNAseq data has
    # the gene ABCD1 and then later has AMN which seems to be a synonym
    # for ABCD1 ... so at this point we are ONLY changing the MIRN names
    if (0):
        return (curGene)

    # ---- obsolete ---- ##
    # trying to reinstate this in Jan 2013 ##

    # we default to the current gene name ... but it might get changed ...
    newGene = curGene

    # for now, we will not change the names of microRNAs ...
    if (curType == "MIRN"):
        return (newGene)

    # if this gene appears to be an "official" gene symbol, then keep it ...
    if (curGene in geneInfoDict):
        return (curGene)

    # otherwise go looking in the synonyms ...
    if (curGene in synMapDict):
        print " QQ  this gene name appears to be a synonym ??? ", curGene, curID
        print curGene, synMapDict[curGene]
        if (len(synMapDict[curGene]) == 1):
            aTuple = synMapDict[curGene][0]
            aGene = aTuple[0]
            aID = aTuple[1]
            if (str(aID) == str(curID)):
                print " QQ  --> changing name to <%s> " % synMapDict[curGene][0][0]
                newGene = synMapDict[curGene][0][0]
                if (newGene not in GAF_geneCoordDict_bySymbol):
                    print " QQ  BUT the new name is not in the GAF file ??? "
                    if (curGene in GAF_geneCoordDict_bySymbol):
                        print " QQ  --> so changing back ... "
                        newGene = curGene
                    else:
                        print " QQ  --> but neither is the old one, so going with new "
                        doNothing = 1
            else:
                print " QQ  --> but the ID of the only associated gene does not match ??? <%s> <%s> <%s> <%s> " % \
                    (curGene, curID, aGene, aID)
                print " QQ      <%s> <%s> " % (str(aID), str(curID))
                doNothing = 1

        else:

            # first see if we can find a matching ID ...
            foundMatchingID = 0
            for aTuple in synMapDict[curGene]:
                aGene = aTuple[0]
                aID = aTuple[1]
                if (str(aID) == str(curID)):
                    newGene = aGene
                    print " QQ  found matching ID !!! ", aTuple
                    foundMatchingID = 1

            if (not foundMatchingID):
                print " QQ  now what ??? ", synMapDict[curGene]
                lowNum = 999999999
                lowGene = ''
                for aTuple in synMapDict[curGene]:
                    aGene = aTuple[0]
                    if (aGene in GAF_geneCoordDict_bySymbol):
                        print " QQ  this one is in the GAF file ... ", aTuple
                        if (aTuple[1] < lowNum):
                            lowNum = aTuple[1]
                            lowGene = aTuple[0]
                print " QQ  --> going with this one: ", lowGene
                newGene = lowGene
                # sys.exit(-1)

    return (newGene)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def annotateFeatures ( dataD, geneInfoDict, synMapDict, \
        Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID, \
        GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID, \
        refGeneDict, cytoDict, forceFlag, nameChangeFlag ):

    print " "
    print " in annotateFeatures ... "

    # the GAF_geneCoordDict_bySymbol has keys that are gene names, eg 'AAGAB', 'TP53', etc
    # and the contents are the coordinates
    # print len(GAF_geneCoordDict_bySymbol)

    # similarly, the GAF_geneCoordDict_byID has keys that are gene IDs, eg '7157' or '8225',
    # etc and the contents are the coordinates

    # the new addition here (19dec12) is the GAF_geneSymbol_byID which may be used to
    # 'update' the gene symbol if it appears to be out of date ...

    # and as of now (17jan14) the same dictionaries exist based on the Gencode database

    # and the feature matrix has thousands of features x hundreds of patients
    try:
        numRow = len(dataD['rowLabels'])
        numCol = len(dataD['colLabels'])
        rowLabels = dataD['rowLabels']
        print " %d rows x %d columns " % (numRow, numCol)
        # print rowLabels[:5]
        # print rowLabels[-5:]
    except:
        print " ERROR in annotateFeatures ??? bad data ??? "
        return (dataD)

    # first create a loop of all of the gene names (for GEXP features)
    curGeneSymbols = []
    dupList = []
    numDup = 0
    for iRow in range(numRow):
        curLabel = rowLabels[iRow]
        curType = curLabel[2:6]
        if (curType == "GEXP"):
            tokenList = curLabel.split(':')
            curGene = tokenList[2]
            if (curGene not in curGeneSymbols):
                curGeneSymbols += [curGene]
            else:
                if ( curGene not in dupList ):
                    print " how can this be ??? duplicate gene labels ??? ", curGene
                    # sys.exit(-1)
                    numDup += 1
                    dupList += [curGene]

    if ( 0 ):
        ## the RNAseqV2 pipeline has SLC35E2 repeated ...
        if ( "SLC35E2" in dupList ):
            if ( numDup == 1 ):
                curGeneSymbols += [ "SLC35E2B" ]
                numDup = 0
                dupList = []
                print " --> the only duplicated gene symbol (SLC35E2) will be handled explicitly ... "
            else:
                print " "
                print " WARNING !!! DUPLICATE gene symbols coming in !!! ", numDup
                print dupList
                print " "
    else:
        if ( numDup > 0 ):
            print " WARNING !!! DUPLICATE gene symbols coming in !!! ", numDup
            print dupList
            print " "

    # we want to loop over all of the feature names and attempt to add either
    # gene names or coordinates as appropriate ...

    print " "
    print " starting loop over %d feature names ... " % numRow

    newRowLabels = []
    usedGeneSymbols = []

    addGene = {}
    addCyto = {}

    # OUTER LOOP IS OVER ROWS ...
    for iRow in range(numRow):
        curLabel = rowLabels[iRow]

        print " "
        print " "
        print " QQ ", iRow, curLabel

        # we'll start by setting the newLabel to the curLabel ...
        newLabel = curLabel

        curType = curLabel[2:6]

        # don't make any attempts at annotating CLIN or SAMP features ...
        if (curType == "CLIN" or curType == "SAMP"):
            newRowLabels += [newLabel]
            continue
        # or platform features ...
        if (curLabel.lower().find("platform") >= 0 ):
            newRowLabels += [newLabel]
            continue

        haveName = 0
        haveCoord = 0
        haveValidCoord = 0
        haveExtraName = 0

        tokenList = curLabel.split(':')
        if (tokenList[2] != ''):
            haveName = 1
        if (tokenList[3] != ''):
            haveCoord = 1
        if (len(tokenList) > 7):
            if (tokenList[7] != ''):
                haveExtraName = 1

        print " curType=<%s>  haveName=%d  haveCoord=%d  haveExtraName=%d " % \
            (curType, haveName, haveCoord, haveExtraName)

        ## if we are forcing a re-annotation, then we may reset haveCoord to false ...
        if ( forceFlag == "YES" ):
            if ( haveCoord ):
                if ( curType == "GEXP" ): haveCoord = 0
                if ( curType == "MIRN" ): haveCoord = 0
                if ( curType == "GNAB" ): haveCoord = 0
                if ( curType == "RPPA" ): haveCoord = 0

        # ------------
        # IF haveCoord
        if (haveCoord):

            if (tokenList[3].startswith("ch")):
                try:
                    iStart = int(tokenList[4])
                except:
                    iStart = -1
                if (tokenList[5] != ''):
                    try:
                        iStop = int(tokenList[5])
                    except:
                        iStop = -1
                else:
                    iStop = iStart
                if (iStart > 0 and iStop > 0):
                    haveValidCoord = 1

        print " flags : ", haveName, haveCoord, haveValidCoord

        # if we have a name, check that it is the "correct" name,
        # and change it if necessary ... (note that most of 'chooseBestName'
        # is currently being bypassed 19dec12)
        # --> actually on 07jan13 have been trying to reinstate ...

        # ------------
        # IF haveName
        if (haveName):
            curGene = tokenList[2]
            curID = tokenList[7]

            newGene = chooseBestName ( curGene, curID, curType, \
                                       geneInfoDict, synMapDict, \
                                       GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID )

            if ( curGene.startswith("SLC35E2") ):
                ## gene IDs 728661 and 9906 are both being called "SLC35E2" in the RNAseqV2
                ## data, but 728661 should be changed to SLC35E2B ...
                if ( curID == "728661" ):
                    print " --> changing gene from <%s> to SLC35E2B " % curGene
                    curGene = "SLC35E2B"

            elif (nameChangeFlag == "YES"):
                if (newGene != curGene):
                    # do NOT change to this "new" name if this name seems to
                    # already be in use ...
                    if ((newGene in curGeneSymbols) or (newGene in usedGeneSymbols) or (newGene == "")):
                        print " --> NOT changing name from <%s> to <%s> " % (curGene, newGene)
                    else:
                        print " --> changing name from <%s> to <%s> " % (curGene, newGene)
                        curGene = newGene

            # keep track of 'used' gene symbols ...
            if (curGene not in usedGeneSymbols):
                usedGeneSymbols += [curGene]

        gotItFlag = 0

        # ------------------------------------
        # IF haveName=TRUE and haveCoord=FALSE
        if (haveName and not haveCoord):

            # here we want to add coordinates based on a gene name ... 
            # --> first we try Gencode, and then we try GAF ...

            # more importantly, FIRST we try by gene ID and then by gene symbol ...
            if ( haveExtraName ):
                geneID = tokenList[7]
                print "         --> first looking using gene ID <%s> " % geneID
                if (geneID in GAF_geneCoordDict_byID):
                    print " found by ID ... ", curLabel, curGene, geneID, GAF_geneCoordDict_byID[geneID]
                    newGene = GAF_geneSymbol_byID[geneID][0]
                    if (newGene != curGene):
                        print " --> changing name from <%s> to <%s> " % (curGene, newGene)
                        curGene = newGene
                        # sys.exit(-1)
                    newLabel = annotateLabel(curLabel, curGene, GAF_geneCoordDict_byID[geneID])
                    print " addGene : ", tokenList, " --> ", newLabel
                    gotItFlag = 1
                    if (curType not in addGene):
                        addGene[curType] = 1
                    else:
                        addGene[curType] += 1

            if ( not gotItFlag ):
                if (curGene in Gencode_geneCoordDict_bySymbol):
                    print " now looking by gene sybmol in Gencode ... ", curLabel, curGene, Gencode_geneCoordDict_bySymbol[curGene]
                    newLabel = annotateLabel(curLabel, curGene, Gencode_geneCoordDict_bySymbol[curGene])
                    print " addGene : ", tokenList, " --> ", newLabel
                    gotItFlag = 1
                    # keep track of how often we add a gene label ...
                    if (curType not in addGene):
                        addGene[curType] = 1
                    else:
                        addGene[curType] += 1

            if ( not gotItFlag ):
                if (curGene in GAF_geneCoordDict_bySymbol):
                    print " now looking by symbol in GAF ... ", curLabel, curGene, GAF_geneCoordDict_bySymbol[curGene]
                    newLabel = annotateLabel(curLabel, curGene, GAF_geneCoordDict_bySymbol[curGene])
                    print " addGene : ", tokenList, " --> ", newLabel
                    gotItFlag = 1
                    # keep track of how often we add a gene label ...
                    if (curType not in addGene):
                        addGene[curType] = 1
                    else:
                        addGene[curType] += 1

            if (not gotItFlag):
                print "     this gene is not in GAF by gene ID (or no gene ID available) ??? ", tokenList
                if (curGene in refGeneDict):
                    print "         finally, found in refGene ... ", curLabel, curGene, refGeneDict[curGene]
                    newLabel = annotateLabel(
                        curLabel, curGene, refGeneDict[curGene])
                    print " addGene : ", tokenList, " --> ", newLabel
                    # keep track of how often we add a gene label ...
                    if (curType not in addGene):
                        addGene[curType] = 1
                    else:
                        addGene[curType] += 1
                else:
                    print "         and also not in refGene ... "

        # -----------------------------------------
        # IF haveName=FALSE and haveValidCoord=TRUE
        elif (not haveName and haveValidCoord):

            # here we want to add either a single gene name based on valid
            # coordinates, or else we add a cytoband label ...
            # print tokenList
            geneList = overlap(curLabel, GAF_geneCoordDict_bySymbol)
            # print geneList

            if ( (len(geneList)!=1) or (curType=="CNVR") ):

                # if there are several (or zero) genes in this segment, then we
                # annotate based on cytoband instead ...
                # print curLabel
                # print geneList
                curCytoband = getCytobandLabel(curLabel, cytoDict)
                newLabel = curLabel[:7] + curCytoband + curLabel[7:]
                print " addCyto : ", tokenList, " --> ", newLabel
                # print newLabel
                # keep track of how often we add a gene label ...
                if (curType not in addCyto):
                    addCyto[curType] = 1
                else:
                    addCyto[curType] += 1

            else:

                # if there is just one gene, then use that
                if (hasSpecialChar(geneList[0])):
                    print " need to fix this gene name : ", geneList[0]
                    sys.exit(-1)
                newLabel = curLabel[:7] + geneList[0] + curLabel[7:]
                print " addGene : ", tokenList, " --> ", newLabel
                # print newLabel
                # keep track of how often we add a gene label ...
                if (curType not in addGene):
                    addGene[curType] = 1
                else:
                    addGene[curType] += 1

        newRowLabels += [newLabel]

        # END OF BLOCK of SEVERAL IF STATEMENTS
        # -------------------------------------

    # END OF OUTER LOOP OVER ROWS ...

    print " "
    print " "

    if ( 0 ):
        # before we assign the new row labels, make sure that they
        # are unique !!
        numIdent = 0
        print " checking for label uniqueness ... ", len(newRowLabels)
        for ii in range(len(newRowLabels)):
            if ( (ii%10000) == 0 ): print ii, len(newRowLabels)
            for jj in range(ii + 1, len(newRowLabels)):
                if (newRowLabels[ii] == newRowLabels[jj]):
                    print " WARNING !!! identical labels ??? tacking on dup "
                    print ii, newRowLabels[ii]
                    print jj, newRowLabels[jj]
                    if (newRowLabels[jj][-1] == ":"):
                        newRowLabels[jj] += "dup"
                    else:
                        newRowLabels[jj] += "_dup"
                    print "     --> ", jj, newRowLabels[jj]
                    numIdent += 1
        if (0):
            if (numIdent > 0):
                sys.exit(-1)

    print " "
    print " OK ... "
    print " "

    if (len(newRowLabels) == len(rowLabels)):
        print " --> seem to have all the new labels ... ", len(newRowLabels), len(rowLabels)
        print "     addGene : ", addGene
        print "     addCyto : ", addCyto
        # assign the new labels ...
        dataD['rowLabels'] = newRowLabels
        return (dataD)

    else:
        print "     ERROR ??? wrong number of labels ??? "
        print len(newRowLabels), len(rowLabels)
        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) >= 4):
            inFile = sys.argv[1]
            build = sys.argv[2]
            outFile = sys.argv[3]
            if (len(sys.argv) >= 5):
                forceFlag = sys.argv[4].upper()
            else:
                forceFlag = "NO"
            if (len(sys.argv) >= 6):
                nameChangeFlag = sys.argv[5].upper()
            else:
                nameChangeFlag = "NO"
        else:
            print " "
            print " Usage: %s <input TSV file> <hg18 or hg19> <output TSV file> [force REannotation=NO/YES] [nameChangeFlag=NO/YES] "
            print "        note that forceFlag nameChangeFlag will default to NO "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
            tumorType = 'gbm'

    if (forceFlag == "Y"):
        forceFlag = "YES"
    if (forceFlag != "YES"):
        forceFlag = "NO"

    if (nameChangeFlag == "Y"):
        nameChangeFlag = "YES"
    if (nameChangeFlag != "YES"):
        nameChangeFlag = "NO"

    print "         forceFlag = %s " % forceFlag
    print "         nameChangeFlag = %s " % nameChangeFlag
    print " "

    # and get the coordinates for these genes ...
    bioinformaticsReferencesDir = gidgetConfigVars['TCGAFMP_BIOINFORMATICS_REFERENCES']
    if (build == 'hg18'):
        gafFilename = bioinformaticsReferencesDir + "/GAF/Feb2011/GAF.hg18.Feb2011/GAF_bundle/outputs/TCGA.hg18.Feb2011.gaf"
        gencodeFilename = ""
        cybFilename = bioinformaticsReferencesDir + "/hg18/cytoBand.hg18.txt"
    elif (build == 'hg19'):
        gafFilename = bioinformaticsReferencesDir + "/GAF/GAF3.0/all.gaf"
        gencodeFilename = bioinformaticsReferencesDir + "/gencode/gencode.v19.gene.gtf"
        refGeneFilename = bioinformaticsReferencesDir + "/hg19/refGene.txt"
        cybFilename = bioinformaticsReferencesDir + "/hg19/cytoBand.hg19.txt"
    else:
        print " ERROR ... genome build must be either hg18 or hg19 "

    infFilename = bioinformaticsReferencesDir + "/ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info"

    print " "
    print " Running : %s %s %s %s " % (sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])
    print "           %s " % gafFilename
    print "           %s " % gencodeFilename
    print "           %s " % refGeneFilename
    print "           %s " % cybFilename
    print "           %s " % infFilename
    print " "
    print " "

    # read in the input feature matrix first, just in case there
    # actually isn't one yet available ...
    print " --> calling tsvIO.readTSV ... "
    testD = tsvIO.readTSV(inFile)
    try:
        print len(testD['rowLabels']), len(testD['colLabels'])
        if (len(testD['rowLabels']) == 0 or len(testD['colLabels']) == 0):
            print " EXITING ... no data "
            sys.exit(-1)
    except:
        print " --> invalid / missing input feature matrix "
        sys.exit(-1)

    # read in the gene_info file ...
    # this was turned off ... looking into turning it back on (1/7/13)
    # turning it back off (1/17/14)
    if (0):
        print " --> calling readGeneInfoFile ... "
        (geneInfoDict, synMapDict) = refData.readGeneInfoFile(infFilename)
    else:
        geneInfoDict = {}
        synMapDict = {}

    # then read in the GAF file ... or GENCODE ...
    print " --> calling readGAF ... "
    (GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID) = refData.readGAF(gafFilename)

    print " --> and Gencode ... "
    (Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID) = refData.readGencode(gencodeFilename)

    # also the refGene file ...
    # looking in to turning this off too (1/17/14)
    if ( 0 ):
        print " --> calling readRefGeneFile ... "
        refGeneDict = refData.readRefGeneFile(refGeneFilename)
    else:
        refGeneDict = {}

    # then read in the cytoband file ...
    print " --> calling readCytobandFile ... "
    cytoDict = refData.readCytobandFile(cybFilename)

    # and annotate the features
    print " --> calling annotateFeatures ... "
    annotD = annotateFeatures ( testD, geneInfoDict, synMapDict, \
        Gencode_geneCoordDict_bySymbol, Gencode_geneCoordDict_byID, Gencode_geneSymbol_byID, \
        GAF_geneCoordDict_bySymbol, GAF_geneCoordDict_byID, GAF_geneSymbol_byID, \
        refGeneDict, cytoDict, forceFlag, nameChangeFlag )

    # check that the feature names are still unique ...
    print " --> verify that the feature names are unique ... "
    ( newLabels, rmList ) = tsvIO.uniqueFeatureLabels(annotD['rowLabels'], annotD['dataMatrix'])
    print "     back from tsvIO.uniqueFeatureLabels "

    # quick sanity check that labels are still what I think they are ...
    for ii in range(len(newLabels)):
        if (not (newLabels[ii] == annotD['rowLabels'][ii])):
            print " "
            print " BAILING !!! ", newLabels[ii], annotD['rowLabels'][ii]
            print " "
            sys.exit(-1)

    # remove any 'extra' features that need removing ...
    if ( len(rmList) > 0 ):
        print "     --> need to remove these rows ", rmList
        tmpD = tsvIO.filter_dataMatrix ( annotD, rmList, [] )
        annotD = tmpD

    # and write the matrix back out
    print " --> calling tsvIO.writeTSV_dataMatrix ... "
    tsvIO.writeTSV_dataMatrix(annotD, 0, 0, outFile)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
