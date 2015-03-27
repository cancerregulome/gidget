# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars
import arffIO
import miscClin
import miscTCGA
import tsvIO

# these are system modules
from datetime import datetime
from xml.dom import minidom
from xml.dom import Node

import os
import path
import string
import sys

featNamesLoaded = 0
featNamesDict = {}

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getLastBit(aName):

    ii = len(aName) - 1
    while (aName[ii] != '/'):
        ii -= 1

    # print ' <%s>    <%s> ' % ( aName, aName[ii+1:] )

    return (aName[ii + 1:])

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def newContentOK(oldString, newString, strName):

    # if the strings are the same, then that's fine ...
    if (newString.lower() == oldString.lower()):
        return (1)

    # try removing special characters from the 'new' string and see if it
    # matches
    newString2 = removeSpecialChars(newString)
    # print "     newString2: ", newString2
    if (newString2.lower() == oldString.lower()):
        return (1)

    print "         in newContentOK for <%s> :  newString = <%s>  oldString = <%s> " % (strName, newString, oldString)

    # NOT LETTING EVERYTHING THROUGH
    # --> 12jun13 : YES, letting everything through again ...
    if (1):
        print "         in newContentOK ... letting everything through now ... <%s> --> <%s> " % (oldString, newString)
        return (1)

    # first, if the patient has gone from living to deceased, that is ok
    try:
        if (newString.lower() == "deceased" and oldString.lower() == "living"):
            return (1)
    except:
        doNothing = 1

    # also going from tumor_free to "with tumor" is ok ...
    try:
        if (newString.lower() == "with tumor" and oldString.lower() == "tumor_free"):
            return (1)
    except:
        doNothing = 1

    # and I guess the other way around is also ok? (surgery?)
    try:
        if (newString.lower() == "tumor free" and oldString.lower() == "with_tumor"):
            return (1)
    except:
        doNothing = 1

    # also going from adjuvant to palliative is ok ...
    try:
        if (newString.lower() == "palliative" and oldString.lower() == "adjuvant"):
            return (1)
    except:
        doNothing = 1

    # next, if the feature is a number and it has increased, that is ok
    if (strName.lower().startswith("days_to") or (strName.lower().find(":days_to_") > 0)):
        try:
            iNew = int(newString)
            iOld = int(oldString)
            if (iNew > iOld):
                print "             keeping new days_to value ", strName, newString, oldString
                return (1)
            else:
                print "             NOT keeping new days_to value ", strName, newString, oldString
                return (0)
        except:
            doNothing = 1

    print "         STILL DIFFERENT ??? may need to look into this ... ", strName, newString, oldString
    return (0)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def removeSpecialChars(aLabel):

    bLabel = ''
    for ii in range(len(aLabel)):
        if (aLabel[ii] == ' '):
            bLabel += "_"
        elif (aLabel[ii] == "'"):
            bLabel += "_"
        elif (aLabel[ii] == '"'):
            bLabel += "_"
        elif (aLabel[ii] == ':'):
            bLabel += "_"
        elif (aLabel[ii] == '/'):
            bLabel += "_"
        # elif ( aLabel[ii] == '-' ):
        ##     bLabel += "_"
        elif (aLabel[ii] == '.'):
            bLabel += "_"
        elif (aLabel[ii] == ','):
            bLabel += "_"
        # elif ( aLabel[ii] == '>' ):
        ##     bLabel += "_"
        # elif ( aLabel[ii] == '<' ):
        ##     bLabel += "_"
        else:
            bLabel += aLabel[ii]

    ii = bLabel.find("_-_")
    while (ii >= 0):
        bLabel = bLabel[:ii] + bLabel[ii + 2:]
        ii = bLabel.find("_-_")

    ii = bLabel.find("__")
    while (ii >= 0):
        bLabel = bLabel[:ii] + bLabel[ii + 1:]
        ii = bLabel.find("__")

    if (bLabel != aLabel):
        if (0):
            print " in removeSpecialChars : <%s> <%s> " % (aLabel, bLabel)

    return (bLabel)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# Element names look like:
#	admin:bcr
# or	shared:tumor_tissue_site
# or	coad:histological_type
#
# the 	admin:xxx elements only have a single attribute, eg: xsd_ver=1.17
# the	shared:xxx and coad:xxx elements have 5 attributes:
#		owner=TSS
#		cde=2735776 (sometimes blank)
#		xsd_ver=1.8 (never blank)
#		tier=1 (rarely blank, otherwise 1 or 2)
#		procurement_status=Completed (or Not Applicable or Not Available)


def walk(parent, xmlDict, xmlFlags):

    # print " walking ... %s ... number of children: %d " % ( parent.nodeName,
    # len(parent.childNodes) )
    for node in parent.childNodes:

        # each node is either an ELEMENT_NODE or a TEXT_NODE
        if node.nodeType == Node.ELEMENT_NODE:

            # element name is node.nodeName

            # get the information out of this node
            attrs = node.attributes
            # print attrs.keys()
            for attrName in attrs.keys():
                attrNode = attrs.get(attrName)
                attrValue = attrNode.nodeValue
                if (attrName.lower() == "procurement_status"):
                    # attribute name is attrName, attribute value is attrValue
                    procStatus = attrValue

            # walk over any text nodes in the current node
            content = []
            for child in node.childNodes:
                if (child.nodeType == Node.TEXT_NODE):
                    content.append(child.nodeValue)

            if content:

                strContent = string.join(content)
                strContent = strContent.strip()
                ## try:
                ##     strContent = strContent.lower()
                ## except:
                ##     strContent = strContent

                if (len(strContent) > 0):
                    # element content is strContent

                    strName = str(node.nodeName)

                    # 22-oct-12 : added this to deal with non-ascii characters
                    # in the xml files from PRAD ...
                    newStr = str(strContent.encode('ascii', 'ignore'))
                    strContent = newStr

                    try:
                        a = str(strName)
                        b = str(strContent)
                        # print " walking ... <%s> <%s> " % ( str(strName),
                        # str(strContent) )
                    except:
                        try:
                            print "         strName : <%s> " % str(strName)
                        except:
                            doNothing = 1
                        try:
                            print "         strContent : <%s> " % str(strContent)
                        except:
                            doNothing = 1
                        print " "
                        print "         weird fatal error in walking xml file ???  skipping ... "
                        continue

                    # ignore certain fields ...
                    if (strName.lower().find("_of_form_completion") > 0):
                        print " FORM COMPLETION INFORMATION : ", strName, strContent
                        continue

                    if (strName.lower().find("_followup_barcode") > 0):
                        continue
                    if (strName.lower().find("_followup_uuid") > 0):
                        continue
                    if (strName.lower().startswith("rx:")):
                        continue
                    if (strName.lower().startswith("rad:")):
                        continue
                    if (strName.lower().endswith("_text")):
                        continue
                    if (strName.lower().endswith("_notes")):
                        continue

                    if (0):
                        if (attrValue.lower() == "not available"):
                            print " how can we have content if the procurement status is not available ??? !!! ", strName, strContent

                    insertNew = 1
                    if (strName in xmlDict.keys()):
                        if (str(xmlDict[strName]).lower() != str(strContent).lower()):
                            print " "
                            print " WARNING: <%s> is already in xmlDict keys and content is different ??? (%s vs %s) " % (strName, xmlDict[strName], strContent)
                            # print type(xmlDict[strName]), type(strContent)
                            for bKey in xmlDict.keys():
                                if (bKey.lower().find("_barcode") > 0):
                                    print "         ", bKey, xmlDict[bKey]

                            # -------------------------------------------------
                            # HERE ... we should decide whether to keep new
                            # content or not
                            if (newContentOK(str(xmlDict[strName]), str(strContent), strName)):
                                print "         keeping new content ... "
                            else:
                                # NEW as of 01mar13
                                insertNew = 0
                                print "         NOT keeping new content ... "
                                continue

                                # there are certain types of keys that we want
                                # to keep no matter what ...
                                if (strName.lower().find("days_to_") > 0):
                                    doNothing = 1
                                elif (strName.lower().find("vital_status") > 0):
                                    doNothing = 1
                                elif (strName.lower().find("eastern_cancer_oncology_group") > 0):
                                    doNothing = 1
                                elif (strName.lower().find("primary_therapy_outcome") > 0):
                                    doNothing = 1
                                elif (strName.lower().find("followup_treatment_success") > 0):
                                    doNothing = 1
                                elif (strName.lower().find("additional_treatment_completion_success_outcome") > 0):
                                    doNothing = 1
                                else:
                                    print " flagging this key as do-not-use \t %s \t %s \t %s " % (strName, str(xmlDict[strName]), str(strContent))
                                    xmlFlags[strName] = "DO NOT USE"

                            print " "

                    if (insertNew):
                        # this is where the "new content" is being put in ...
                        # print "     trying to add ... "
                        # first see if the strContent can be treated as an
                        # INTEGER
                        try:
                            xmlDict[strName] = int(strContent)
                        except:
                            # if that doesn't work, try as a FLOAT
                            try:
                                xmlDict[strName] = float(strContent)
                            # if that doesn't work, then it must be a STRING
                            except:
                                # is it a stage or grade string? (is already
                                # lowercase)
                                if (strContent.lower().startswith("stage ")):
                                    print "         startswith stage "
                                    # stage 'zero' is the same as 'in situ' ...
                                    if (strContent == "stage 0"):
                                        strContent = "tis"
                                    else:
                                        strContent = strContent[6:]
                                elif (strContent.lower().startswith("grade ")):
                                    print "         startswith grade "
                                    strContent = strContent[6:]
                                    try:
                                        iGrade = int(strContent)
                                        strContent = "g" + strContent
                                    except:
                                        doNothing = 1

                                try:
                                    if ((strName.lower().find("barcode") < 0) and (strName.lower().find("uuid") < 0)):
                                        fixContent = removeSpecialChars(
                                            strContent)
                                        xmlDict[strName] = str(fixContent)
                                    else:
                                        xmlDict[strName] = str(strContent)
                                except:
                                    print " FAILED to handle strContent for strName <%s> " % strName
                                    doNothing = 1

                    if (strName not in xmlDict.keys()):
                        print " FAILED To add <%s> as a key to the dictionary ??? " % strName
                    else:
                        # print " SUCCEEDED in adding <%s> as a key to the
                        # dictionary " % strName
                        doNothing = 1
                    # print ' xmlDict : ', xmlDict

            else:
                doNothing = 1
                if (0):
                    if (attrValue.lower() == "available"):
                        print " how can the procurement status be available but there is no content ??? ", attrValue
                        sys.exit(-1)

            # walk the child nodes
            walk(node, xmlDict, xmlFlags)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def writeDataFreezeLog(fhLog, fName):

    ## fName = ".../TCGA/repositories/dcc-snapshot/public/tumor/brca/bcr/nationwidechildrens.org/bio/clin/nationwidechildrens.org_BRCA.bio.Level_1.120.20.0/nationwidechildrens.org_clinical.TCGA-A2-A1FZ.xml"

    i1 = len(fName) - 1
    while (fName[i1] != '/'):
        i1 -= 1

    i2 = i1 - 1
    while (fName[i2] != '/'):
        i2 -= 1

    fileName = fName[i1 + 1:]
    # print " fileName = <%s> " % fileName
    archiveName = fName[i2 + 1:i1]
    # print " archiveName = <%s> " % archiveName

    i1 = fileName.find("TCGA-")
    i2 = fileName.find(".xml", i1)
    patientID = fileName[i1:i2]
    # print " patientID = <%s> " % patientID

    fhLog.write("%s\t%s\t%s\n" % (patientID, fileName, archiveName))

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getFeatNamesDict():
    global featNamesLoaded
    global featNamesDict

    if ( featNamesLoaded ):
        return
    try:
        fh = file (gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/bio_clin/featNames.tsv")
        for aLine in fh:
            tokenList = aLine.split()
            featName = tokenList[1]
            featType = tokenList[0]
            featNamesDict[featName] = featType
        fh.close()
        featNamesLoaded = 1

    except:
        featNamesLoaded = 2

    return

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def getFeatTypeByName ( aName ):
    global featNamesDict
    global featNamesLoaded
    if ( featNamesLoaded == 0 ):
        getFeatNamesDict()

    try:
        return ( featNamesDict[aName] )
    except:
        return ( "CLIN" )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def fixUpFeatureNames(allClinDict):

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
                featType = getFeatTypeByName ( aKey )
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
                print " ERROR in fixUpFeatureNames ??? key not found <%s> " % aKey
                newName = aKey

            newClinDict[newName] = allClinDict[aKey]

    return ( newClinDict )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# NOTE (01mar13): maybe this should be done using
# http://docs.python.org/2/library/xml.etree.elementtree.html
# instead ...
# or maybe I just need to use the "minidom" information more intelligently?
# according to this page http://docs.python.org/2/library/xml.dom.minidom.html
# "users who are not already proficient with DOM should consider using the
# xml.etree.ElementTree module for their XML processing instead"
#


def parseOneXmlFile(xmlFilename):

    ## xmlFilename = ".../TCGA/repositories/dcc-mirror/coad/bcr/intgen.org/bio/clin/intgen.org_COAD.bio.Level_1.41.3.0/intgen.org_clinical.TCGA-AA-3984.xml"

    print " "
    print " --------------------------------------------------------------------------------- "
    print " in parseOneXmlFile ... ", xmlFilename
    print " "

    doc = minidom.parse(xmlFilename)
    rootNode = doc.documentElement
    xmlDict = {}
    xmlFlags = {}
    walk(rootNode, xmlDict, xmlFlags)

    # remove any of the keys that were flagged as DO NOT USE ...
    if (len(xmlFlags) > 0):
        print len(xmlDict)
        print xmlFlags
        for aKey in xmlFlags.keys():
            del xmlDict[aKey]
        print len(xmlDict)

    # this is somewhat of a hack, but we are going to assign all
    # of the clinical data to the tumor sample for this patient
    # for the moment ...
    aKey = "shared:bcr_patient_barcode"
    barcode = xmlDict[aKey]

    # added July 10th 2012:
    # since we are trying to handle both tumor and normal samples,
    # we need to associate this patient information with a *sample*
    # barcode, so grab an associated tumor barcode here ...
    xmlDict[aKey] = miscTCGA.get_tumor_barcode(barcode)
    # print aKey, barcode, xmlDict[aKey]
    # sys.exit(-1)

    if (0):
        print " "
        print " "
        print " "
        for aKey in xmlDict.keys():
            print aKey, xmlDict[aKey]
        sys.exit(-1)

    return (xmlDict)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#
# this program loops over the tumor types in the cancerDirNames list and
# looks for all available *clinical*.xml files in the current "dcc-snapshot"
#
# all of the information is bundled into a dictionary called allClinDict
#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv) > 4 or len(sys.argv) < 3):
            print " Usage: %s <tumorType> <outSuffix> [snapshot-name] "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        else:

            tumorType = sys.argv[1].lower()
            if (tumorType == "coadread"):
                cancerDirNames = ['coad', 'read']
            else:
                cancerDirNames = [tumorType]

            outSuffix = sys.argv[2]

            if (len(sys.argv) == 4):
                snapshotName = sys.argv[3]
            else:
                snapshotName = "dcc-snapshot"

            ## outName = ".../TCGA/outputs/" + tumorType + "/" + tumorType + "." + outSuffix
            outName = "./" + tumorType + "." + outSuffix

    # open output header files ...
    fhHdr1 = file(outName + ".hdr1", 'w')
    fhHdr2 = file(outName + ".hdr2", 'w')

    fhHdr1.write("@START_TIMESTAMP %s" % (datetime.today().isoformat()))
    fhHdr2.write("@START_TIMESTAMP %s" % (datetime.today().isoformat()))
    for hh in range(len(sys.argv)):
        fhHdr1.write(" %s" % sys.argv[hh])
        fhHdr2.write(" %s" % sys.argv[hh])
    fhHdr1.write("\n")
    fhHdr2.write("\n")

    # and the output log file for the patient IDs, etc
    fhLog = file(outName + ".clinical.data_freeze.log", 'w')

    # initialize empty dictionary for clinical data
    allClinDict = {}

    # counter to keep track of the total # of clinical xml files parsed
    numClinicalFiles = 0

    # outer loop over tumor types (note that generally this should be looking
    # at only one tumor type at a time)
    for zCancer in cancerDirNames:
        print ' '
        print ' OUTER LOOP over CANCER TYPES ... ', zCancer

        ## topDir = ".../TCGA/repositories/dcc-snapshot/public/tumor/" + zCancer + "/bcr"
        topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + "/" + \
            snapshotName + "/public/tumor/" + zCancer + "/bcr"

        # get the contents of the bcr directory and loop over the subdirectories which
        # represent the specific BCR's (e.g. intgen.org and
        # nationwidechildrens.org)
        d1 = path.path(topDir)
        print d1
        print len(d1.dirs())
        for d1Name in d1.dirs():

            # NEW: 08mar13 ... intgen.org should be completely phased out by
            # now ...
            if (d1Name.find("intgen.org") >= 0):
                continue

            print '    ', d1Name

            # under the BCR-specific directory is a "bio" and then "clin" (or
            # at least it should)
            d1Name = d1Name + "/bio/clin"
            if (not os.path.exists(d1Name)):
                print "     <%s> does not exist " % d1Name
                continue

            print '      ', d1Name
            d2 = path.path(d1Name)

            # finally, at this level is where we look for "Level_1" archives, so d2Name
            # will, for example, look like:
            # .../TCGA/repositories/dcc-snapshot/coad/bcr/intgen.org/bio/clin/intgen.org_COAD.bio.Level_1.45.6.0
            for d2Name in d2.dirs():
                print '        ', d2Name
                if (d2Name.find("Level_1") >= 0):

                    archiveName = getLastBit(d2Name)
                    print " archive name : ", archiveName
                    numXmlFilesInArchive = 0
                    numFilesInArchive = 0

                    fhHdr1.write("@ARCHIVE %s\n" % archiveName)

                    d3 = path.path(d2Name)

                    # now we're finally down to some files ...
                    for fName in d3.files():

                        numFilesInArchive += 1

                        # we are only interested in XML files with the word "clinical"
                        # (not the "biospecimen" XML files)
                        if (not fName.endswith(".xml")):
                            continue
                        if (fName.find("clinical") < 0):
                            continue
                        print '            ', fName

                        fhHdr1.write("@DATAFILE %s\n" % fName)

                        # get (almost) all of the information out of this one
                        # xml file ...
                        oneDict = parseOneXmlFile(fName)
                        if (len(oneDict) > 0):
                            numXmlFilesInArchive += 1
                            writeDataFreezeLog(fhLog, fName)

                        # once we have the dict from this single xml file, we want
                        # to add all of this information to the allClinDict ...

                        # first get the keys that we already have in the
                        # allClinDict
                        currentAllKeys = allClinDict.keys()

                        print " "

                        # now loop over the keys from this new 'oneDict'
                        for aKey in oneDict.keys():

                            # if this key is not yet known to allClinDict, then
                            # create a blank list for this key
                            if (aKey not in currentAllKeys):
                                allClinDict[aKey] = []
                                print " new key : ", aKey

                            # if the list associated with this key is shorter than
                            # the current numClinicalFiles counter, then fill in
                            # the missing values with "NA"
                            if (len(allClinDict[aKey]) < numClinicalFiles):
                                while (len(allClinDict[aKey]) < numClinicalFiles):
                                    allClinDict[aKey] += ["NA"]

                            # finally, add the information from the new
                            # 'oneDict'
                            allClinDict[aKey] += [oneDict[aKey]]

                        # also make sure that any other keys (that are known to allClinDict
                        # but not to the new 'oneDict') are brought up to the
                        # correct length ...
                        for bKey in currentAllKeys:
                            if (bKey in oneDict.keys()):
                                continue
                            while (len(allClinDict[bKey]) < numClinicalFiles):
                                allClinDict[bKey] += ["NA"]
                            allClinDict[bKey] += ["NA"]

                        # finally increment the counter ...
                        numClinicalFiles += 1
                        print " NUMBER : ", numClinicalFiles

                    if (numXmlFilesInArchive == 0):
                        if (numFilesInArchive == 0):
                            print "             WARNING !!! zero files of ANY type in this archive ??? ", archiveName
                        else:
                            print "             WARNING !!! zero clinical XML files in this archive ??? ", archiveName
                    else:
                        print "             %d clinical xml files parsed in this archive " % numXmlFilesInArchive, archiveName

    print " "
    print " "
    print " "
    print " DONE parsing "
    print " "
    print " "
    print allClinDict.keys()
    print len(allClinDict.keys())
    print numClinicalFiles
    if (numClinicalFiles == 0):
        print " no clinical data found ??? "
        sys.exit(-1)

    # and close the log file ...
    fhLog.close()

    # now let's look at all of this ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    # now look for duplicate keys ...
    # (note this also abbreviates the key names)
    (allClinDict) = miscClin.removeDuplicateKeys(allClinDict)

    # add prefixes onto feature names and standardize ...
    (allClinDict) = fixUpFeatureNames(allClinDict)

    if (0):
        # and remove uninformative keys ...
        (allClinDict) = miscClin.removeConstantKeys(allClinDict)

    # take another look ...
    (naCounts, otherCounts) = miscClin.lookAtClinDict(allClinDict)

    # now let's come up with a new ordering of the keys based on the naCounts ...
    # --> actually, let's NOT change the ordering ... it makes it much harder
    # to see if/when things change ...
    if (1):
        tmpCounts = [max(naCounts)] * len(naCounts)
        naCounts = tmpCounts
    bestKeyOrder = miscClin.getBestKeyOrder(allClinDict, naCounts)

    # finally, let's write out a tsv file ...
    tsvIO.writeTSV_clinical(allClinDict, bestKeyOrder, outName)

    # and the header file ...
    tsvIO.writeAttributeHeader(allClinDict, bestKeyOrder, fhHdr2)

    # and an arff file too ...
    arffIO.writeARFF(allClinDict, bestKeyOrder, sys.argv[0], outName)

    # once we're done, we stamp and close the header files ...
    fhHdr1.write("@END_TIMESTAMP %s %d features %d patients" %
                 (datetime.today().isoformat(), len(bestKeyOrder), numClinicalFiles))
    fhHdr2.write("@END_TIMESTAMP %s %d features %d patients" %
                 (datetime.today().isoformat(), len(bestKeyOrder), numClinicalFiles))

    fhHdr1.close()
    fhHdr2.close()

    print " "
    print " "
    print " "
    print " ok, really DONE now "
    print " "
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
