'''
Created on Aug 15, 2013

@author: michael
'''
import ConfigParser
from datetime import datetime
import os
import sys
import traceback

import miscTCGA
import parse_tcga
import path
from technology_type_factory import technology_type_factory
from record_info import recordInfo

# Extract Name
# Comment [TCGA Barcode]
# Protocol REF
# Labeled Extract Name
# Label
# Term Source REF
# Protocol REF
# Hybridization Name
# Array Design REF
# Term Source REF
# Protocol REF
# Scan Name
# Array Data File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data Matrix File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data Matrix File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data Matrix File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data Matrix File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data Matrix File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]
# Protocol REF
# Normalization Name
# Derived Array Data File
# Comment [TCGA Archive Name]
# Comment [TCGA Data Type]
# Comment [TCGA Data Level]
# Comment [TCGA Include for Analysis]
# Comment [Genome reference]
# Comment [md5]

class HeaderInfo:
    def __init__(self, startIndex, hdrTokens):
        self.fileNameIndex = startIndex
        self.archiveNameIndex = -1
        self.typeIndex = -1
        self.levelIndex = -1
        self.includeIndex = -1
        for index, hdrToken in enumerate(hdrTokens[startIndex + 1:]):
            if 'Comment' not in hdrToken:
                break
            
            if '[TCGA Archive Name]' in hdrToken:
                self.archiveNameIndex = startIndex + 1 + index
            elif 'TCGA Data Type' in hdrToken:
                self.typeIndex = startIndex + 1 + index
            elif '[TCGA Data Level]' in hdrToken:
                self.levelIndex = startIndex + 1 + index
            elif '[TCGA Include for Analysis]' in hdrToken:
                self.includeIndex = startIndex + 1 + index
        if -1 == self.archiveNameIndex or -1 == self.typeIndex or -1 == self.levelIndex or -1 == self.includeIndex:
            raise ValueError('''Didn't find all the info for the header: start: %i archive: %i type: %i level: %i include: %i''' % (self.fileNameIndex, self.archiveNameIndex, self.typeIndex, self.levelIndex, self.includeIndex))

def processHeaderLine(hdrTokens):
    headerInfos = []
    for index, hdrToken in enumerate(hdrTokens):
        if 'Array' in hdrToken and 'Data' in hdrToken and 'File' in hdrToken:
            headerInfos += [HeaderInfo(index, hdrTokens)]
    return headerInfos

def getSDRFinfo(sdrfFilename, techName, techType, archiveInfo):
    print '\n', datetime.now(), 'in getSDRFinfo ... <%s> ' % sdrfFilename
    ## figure out which platform it is based on the SDRF file ...
    print "\tPlatform : ", techType
        
    parse_tcga.sanityCheckSDRF(sdrfFilename)
    reader = open(sdrfFilename)
    hdrTokens = reader.readline().strip().split('\t')
    headerInfos = processHeaderLine(hdrTokens)
    uuidIndex = -1
    barcodeIndex = -1
    
    numTokens = len(hdrTokens)
    lineNum = 0
    archives = set()
    numFiles = 0
    while True:
        tokens = reader.readline().strip().split('\t')
        if ( len(tokens) < numTokens ):
            break
        if -1 == uuidIndex and -1 == barcodeIndex:
            for index in range(len(tokens)):
                if miscTCGA.looks_like_uuid(tokens[index]):
                    uuidIndex = index
                    break
            for index in range(len(tokens)):
                if miscTCGA.looks_like_barcode(tokens[index]):
                    barcodeIndex = index
                    break
            if -1 == uuidIndex and -1 == barcodeIndex:
                raise ValueError('did not find uuid and barcode')
        lineNum += 1
        for headerInfo in headerInfos:
            line = ['' for _ in range(12)]
            
            if -1 < uuidIndex and not miscTCGA.looks_like_uuid(tokens[uuidIndex]):
                print '\tskipping file w/out uuid... line #: ', lineNum, tokens[uuidIndex]
                continue
            if -1 == barcodeIndex:
                barcode = miscTCGA.uuid_to_barcode(tokens[uuidIndex])
            else:
                barcode = tokens[barcodeIndex]
            if not miscTCGA.looks_like_barcode(barcode):
                print '\tskipping file without barcode... line #: ', lineNum, barcode
                continue

            line[0] = miscTCGA.patientLevelCode(barcode)
            line[1] = miscTCGA.sampleLevelCode(barcode)
            line[2] = barcode
            if -1 < uuidIndex:
                line[3] = tokens[uuidIndex]
            line[4] = tokens[headerInfo.typeIndex]
            line[5] = techName
            
            archiveName = tokens[headerInfo.archiveNameIndex]
            fileName = tokens[headerInfo.fileNameIndex]
            fileIndex = sdrfFilename.rindex('/')
            if -1 == fileIndex:
                fileIndex = sdrfFilename.rindex('\\')
            archiveIndex = sdrfFilename.rindex('/', fileIndex - 1)
            if -1 == archiveIndex:
                archiveIndex = sdrfFilename.rindex('\\', fileIndex - 1)
            line[6] = sdrfFilename[:archiveIndex + 1] + archiveName + '/' + fileName
            line[7] = tokens[headerInfo.levelIndex]
            line[8] = archiveName
            line[11] = tokens[headerInfo.includeIndex]
            ri = recordInfo(line)
            level2ri = archiveInfo.setdefault(archiveName, {})
            levelInfo = level2ri.setdefault(ri.data_level, [set(), set()])
            ## also sanity check that we don't have duplicate barcodes ...
            if ('yes' == ri.annotation_types.lower()):
                levelInfo[0].add(ri)
                print '\tYES file marked as include... ', ri.barcode, ri.archive_name, fileName
            else:
                levelInfo[1].add(ri)
                print '\tNO file marked as not included... line #: ', lineNum, ri.barcode, ri.archive_name, fileName

    print '\tfound %d archives and %d data files ' % (len(archives), numFiles)

    print datetime.now(), 'completed getSDRFinfo %s' % (sdrfFilename)

