'''
Created on Jun 18, 2012

this is a refactoring of sheila's new_Level3_matrix script into an OO
approach

@author: m.miller

'''
import ConfigParser
import os
import sys
import traceback
from   datetime import datetime

import miscIO
import miscTCGA
import path
from   technology_type_factory import technology_type_factory

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
class NoSamplesException(Exception):
    '''
    classdocs
    '''

    def __init__(self, msg):
        '''
        Constructor
        '''
        Exception.__init__(self, msg)
    
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def makeOutputFilename ( tumorList, platformID, outSuffix ):
    outDir = config.get('main', 'out_directory')
    if ( len(tumorList) == 1 ):
        zCancer = tumorList[0]
    elif len(tumorList) == len(config.get('main', 'cancerDirNames').split(',')):
        zCancer = 'all'
    else:
        tumorList.sort()
        zCancer = tumorList[0]
        for aCancer in tumorList[1:]:
            zCancer = zCancer + '_' + aCancer
        print " --> combined multi-cancer name : <%s> " % zCancer

    ## start by pasting together the outDir, cancer sub-dir, then '/'
    ## and then the cancer name again, followed by a '.'
    # outFilename = outDir + zCancer + "/" + zCancer + "."
    # match change in current script to put directly in outDir --mm 2013-05-01
    outFilename = outDir + "/" + zCancer + "."
    # make sure the directory exists
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    ## next we want to replace all '/' in the platform string with '__'
    i1 = 0
    while ( i1 >= 0 ):
        i2 = platformID.find('/', i1)
        if 0 > i2:
            # --mm for testing on windows
            i2 = platformID.find('\\', i1)
        if ( i1>0 and i2>0 ):
            outFilename += "__"
        if ( i2 > 0 ):
            outFilename += platformID[i1:i2]
            i1 = i2 + 1
        else:
            i1 = i2

    ## and finally we add on the suffix (usually something like '25jun')
    if ( not outSuffix.startswith(".") ):
        outFilename += "."
    outFilename += outSuffix

    return ( outFilename )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def hackBarcode ( barcode ):
    if (barcode.startswith("TCGA-") and barcode[19] == '-'):
        barcode = barcode[:19] + 'A' + barcode[19:27]
    return barcode

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def sanityCheckSDRF ( sdrfFilename ):
    try:
        fh = file ( sdrfFilename )
    except:
        print " ERROR in sanityCheckSDRF ??? failed to open file ??? "
        print sdrfFilename
        sys.exit(-1)

    nl = miscIO.num_lines ( fh )
    nr = min ( nl/2, 5 )
    nt = [0] * nr
    for index in range(nr):
        aLine = fh.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        nt[index] = len ( tokenList )

    ntMin = min ( nt )
    ntMax = max ( nt )
    for index in range(nl-nr):
        aLine = fh.readline()
        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        ntCur = len ( tokenList )
        if ( ntCur == 0 ): 
            continue
        if ( ntCur < ntMin ):
            mess = "ERROR in sanityCheckSDRF ??? file appears to have been truncated ??? %i %i %i %s" % (ntCur, ntMin, ntMax, str(tokenList))
            raise ValueError(mess)

    fh.close()

    return 1

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def getSDRFinfo(sdrfFilename, techType):
    try:
        print '\n', datetime.now(), 'in getSDRFinfo ... <%s> ' % sdrfFilename
        ## figure out which platform it is based on the SDRF file ...
        print "\tPlatform : ", techType
            
        sanityCheckSDRF(sdrfFilename)
        techType.preprocessSDRFFile(sdrfFilename)
    
        filename2sampleID = {}
        reader = open(sdrfFilename)
        hdrTokens = reader.readline().strip().split('\t')
    
        # set the column indices
        techType.setConfiguration(hdrTokens)

        archives = set()
        barcodes = set()
        numTokens = len(hdrTokens)
        lineNum = 0
        while True:
            tokens = reader.readline().strip().split('\t')
            if ( len(tokens) < numTokens ):
                break
            lineNum += 1
    
            (barcode, filename, archive, otherInfo, includeFlag, message) = techType.includeFile(tokens)
            
            ## also sanity check that we don't have duplicate barcodes ...
            if (includeFlag and not barcode in barcodes):
                archives.add(archive)
                barcodes.add(barcode)
                # TODO: check if barcode is a UUID and in hackBarcode look up barcode from UUID
                fileBarcodes = filename2sampleID.get(filename, [])
                ## need to take this out (21feb13) because we need to keep
                ## the barcodes that the DCC reports in the UUID-to-barcode
                ## mapping metadata file ...
                # fileBarcodes.append((hackBarcode(barcode), otherInfo, archive))
                fileBarcodes.append((barcode, otherInfo, archive))
                filename2sampleID[filename] = fileBarcodes
                print '\tYES including this file ... ', techType.iFilename, tokens[techType.iFilename], techType.iBarcode, tokens[techType.iBarcode], techType.iYes, tokens[techType.iYes]
            else:
                if not message:
                    message = '\t(-) NOT including this file ... ', techType.iFilename, tokens[techType.iFilename], techType.iBarcode, tokens[techType.iBarcode], techType.iYes, tokens[techType.iYes]
                print '\t', str(message)[1:-1].replace(',', ' '), 'line #: ', lineNum
    
        if 0 == len(filename2sampleID):
            raise ValueError('no files were found: tokens[barcode=%i]' % (techType.iBarcode))
        keyList = filename2sampleID.keys()
        keyList.sort()
        print '\tfirst file in filename2sampleID dictionary: ', keyList[0], filename2sampleID[keyList[0]]
    
        ## now sort ...
        archives = list(archives)
        archives.sort()
        print '\tfound %d archives and %d data files ' % ( len(archives), len(filename2sampleID) )
    
        print datetime.now(), 'completed getSDRFinfo ... <%s> %d\n' % (sdrfFilename, len(filename2sampleID) )
    except ValueError as ve:
        print ve
        return 0, {}, []
    return (len(barcodes), filename2sampleID, archives)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def getArchiveRevision(dName, mtIndicator):
    print '\tin getArchiveRevision ... %s' % dName
    mageTabStart = dName.find(mtIndicator)
    mageTabEnd = mageTabStart + 9
    archDelim = dName.find('.', mageTabEnd) 
    revDelim = dName.find('.', archDelim+1) 

    iArch = int(dName[mageTabEnd:archDelim])
    iRev  = int(dName[archDelim+1:revDelim])
    return ( iArch, iRev )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def getSDRFilename(topDir):
    print '\n', datetime.now(), "in getSDRFilename starting at %s" % topDir
    ## print topDir

    if ( os.path.exists(topDir) ):
        topPath = path.path ( topDir )
        if ( not topPath.isdir() ):
            print ' <%s> is not a directory, skipping ... ' % topPath
            return ( 'NA' )
    else:
        print ' <%s> does not exist, skipping ... ' % topDir
        return ( 'NA' )

    ## first we need to gather up all of the mage-tab directory names, with the proper
    ## archive and revision numbers ... and at the same time, find the highest
    ## archive #
    mtIndicator = config.get('main', 'mage_tab_dir_indicator')
    mageTabDict = {}
    maxArch = -1
    for dName in topPath.dirs():
        if ( dName.find(mtIndicator) >= 0 ):
            ( iArch, iRev ) = getArchiveRevision(dName, mtIndicator)
            mageTabDict[dName] = ( iArch, iRev )
            if ( iArch > maxArch ):
                maxArch = iArch

    if ( maxArch == -1 ):
        print " WARNING ... in getSDRFilename ... failed to find mage-tab directory in %s" % topDir

    ## now we need to get the highest revision number for this archive
    maxRev = -1
    for curKey in mageTabDict.keys():
        if ( mageTabDict[curKey][0] == maxArch ):
            if ( mageTabDict[curKey][1] > maxRev ):
                maxRev = mageTabDict[curKey][1]
                topKey = curKey

    if ( maxRev < 0 ):
        print "\n--> FAILED to find SDRF file !!! ", topDir
        ## print "\nFATAL ERROR in getSDRFilename ??? %s %s %s %s" % (mageTabDict.keys(), mageTabDict, maxArch, maxRev)
        ## return ( "NA" )
        raise ValueError("\nFATAL ERROR in getSDRFilename ??? %s %s %s %s" % (mageTabDict.keys(), mageTabDict, maxArch, maxRev))

    ## and now we have the proper mage-tab directory
    print '\thave topKey: ',  topKey
    mageTabDir = path.path( topKey)
    for fName in mageTabDir.files():
        print '\tlooking at fName <%s> ' % fName
        if ( fName.endswith(config.get('main', 'sdrfExt')) ):
            print datetime.now(), 'found', fName, 'in getSDRFilename'
            return ( fName )

    print "\t--> FAILED to find SDRF file !!! ", topDir
    print "FATAL ERROR in getSDRFilename ??? %s %s %s %s" % (mageTabDict.keys(), mageTabDict, maxArch, maxRev)
    return ( "NA" )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def getFilesFromArchives(topDir, techType):
    return techType.getFilesFromArchives(topDir)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def openDataFreezeLogFile(tumorTypes, outFilename, outSuffix, platformStrings):
    print " in openDataFreezeLogFile ... "

    if ( len(platformStrings) != 1 ):
        print " ERROR in openDataFreezeLogFile ... there should only be one platform string "
        print platformStrings
        sys.exit(-1)
    print "\t<%s> <%s> <%s> <%s>" % (outFilename, tumorTypes, outSuffix, platformStrings[0])
    
    if len(tumorTypes) == len(config.get('main', 'cancerDirNames').split(',')):
        tumorTypes = ['all']

    tumors = ''
    for tumorType in tumorTypes:
        tumors += tumorType + '_'
    tumors = tumors[:-1]
    
    outFilename = outFilename[:outFilename.rindex('/') + 1]
    dflFilename = outFilename + tumors + "." + outSuffix + "."
    tokenList = platformStrings[0].split('/')
    print len(tokenList), tokenList

    for ii in range(len(tokenList)-1,0,-1):
        if ( len(tokenList[ii]) > 0 ):
            dflFilename += tokenList[ii]
            dflFilename += "__"
    dflFilename += tokenList[0]

    dflFilename += ".data_freeze.log"

    print " opening log file at: ", dflFilename
    fh = file ( dflFilename, 'w' )

    return ( fh )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def verifyPath(outFilename):
    index = str(outFilename).rindex('/')
    outPath = outFilename[0:index]
    if (not os.path.exists(outPath)):
        os.makedirs(outPath)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def writeLog(logFile, filename2sampleInfo, tumorType, platformID, outSuffix, outFilename):
    logFile.write('%s Files for 2012_06_18_parse_tcga.py %s %s %s\n' % (datetime.now(), tumorType, outSuffix, platformID))
    archive2files = {}
    for filename, info in filename2sampleInfo.iteritems():
        files = archive2files.get(info[0][2], [])
        files += [(info[0][0], filename)]
        archive2files[info[0][2]] = files
    
    archives = archive2files.keys()
    archives.sort()
    for archive in archives:
        logFile.write('\t%s\n' % archive)
        fileinfo = archive2files[archive]
        for barcode, filename in fileinfo:
            logFile.write('\t\t%s %s\n' % (barcode, filename))
    
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def parseFileInfo(techType, tumorType):
    try:
        topDir = techType.getTopDirectory(tumorType);
    except:
        traceback.print_exc()
        raise ValueError('problem reading top dir for %s:%s' % (techType, tumorType))
    print "topDir: %s" % topDir
    
    if techType.hasSDRFFile():
        sdrfFilename = getSDRFilename(topDir)
        if (sdrfFilename == "NA"):
            return 0, None, None, None
        else:
            numSamples, filename2sampleInfo, archiveList = getSDRFinfo(sdrfFilename, techType)
            localTopDirs = [topDir] ## load up the information from the SDRF file ...
    else:
        numSamples, filename2sampleInfo, archiveList, localTopDirs = getFilesFromArchives(topDir, techType) ## load up the information from the directory structure ...
    return numSamples, filename2sampleInfo, archiveList, localTopDirs

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def mergeFilename2SampleInfo(mergedFilename2sampleInfo, filename2sampleInfo):
# check for filename being the same
    for key in filename2sampleInfo.iterkeys():
        if key in mergedFilename2sampleInfo:
            raise ValueError('(a) this should not happen, right ??? file %s already seen' % key)
