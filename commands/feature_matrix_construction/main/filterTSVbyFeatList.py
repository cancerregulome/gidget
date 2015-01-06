# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscTCGA
import tsvIO

import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def readFeatureListFromFile(featNameFile):

    try:
        fh = file(featNameFile)
    except:
        print " FAILED to read input list from <%s> " % featNameFile
        return ([])

    featNameList = []

    for aLine in fh:
        aLine = aLine.strip()
        if ( len(aLine) < 1 ): continue
        if ( aLine.startswith ("#") ): continue
        if ( aLine.find('\t') > 0 ):
            aTokens = aLine.split()
            featNameList += [ aTokens[0] ]
        elif ( aLine.find('#') > 0 ):
            aTokens = aLine.split()
            featNameList += [ aTokens[0] ]
        else:
            featNameList += [aLine]

    fh.close()

    return (featNameList)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# tmpLabel is a test feature (row) label from the input matrix
# featNameList is the list of features that are to be black-listed (or white-)
# aFlag specifies whether the match is to be 'strict' or loose


def is_in_list(tmpLabel, featNameList, aFlag):

    lowerT = tmpLabel.lower()

    for aSample in featNameList:
        lowerA = aSample.lower()
        if (aFlag == "strict"):
            if (lowerA == lowerT):
                return (1)
        else:
            # if the matching is "loose", then allow substring matching...
            if (lowerT.find(lowerA)>=0): return (1)
            if (lowerT.startswith(lowerA)): return (1)

    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def get_strict_name ( tmpLabel, featNameList ):

    lowerT = tmpLabel.lower()
    for aSample in featNameList:
        lowerA = aSample.lower()
        if ( lowerT.find(lowerA)>=0 ): return ( aSample )
        if ( lowerT.startswith(lowerA) ): return ( aSample )

    return ( '' )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    if (1):
        # there must be 2 + 3N parameters, where N is the # of sample-lists
        # being used for filtering ...
        if (len(sys.argv) < 6):
            print " Usage : %s <input file> <output file> <feature-list> <{black,white}> <{loose,strict}> " % sys.argv[0]
            print " "
            print " Notes : a BLACK list means that all features in this list must be removed "
            print "         a WHITE list means that only features in this list should be kept "
            print " "
            print "         LOOSE filtering means that only a partial match to the feature name is required "
            print "         STRICT filtering means that an exact match to the feature name is required "
            print "         from the input file, and this is generally done with LOOSE filtering "
            print " "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)

        inFile = sys.argv[1]
        outFile = sys.argv[2]

        ii = 3
        listInfo = []
        while (len(sys.argv) >= (ii + 2)):
            listInfo += [sys.argv[ii:ii + 3]]
            ii += 3
        if (len(listInfo) < 1):
            print " ERROR ??? no sample-list information provided ??? "
            sys.exit(-1)

    print " "
    print " in filterTSVbyFeatList.py ... "
    print "         input file  : ", inFile
    print "         output file : ", outFile
    print "         list info   : ", listInfo
    print " "

    # print " "
    # print " ***************************************************************** "
    # print " calling readTSV ... ", inFile
    dataD = tsvIO.readTSV(inFile)
    if (dataD == {}):
        print " ERROR: nothing returned from <%s> ??? " % inFile
        sys.exit(-1)

    tsvIO.lookAtDataD(dataD)

    # as we read in the white lists (if any), build up an ordered list
    # of the feature names ...
    orderedWhiteList = []

    print " "
    print " reading feature name lists ... "
    numLists = len(listInfo)
    listDetails = [0] * numLists
    listBW = [0] * numLists
    listLS = [0] * numLists
    for iList in range(numLists):
        print " --> loading feature list #%d from <%s> " % ((iList + 1), listInfo[iList][0])
        listDetails[iList] = readFeatureListFromFile(listInfo[iList][0])
        listBW[iList] = listInfo[iList][1]
        listLS[iList] = listInfo[iList][2]
        if (len(listDetails[iList]) > 0):
            print "     %4d features found, eg <%s> " % (len(listDetails[iList]), listDetails[iList][0])
        else:
            print "        0 features found "
            if (listLS[iList] == "strict"):
                print "             --> NO strict filtering can/will be applied "


        print " "
        print iList
        print listDetails[iList][:3]
        print listBW[iList]
        print listLS[iList]

        if ( listBW[iList] == "white" ): orderedWhiteList += listDetails[iList]

    print " length of ordered white list : ", len(orderedWhiteList)

    # now we start the real work ...

    rowLabels = dataD['rowLabels']
    dataMatrix = dataD['dataMatrix']
    numRow = len(dataMatrix)
    if (numRow != len(rowLabels)):
        print " mismatched sizes ??? ", numRow, len(rowLabels)
        sys.exit(-1)

    print " "
    print "     %4d features in input data matrix " % numRow
    print " debug : rowLabels  : ", rowLabels[1:5]

    print " "
    print " building up skipRowList ... "
    skipRowList = []
    for iList in range(numLists):

        featNameList = listDetails[iList]
        if (len(featNameList) == 0):
            continue

        bwFlag = listBW[iList]
        lsFlag = listLS[iList]
        print "         examining list #%d (%d,%s,%s) " % ((iList + 1), len(featNameList), bwFlag, lsFlag)

        numSkip = 0
        for iRow in range(numRow):
            # print rowLabels[iRow], featNameList[1:5]
            tmpLabel = rowLabels[iRow]
            # print tmpLabel

            # if this feature has already been added to the skip-list,
            # we don't need to add it again ...
            if (iRow in skipRowList):
                print "     <%s> is ALREADY in the skip-list (list #%d) " % (tmpLabel, (iList + 1))
                continue

            # NEW:
            if (bwFlag == "black"):
                if (is_in_list(tmpLabel, featNameList, lsFlag)):
                    print " --> %s is being black-listed " % tmpLabel
                    skipRowList += [iRow]
                    numSkip += 1

            else:
                if (not is_in_list(tmpLabel, featNameList, lsFlag)):
                    skipRowList += [iRow]
                    numSkip += 1
                else:
                    print " --> %s is being white-listed " % tmpLabel

        print "         --> %d additional features to be skipped " % numSkip, listInfo[iList][0], bwFlag, lsFlag
    # print skipRowList

    print " "
    print " number of features to be skipped : ", len(skipRowList)
    print " --> number of features remaining : ", (numRow - len(skipRowList))

    if (0):
        if (len(skipRowList) == 1):
            print "     for example ", rowLabels[skipRowList[0]]
        elif (len(skipRowList) > 1):
            print "     for example ", rowLabels[skipRowList[0]], rowLabels[skipRowList[-1]]

    else:
        print " "
        print " "
        for iRow in range(len(skipRowList)):
            print "    REMOVING FEATURE %s " % rowLabels[skipRowList[iRow]]
        print " "
        print " "

    if (len(skipRowList) > int(0.90 * numRow)):
        print " "
        print " WARNING !!! more than 90% of the data is going to be lost ??? !!! "
        print " "
        # sys.exit(-1)

    print " "
    print " calling filter_dataMatrix ... "
    outD = tsvIO.filter_dataMatrix(dataD, skipRowList, [])

    # now build up the list of actual features that we have ... 
    curRowLabels = outD['rowLabels']
    numRow = len(curRowLabels)
    print " now we have %d output features " % numRow

    # and put together a new ordered list for the output ...
    # (here we need the 'strict' feature names)
    print " building up new outputOrder vector "
    outputOrder = []
    for jRow in range(len(orderedWhiteList)):
        aFeat = orderedWhiteList[jRow]
        if ( is_in_list ( aFeat, curRowLabels, 'strict' ) ):
            outputOrder += [ aFeat ]
        elif ( is_in_list ( aFeat, curRowLabels, 'loose' ) ):
            sName = get_strict_name ( aFeat, curRowLabels ) 
            if ( sName != '' ):
                outputOrder += [ sName ]
        else:
            doNothing = 1
            print " <%s> will not be in the output " % aFeat

    print " --> length = %d " % len(outputOrder)

    # any features that are not in the ordered white list will just be
    # tacked on at the end in whatever order we come across them ...
    for iRow in range(numRow):
        if ( curRowLabels[iRow] not in outputOrder ):
            outputOrder += [ curRowLabels[iRow] ]
    print " --> length = %d " % len(outputOrder)

    # sanity check ...
    if ( len(outputOrder) != numRow ):
        print " ERROR ??? length of ordered list is wrong ??? "
        print len(outputOrder), numRow
        sys.exit(-1)
    
    # and now we need to build up the output rowOrder ...
    print " setting up index-mapping for output order "
    sortRowFlag = 1
    rowOrder = [0] * numRow
    for newPos in range(numRow):
        ## print " "
        ## print newPos, outputOrder[newPos]
        oldPos = curRowLabels.index(outputOrder[newPos])
        ## print oldPos, curRowLabels[oldPos]
        rowOrder[newPos] = oldPos

    print " --> the new rowOrder vector : "
    print rowOrder[:5], rowOrder[-5:]
        
    # set up sorting options ...
    sortColFlag = 0
    colOrder = []

    print " "
    print " calling writeTSV_dataMatrix ... ", outFile
    tsvIO.writeTSV_dataMatrix(outD, sortRowFlag, sortColFlag, outFile, rowOrder, colOrder)

    print " "
    print " DONE "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
