'''
Created on Aug 2, 2012

@author: michael
'''
from env import gidgetConfigVars

from xml.dom  import minidom
from xml.dom  import Node

from datetime import datetime
import os
import string
import sys
import traceback

from technology_type import technology_type
import arffIO
import miscTCGA
import miscClin
import path
import tsvIO

class clinical(technology_type):
    '''
    classdocs
    '''

    def __init__(self, config, platformID):
        '''
        Constructor
        '''
        technology_type.__init__(self, config, platformID)
        self.configuration.update(config.items('clinical'))
        ## initialize empty dictionary for clinical data
        self.allClinDict = {}
        self.curFileCount = 0
        ## get the stings needed for processing tags
        self.excludePrefix = self.configuration['excludeprefix'].split(',')
        self.excludeSuffix = self.configuration['excludesuffix'].split(',')
        self.excludeStrings = self.configuration['excludestrings'].split(',')
        self.includeStrings = self.configuration['includestrings'].split(',')
        self.removePrefix = [pre.split(':') for pre in self.configuration['removeprefix'].split(',')]
        self.sharedBarcodeKey = self.configuration['sharedbarcode']
        self.featNamesLoaded = 0
        self.featNamesDict = {}

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def includeFile(self, tokens):
        ## we are only interested in XML files with the word "clinical"
        ## (not the "biospecimen" XML files)
        fName = tokens
        if ( not fName.endswith(".xml") ): 
            mess = '(e) NOT including this non-xml file ... ', fName
            return (None, fName, None, None, False, mess)
        if ( fName.find("clinical") < 0 ): 
            mess = '(e) NOT including this non-clinical file ... ', fName
            return (None, fName, None, None, False, mess)
        barcode = fName.rstrip('.xml')
        barcode = barcode[barcode.rindex('.') + 1:]
        return (barcode, fName, None, None, True, None)

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def removeSpecialChars(self, aLabel):
        bLabel = ''
        for ii in range(len(aLabel)):
            if ( aLabel[ii] == ' ' ):
                bLabel += "_"
            elif ( aLabel[ii] == "'" ):
                bLabel += "_"
            elif ( aLabel[ii] == '"' ):
                bLabel += "_"
            elif ( aLabel[ii] == ':' ):
                bLabel += "_"
            elif ( aLabel[ii] == '/' ):
                bLabel += "_"
            ## elif ( aLabel[ii] == '-' ):
            ##     bLabel += "_"
            elif ( aLabel[ii] == '.' ):
                bLabel += "_"
            elif ( aLabel[ii] == ',' ):
                bLabel += "_"
            ## elif ( aLabel[ii] == '>' ):
            ##     bLabel += "_"
            ## elif ( aLabel[ii] == '<' ):
            ##     bLabel += "_"
            else:
                bLabel += aLabel[ii]
    
        ii = bLabel.find("_-_")
        while ( ii >= 0 ):
            bLabel = bLabel[:ii] + bLabel[ii+2:]
            ii = bLabel.find("_-_")
    
        ii = bLabel.find("__")
        while ( ii >= 0 ):
            bLabel = bLabel[:ii] + bLabel[ii+1:]
            ii = bLabel.find("__")
    
        if ( bLabel != aLabel ):
            print "\t\t\tin removeSpecialChars : <%s> <%s> " % ( aLabel, bLabel )
    
        return ( bLabel )

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def newContentOK(self, oldString, newString):
        print "\tnewString = <%s>\toldString = <%s> " % ( newString, oldString )
    
        if True:
            print "\tin newContentOK ... letting everything through now ... <%s> --> <%s> " % ( oldString, newString )
            return ( 1 )

        try:
            if ( newString == "Dead"  and  oldString == "Alive" ):
                return ( 1 )
            else:
                return ( 0 )
        except:
            pass
    
        ## also going from tumor_free to "with tumor" is ok ...
        try:
            if ( newString == "with tumor"  and  oldString == "tumor_free" ):
                return ( 1 )
        except:
            pass
    
        ## and I guess the other way around is also ok? (surgery?)
        try:
            if ( newString == "tumor free"  and  oldString == "with_tumor" ):
                return ( 1 )
        except:
            pass
    
        ## also going from adjuvant to palliative is ok ...
        try:
            if ( newString == "palliative"  and  oldString == "adjuvant" ):
                return ( 1 )
        except:
            pass

        try:
            iNew = int(newString)
            iOld = int(oldString)
            if ( iNew > iOld ):
                return ( 1 )
            else:
                return ( 0 )
        except:
            pass

        ## finally, try removing special characters from the 'new' string and see if it matches
        newString2 = self.removeSpecialChars(newString)
        print "     newString2: ", newString2
        if ( newString2 == oldString ):
            return ( 1 )
    
        print "         STILL DIFFERENT ??? CHECK HERE "
        print " "
        return ( 0 )
    
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    # Element names look like:
    #       admin:bcr
    # or    shared:tumor_tissue_site
    # or    coad:histological_type
    #
    # the   admin:xxx elements only have a single attribute, eg: xsd_ver=1.17
    # the   shared:xxx and coad:xxx elements have 5 attributes:
    #               owner=TSS
    #               cde=2735776 (sometimes blank)
    #               xsd_ver=1.8 (never blank)
    #               tier=1 (rarely blank, otherwise 1 or 2)
    #               procurement_status=Completed (or Not Applicable or Not Available)
    
    def walk(self, parent, xmlDict, xmlFlags):
        ## print " walking ... %s ... number of children: %d " % ( parent.nodeName, len(parent.childNodes) )
        for node in parent.childNodes:
            ## each node is either an ELEMENT_NODE or a TEXT_NODE
            if node.nodeType == Node.ELEMENT_NODE:
    
                ## element name is node.nodeName
    
                ## get the information out of this node
                attrs = node.attributes
                ## print attrs.keys()
                for attrName in attrs.keys():
                    attrNode = attrs.get(attrName)
                    attrValue = attrNode.nodeValue
                    if ( attrName.lower() == "procurement_status" ):
                        ## attribute name is attrName, attribute value is attrValue
                        # procStatus = attrValue
                        pass
    
                ## walk over any text nodes in the current node
                content = []
                for child in node.childNodes:
                    if ( child.nodeType == Node.TEXT_NODE ):
                        content.append ( child.nodeValue )
    
                if content:
    
                    strContent = string.join ( content )
                    strContent = strContent.strip()