def getFilesFromArchives(topDir, techName, techType, archiveInfo):
    print datetime.now(), "in getFilesFromArchives(): %s" % (topDir)
    if (not os.path.exists(topDir)):
        print '\t<%s> does not exist' % topDir
        return
    
    numClinicalFiles = 0
    level = techType.getDirectoryLevel()
    ## finally, at this level is where we look for "Level_1" potentArchives, so potentArchive
    ## will, for example, look like:
    ## .../TCGA/repositories/dcc-snapshot/coad/bcr/intgen.org/bio/clin/intgen.org_COAD.bio.Level_1.45.6.0
    baseDirs = path.path ( topDir )
    try:
        baseDirs = path.path ( topDir )
    except:
        traceback.print_exc()
        raise ValueError('problem with path %s' % (topDir))
    
    for baseDir in baseDirs.dirs():
        baseDir = baseDir + techType.getAddedPath()
        if (not os.path.exists(baseDir)):
            print '\tWARNING: <%s> does not exist' % baseDir
            continue

        try:
            potentArchives = path.path ( baseDir )
        except:
            traceback.print_exc()
            raise ValueError('problem with path %s' % (baseDir))
        
        print 'potentArchives: %s from %s' % (potentArchives, baseDir)
        for potentArchive in potentArchives.dirs():
            excludepathpiece = techType.getExcludedPathPiece()
            if excludepathpiece and excludepathpiece in potentArchive:
                continue
            print '\tchecking %s for files' % potentArchive

            if ( potentArchive.find(level) >= 0 ):
                numXmlFilesInArchive = 0
                numFilesInArchive = 0
                archiveName = parse_tcga.getFileNameFromPath(potentArchive)
                files = path.path ( potentArchive )
    
                level2ri = archiveInfo.setdefault(archiveName.lower(), {})
                levelInfo = level2ri.setdefault(int(level[-1]),[set(), set()])
                ## now we're finally down to some files ...
                for fName in files.files():
                    numFilesInArchive += 1
                    retVal = techType.includeFile((fName))
                    if not retVal[4]:
                        print retVal[5]
                        continue
                    print '\t\tincluding', fName
                    numXmlFilesInArchive += 1
    
                    ## update the return values
                    numClinicalFiles += 1
                    line = ['' for _ in range(12)]
                    line[0] = retVal[0]
                    line[5] = techName
                    line[6] = fName
                    line[7] = level
                    line[8] = archiveName
                    levelInfo[0].add(recordInfo(line))
                if ( numXmlFilesInArchive == 0 ):
                    if ( numFilesInArchive == 0 ):
                        print "\tWARNING !!! zero files of ANY type in this archive ??? ", archiveName
                    else:
                        print "\tWARNING !!! zero clinical XML files in this archive ??? ", archiveName
                else:
                    print "\t%d clinical xml files parsed in this archive " % numXmlFilesInArchive, archiveName

    
    print datetime.now(), "finished getFilesFromArchives().  file count: ", numClinicalFiles

def getArchiveData(tumorType, techName, techType, archiveInfo):
    topDir = techType.getTopDirectory(tumorType);
    print "topDir: %s" % topDir
    
    if techType.hasSDRFFile():
        sdrfFilename = parse_tcga.getSDRFilename(topDir)
        if (sdrfFilename == "NA"):
            print 'did not find any samples for %s' % tumorType
        else:
            getSDRFinfo(sdrfFilename, techName, techType, archiveInfo)
    else:
        getFilesFromArchives(topDir, techName, techType, archiveInfo) ## load up the information from the directory structure ...

def main(configName, tumorType):
    print datetime.now(), 'begin reading sdrfs'
    parse_tcga.initialize([None, configName])
    config = ConfigParser.ConfigParser()
    config.read(configName)

    ttFactory = technology_type_factory(config)
    techTypes = ttFactory.getTechnologyTypes()
    platform2archive = {}
    for techName in techTypes:
        if ('clinical' in techName):
            platform = 'bio'
        else:
            index = techName.find('/') + 1
            rindex = techName[:-1].rfind('/')
            platform = techName[index:rindex]
        platform2archive[platform] = {}
        getArchiveData(tumorType, techName, ttFactory.getTechnologyType(config, techName), platform2archive[platform.lower()])
    print datetime.now(), 'done reading sdrfs'
    return platform2archive

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