#            print "WARNING: (b) duplicate file should not happen, right ??? %s " % (key)
#            continue

# check for barcodes being the same
    newBarcodes = set([info[0][0] for info in filename2sampleInfo.itervalues()])
    curBarcodes = set([info[0][0] for info in mergedFilename2sampleInfo.itervalues()])
    if len(curBarcodes & newBarcodes):
        for barcode in curBarcodes & newBarcodes:
            if '-20A-' != barcode[12:17]:
                raise ValueError('(b) this should not happen, right ??? barcode(s) %s already seen. %s %s' % ((curBarcodes & newBarcodes), barcode, barcode[12:17]))
    mergedFilename2sampleInfo.update(filename2sampleInfo)


def mergeArchiveList(mergedArchiveList, archiveList):
# check for archives being the same
    for archive in archiveList:
        if (archive == "unknown"):
            continue
        if archive in mergedArchiveList:
            raise ValueError('(c) this should not happen, right ??? archive %s already seen' % archive)
    
    mergedArchiveList += archiveList
    return mergedArchiveList

def parseCancers(platformID, tumorTypes, outSuffix):
    if 1 == len(tumorTypes) and 'all' == tumorTypes[0].lower():
        tumorTypes = config.get("main","cancerDirNames").split(',')
    
    techType = technology_type_factory(config).getTechnologyType(config, platformID)
    outFilename = makeOutputFilename(tumorTypes, platformID, outSuffix)
    logFile = None
    totalSamples = 0
    mergedFilename2sampleInfo = {}
    mergedArchiveList = []
    topDirs = []
    for tumorType in tumorTypes:
        try:
            numSamples, filename2sampleInfo, archiveList, localTopDirs = parseFileInfo(techType, tumorType)
            if 0 == numSamples:
                print 'did not find any samples for %s' % tumorType
                continue 
            
            if techType.isBioAssayDataMatrix():
                totalSamples = numSamples
                mergedFilename2sampleInfo = filename2sampleInfo
                mergedArchiveList = archiveList
            else:
                mergeFilename2SampleInfo(mergedFilename2sampleInfo, filename2sampleInfo)
                mergedArchiveList = mergeArchiveList(mergedArchiveList, archiveList)
                
                ## write out what we are using to the log file ...
                if not logFile:
                    logFile = openDataFreezeLogFile(tumorTypes, outFilename, outSuffix, [platformID])
                writeLog(logFile, filename2sampleInfo, tumorType, platformID, outSuffix, outFilename)
                topDirs += localTopDirs
                totalSamples += numSamples
        except Exception as e:
            print
            traceback.print_exc(10)
            # record the error but move on
            # print 'ERROR: problem parsing tumor type %s for platform %s' % (tumorType, platformID), e
            
            # raise the exception and stop processing
            raise e
        
    if logFile:
        logFile.flush()
        logFile.close()
    if 0 == totalSamples:
        ## print 'did not find any samples for tumor types %s for platform \'%s\'' % (tumorTypes, platformID)
        ## return
        raise NoSamplesException('ERROR ??? did not find any samples for tumor types %s for platform \'%s\'' % (tumorTypes, platformID))
    
    print "--> setting numSamples ... samples: %i files: %i mappings: %i" % (totalSamples, len(mergedFilename2sampleInfo), len(mergedFilename2sampleInfo))
    try:
        (dataMatrix, featureList, sampleList) = techType.processDirectories(topDirs, mergedArchiveList, mergedFilename2sampleInfo, totalSamples)
        matrixParams = techType.postprocess(dataMatrix, featureList, sampleList)
        verifyPath(outFilename)
        techType.writeMatrix(matrixParams, outFilename)
    except Exception as e:
        print
        traceback.print_exc()
        print
        raise ValueError('ERROR ??? problem processing tumor types %s for platform \'%s\'' % (tumorTypes, platformID), e)
        print
        

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def verifyArgs(platformID, tumorTypes):
    if ( len(tumorTypes) == 0 ):
        raise ValueError(" ERROR ??? have no tumor types in list ??? ", tumorTypes)

    if 'all' != tumorTypes[0].lower():
        cancerNames = config.get("main","cancerDirNames")
        for tumorType in tumorTypes:
            if (tumorType in cancerNames):
                print "\tprocessing tumor type: ", tumorType
            else:
                raise ValueError("ERROR ??? tumorType <%s> not in list of known tumors: %s? " % (tumorType,cancerNames))
        
    platformStrings = technology_type_factory(config).getTechnologyTypes()
    if (platformID in platformStrings):
        print "\tprocessing platform: ", platformID
    else:
        print "\tplatform <%s> is not supported " % platformID
        print "\tcurrently supported platforms are:\n", platformStrings
        raise ValueError("ERROR ??? platform <%s> is not supported " % platformID)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def setConfig(configFile):
    # Read the configuration file
    config = ConfigParser.ConfigParser()
    config.read(configFile)
    return config

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def checkUsage(argv):
    if ( len(argv) < 2 or len(argv) > 6):
        print " Usage: %s <config file>[ <platform>[ <tumor,[...]*>[ <tag>][ <snapshot>]*]*]*]*" % argv[0]
        print "saw %s" % argv
        print " ERROR -- bad command line arguments "
        sys.exit(-1)
    
    print 'checking %s for validity from %s' % (argv[1], path.path.getcwd())
    if not path.path.isfile(path.path(argv[1])):
        print '%s is not a file from %s' % (argv[1], path.path.getcwd())
        sys.exit(-1)
        
def initialize(argv):
    checkUsage(argv)
    global config
    config = setConfig(argv[1])
    if 2 < len(argv):
        platformID = argv[2]
    else:
        platformID = config.get('main', 'platformID')
    
    if 3 < len(argv):
        tumorTypes = argv[3].split(',')
    else:
        tumorTypes = config.get('main', 'tumorTypes').split(',')

    if 4 < len(argv):
        outSuffix = argv[4]
    else:
        outSuffix = config.get('main', 'outSuffix')

    if 5 < len(argv):
        config.set('technology_type', 'snapshot', argv[5]) 
        snapshotName = config.get('technology_type', 'snapshot') 
        miscTCGA.setMappingFile ( snapshotName )

    verifyArgs(platformID, tumorTypes)
    
    return platformID, tumorTypes, outSuffix

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
if __name__ == '__main__':
    print datetime.now(), "starting..."
    try:
        platformID, tumorTypes, outSuffix = initialize(sys.argv)
        parseCancers(platformID, tumorTypes, outSuffix)
    except Exception as e:
        print e
    print datetime.now(), "finished"
    sys.exit(0)