#                    try:
#                        strContent = strContent.lower()
#                    except:
#                        strContent = strContent
    
                    if ( len(strContent) > 0 ):
                        ## element content is strContent
    
                        strName = str ( node.nodeName )


                        ## 22-oct-12 : added this to deal with non-ascii characters
                        ## in the xml files from PRAD ...
                        newStr = str ( strContent.encode('ascii','ignore') )
                        strContent = newStr
    
                        try:
                            _ = str(strName)
                            _ = str(strContent)
                            ## print " walking ... <%s> <%s> " % ( str(strName), str(strContent) )
                        except:
                            try:
                                print "         strName : <%s> " % str(strName)
                            except:
                                pass
                            try:
                                print "         strContent : <%s> " % str(strContent)
                            except:
                                pass
                            print " "
                            print "         weird fatal error in walking xml file ???  skipping ... "
                            continue
    
                        ## ignore certain fields ...
                        toExclude = False
                        for exclude in self.excludePrefix:
                            if strName.lower().startswith(exclude):
                                toExclude = True
                                break
                        if toExclude:
                            continue

                        for exclude in self.excludeSuffix:
                            if strName.lower().endswith(exclude):
                                toExclude = True
                                break
                        if toExclude:
                            continue

                        for exclude in self.excludeStrings:
                            excludeFields = exclude.split(':')
                            if excludeFields[0] in strName.lower():
                                if 2 == len(excludeFields):
                                    print '%s :  %s %s' % (excludeFields[1], strName, strContent)
                                toExclude = True
                                break
                        if toExclude:
                            continue
    
                        if ( 0 ):
                            if ( attrValue.lower() == "not available" ):
                                print " how can we have content if the procurement status is not available ??? !!! ", strName, strContent
    
                        if ( strName in xmlDict.keys() ):
                            if ( str(xmlDict[strName]).lower() != str(strContent).lower() ):
                                print " "
                                print "WARNING: <%s> is already in xmlDict keys and content is different ??? (%s vs %s) " % ( strName, xmlDict[strName], strContent )
                                print type(xmlDict[strName]), type(strContent)
                                for bKey in xmlDict.keys():
                                    if ( bKey.find("_barcode") > 0 ):
                                        print "         ", bKey, xmlDict[bKey]
    
                                if (self.newContentOK (str(xmlDict[strName]), str(strContent))):
                                    print "\t\t\tkeeping new content ... "
                                else:
                                    ## there are certain types of keys, includeStrings, that we want to keep no matter what ...
                                    dontUse = True
                                    for include in self.includeStrings:
                                        if include in strName.lower():
                                            dontUse = False
                                            break 
                                    if dontUse:
                                        print "\t\t\tflagging this key as do-not-use \t %s \t %s \t %s " % ( strName, str(xmlDict[strName]), str(strContent) )
                                        xmlFlags[strName] = "DO NOT USE"
    
                                print " "

                        ## print "\t\t\ttrying to add ... "
                        ## first see if the strContent can be treated as an INTEGER
                        try:
                            xmlDict[strName] = int ( strContent )
                        except:
                            ## if that doesn't work, try as a FLOAT
                            try:
                                xmlDict[strName] = float ( strContent )
                            ## if that doesn't work, then it must be a STRING
                            except:
                                ## is it a stage or grade string? (is already lowercase)
                                for prefix in self.removePrefix:
                                    if strContent.lower().startswith(prefix[0]):
                                        print "\t\t\tstarts with", prefix[0]
                                        try:
                                            strContent = strContent[len(prefix[0]):]
                                            twoper = prefix[1].split('%')
                                            # the logic here is getting a little twisted to deal with 'Stage 0a' vs 'Stage 0'.  if more cases come up
                                            # may need to rethink how to do this --mm 2014-05-23
                                            if twoper[1]:
                                                if strContent:
                                                    _ = int(strContent)
                                                elif 'i' == twoper[0]:
                                                    strContent = twoper[1]
                                                if 'a' == twoper[0]:
                                                    strContent = twoper[1] + strContent
                                                elif 'r' == twoper[0]:
                                                    strContent = twoper[1]
                                        except:
                                            pass
                                        break;
                                        
                                try:
                                    if ( (strName.lower().find("barcode")<0) and (strName.lower().find("uuid")<0) ):
                                        fixContent = self.removeSpecialChars ( strContent )
                                        xmlDict[strName] = str ( fixContent )
                                    else:
                                        xmlDict[strName] = str ( strContent )
                                except:
                                    print "FAILED to handle strContent for strName <%s> " % strName
    
                        if ( strName not in xmlDict.keys() ):
                            print "FAILED To add <%s> as a key to the dictionary ??? " % strName
                        else:
                            ## print "\t\t\tSUCCEEDED in adding <%s> as a key to the dictionary " % strName
                            pass
                        ## print ' xmlDict : ', xmlDict
    
                else:
                    if ( 0 ):
                        if ( attrValue.lower() == "available" ):
                            raise ValueError("how can the procurement status be available but there is no content ??? %s" % str(attrValue))
    
            ## walk the child nodes
            self.walk(node, xmlDict, xmlFlags)


    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    def parseOneXmlFile (self, xmlFilename):
    
        ## xmlFilename = ".../TCGA/repositories/dcc-mirror/coad/bcr/intgen.org/bio/clin/intgen.org_COAD.bio.Level_1.41.3.0/intgen.org_clinical.TCGA-AA-3984.xml"
    
        print " "
        print "\t\t--------------------------------------------------------------------------------- "
        print "\t\tin parseOneXmlFile ... ", xmlFilename
        print " "
        doc = minidom.parse ( xmlFilename )
        rootNode = doc.documentElement
        xmlDict = {}
        xmlFlags = {}
        self.walk( rootNode, xmlDict, xmlFlags )
    
        ## remove any of the keys that were flagged as DO NOT USE ...
        if ( len(xmlFlags) > 0 ):
            print '\t\t\tbefore size of dict: ', len(xmlDict)
            print '\t\t\t', xmlFlags
            for aKey in xmlFlags.keys():
                del xmlDict[aKey]
            print '\t\t\tafter size of dict: ', len(xmlDict)
    
        ## this is somewhat of a hack, but we are going to assign all
        ## of the clinical data to the tumor sample for this patient
        ## for the moment ...
        aKey = self.sharedBarcodeKey
        barcode = xmlDict[aKey]
    
        ## added July 10th 2012:
        ## since we are trying to handle both tumor and normal samples,
        ## we need to associate this patient information with a *sample*
        ## barcode, so grab an associated tumor barcode here ...
        xmlDict[aKey] = miscTCGA.get_tumor_barcode ( barcode )
        ## print aKey, barcode, xmlDict[aKey]
        ## sys.exit(-1)
    
        if ( 0 ):
            print " "
            print " "
            print " "
            for aKey in xmlDict.keys():
                print '\t\t\t', aKey, xmlDict[aKey]
            sys.exit(-1)
    
        return ( xmlDict )

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getFeatNamesDict(self):
        if ( self.featNamesLoaded ):
            return
        try:
            featureNamesFilename = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/bio_clin/featNames.tsv"
            fh = file (featureNamesFilename)
            for aLine in fh:
                tokenList = aLine.split()
                featName = tokenList[1]
                featType = tokenList[0]
                self.featNamesDict[featName] = featType
            fh.close()
            self.featNamesLoaded = 1
    
        except:
            self.featNamesLoaded = 2
    
        return
    
    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    def getFeatTypeByName (self, aName ):
        if ( self.featNamesLoaded == 0 ):
            self.getFeatNamesDict()
    
        try:
            print 'looking at featNamesDict[] for %s' % (aName)
            return ( self.featNamesDict[aName] )
        except:
            return ( "CLIN" )
    
    # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    def fixUpFeatureNames(self, allClinDict):
    
        print " "
        print " in fixUpFeatureNames ... "
    
        keyList = allClinDict.keys()
        newClinDict = {}
    
        for aKey in keyList:
    
            ## if the feature name already looks like B:SAMP:etc or N:CLIN:etc
            ## then we don't do anything
            if ( aKey[1]==":" and aKey[6]==":" ):
                newName = aKey
    
            else:
                try:
                    featType = self.getFeatTypeByName ( aKey )
                    print featType
                    info = miscClin.lookAtKey ( allClinDict[aKey] )
                    print aKey
                    print info
                    if ( info[0] == "NOMINAL" ):
                        if ( info[3] == 2 ):
                            newName = "B:" + featType + ":" + aKey + ":::::"
                        else:
                            newName = "C:" + featType + ":" + aKey + ":::::"
                    elif ( info[0] == "NUMERIC" ):
                        newName = "N:" + featType + ":" + aKey + ":::::"
                    else:
                        sys.exit(-1)
                except:
                    traceback.print_exc(limit=5)
                    print " ERROR in fixUpFeatureNames ??? key not found <%s> " % aKey
                    newName = aKey
    
                newClinDict[newName] = allClinDict[aKey]
    
        return ( newClinDict )

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def postprocess(self, dataMatrix, geneList, sampleList):
        ## now let's look at all of this ...
        miscClin.lookAtClinDict ( self.allClinDict )
    
        ## now look for duplicate keys ...
        ## (note this also abbreviates the key names)
        ( self.allClinDict ) = miscClin.removeDuplicateKeys ( self.allClinDict )
    
        # add prefixes onto feature names and standardize ...
        (self.allClinDict) = self.fixUpFeatureNames(self.allClinDict)

        ## take another look ...
        ( naCounts, _ ) = miscClin.lookAtClinDict ( self.allClinDict )
    
        ## now let's come up with a new ordering of the keys based on the naCounts ...
        ## --> actually, let's NOT change the ordering ... it makes it much harder
        ##     to see if/when things change ...
        if ( 1 ):
            tmpCounts = [max(naCounts)] * len(naCounts)
            naCounts = tmpCounts
        bestKeyOrder = miscClin.getBestKeyOrder ( self.allClinDict, naCounts )
        dataD = {}
        dataD['clinDict'] = self.allClinDict
        dataD['bestKeyOrder'] = bestKeyOrder
        return dataD

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def readDataFile(self, dataMatrix, fullPathName, fileName, filename2sampleInfo, sampleIndex):
        print "\t\t", datetime.now(), "reading data for %s" % str(self)
        self._readPatternDesign()
        (barcode, info, _) = filename2sampleInfo[fileName][0]
        print '\t\tbarcode: %s info: %s' % (barcode, info)

        ## get (almost) all of the information out of this one xml file ...
        try:
            oneDict = self.parseOneXmlFile(fullPathName)
        except Exception as e:
            raise ValueError('Failed to read the xml file %s'% fullPathName, e)

        ## once we have the dict from this single xml file, we want
        ## to add all of this information to the allClinDict ...

        ## first get the keys that we already have in the allClinDict
        currentAllKeys = self.allClinDict.keys()

        ## now loop over the keys from this new 'oneDict'
        for aKey in oneDict.keys():

            ## if this key is not yet known to allClinDict, then
            ## create a blank list for this key
            if ( aKey not in currentAllKeys ):
                self.allClinDict[aKey] = []
                print " new key : ", aKey

            ## if the list associated with this key is shorter than
            ## the current self.curFileCount counter, then fill in
            ## the missing values with "NA"
            if ( len(self.allClinDict[aKey]) < self.curFileCount ):
                while ( len(self.allClinDict[aKey]) < self.curFileCount ):
                    self.allClinDict[aKey] += [ "NA" ]

            ## finally, add the information from the new 'oneDict'
            self.allClinDict[aKey] += [ oneDict[aKey] ]

        ## also make sure that any other keys (that are known to allClinDict
        ## but not to the new 'oneDict') are brought up to the correct length ...
        for bKey in currentAllKeys:
            if ( bKey in oneDict.keys() ): continue
            while ( len(self.allClinDict[bKey]) < self.curFileCount ):
                self.allClinDict[bKey] += [ "NA" ]
            self.allClinDict[bKey] += [ "NA" ]

        ## finally increment the counter ...
        self.curFileCount += 1
        print " NUMBER : ", self.curFileCount

        print "\t\t", datetime.now(), "finished reading %i keys for barcode %s. " % (len(oneDict), barcode)
        return None, [barcode]

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getAddedPath(self):
        return self.configuration["addpath"]
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getExcludedPathPiece(self):
        return self.configuration["excludepiece"]
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getTopDirectory(self, tumorType):
        return self.configuration["topdir"] % (self.configuration['snapshot'], self.configuration['basedirectorybranch'], tumorType)
        
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    def getFilesFromArchives(self, topDir):
        print datetime.now(), "in getFilesFromArchives(): %s" % (topDir)
        if (not os.path.exists(topDir)):
            print '\t<%s> does not exist' % topDir
            return 0, None, None, []
        numClinicalFiles = 0
        filename2sampleInfo = {}
        archiveList = []
        level = self.getDirectoryLevel()
        ## finally, at this level is where we look for "Level_1" potentArchives, so potentArchive
        ## will, for example, look like:
        ## .../TCGA/repositories/dcc-snapshot/coad/bcr/intgen.org/bio/clin/intgen.org_COAD.bio.Level_1.45.6.0
        baseDirs = path.path ( topDir )
        try:
            baseDirs = path.path ( topDir )
        except:
            traceback.print_exc()
            raise ValueError('problem with path %s' % (topDir))
        
        localTopDirs = []
        for baseDir in baseDirs.dirs():
            baseDir = baseDir + self.getAddedPath()
            if (not os.path.exists(baseDir)):
                print '\tWARNING: <%s> does not exist' % baseDir
                continue
    
            localTopDirs += [baseDir]
            try:
                potentArchives = path.path ( baseDir )
            except:
                traceback.print_exc()
                raise ValueError('problem with path %s' % (baseDir))
            
            print 'potentArchives: %s from %s' % (potentArchives, baseDir)
            for potentArchive in potentArchives.dirs():
                excludepathpiece = self.getExcludedPathPiece()
                if excludepathpiece and excludepathpiece in potentArchive:
                    continue
                print '\tchecking %s for files' % potentArchive
                if ( potentArchive.find(level) >= 0 ):
                    numXmlFilesInArchive = 0
                    numFilesInArchive = 0
                    archiveName = potentArchive[potentArchive.rfind('/') + 1:]
                    files = path.path ( potentArchive )
        
                    ## now we're finally down to some files ...
                    for fName in files.files():
                        numFilesInArchive += 1
                        retVal = self.includeFile((fName))
                        if not retVal[4]:
                            print retVal[5]
                            continue
                        print '\t\tincluding', fName
                        numXmlFilesInArchive += 1
        
                        ## update the return values
                        numClinicalFiles += 1
                        filename2sampleInfo[fName[fName.rfind('/') + 1:]] = [(retVal[0], retVal[3], potentArchive)]
                        archiveList.append(archiveName)
                    
                    if ( numXmlFilesInArchive == 0 ):
                        if ( numFilesInArchive == 0 ):
                            print "\tWARNING !!! zero files of ANY type in this archive ??? ", archiveName
                        else:
                            print "\tWARNING !!! zero clinical XML files in this archive ??? ", archiveName
                    else:
                        print "\t%d clinical xml files parsed in this archive " % numXmlFilesInArchive, archiveName
    
        
        print datetime.now(), "finished getFilesFromArchives().  file count: ", numClinicalFiles
        return numClinicalFiles, filename2sampleInfo, archiveList, localTopDirs

    def writeMatrix(self, matrixParams, outFilename):
        print datetime.now(), 'writing out data matrix to %s' % outFilename
        ## write out the tsv file ...
        allClinDict = matrixParams['clinDict']
        bestKeyOrder = matrixParams['bestKeyOrder']
        tsvIO.writeTSV_clinical ( allClinDict, bestKeyOrder, outFilename )
    
        ## and the header file ...
        logFile = open(outFilename + self.configuration['logext'], 'w')
        logFile.write ("@START_TIMESTAMP %s %s\n" % ( datetime.today().isoformat(), outFilename))
        tsvIO.writeAttributeHeader(allClinDict, bestKeyOrder, logFile)
    
        ## and an arff file too ...
        arffIO.writeARFF(allClinDict, bestKeyOrder, sys.argv[0], outFilename)
    
        ## once we're done, we stamp and close the header files ...
        logFile.write ("@END_TIMESTAMP %s %d features %d patients\n" % ( datetime.today().isoformat(), len(bestKeyOrder), self.curFileCount))
        logFile.flush()
    
        logFile.close()
        print datetime.now(), 'finished writing out data matrix\n'
