import commands
from datetime import datetime
import os.path
import re
import sys
import time

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

NA_VALUE = -999999
uuidMetadataScript='/titan/cancerregulome11/TCGA/repositories/uuids/get_metadata.sh'
uuidMappingFile = "/titan/cancerregulome11/TCGA/repositories/uuids/metadata.current.txt"
uuid_re=re.compile('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
barcodes=re.compile('^TCGA-\w{2}-\w{4}(-\w{2}[a-zA-Z](-\w{2}[a-zA-Z]?(-\w{4}(-[0-9]{2})*)*)*)*$')

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def patientLevelCode ( barcode ):
    return ( barcode[:12] )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def sampleLevelCode ( barcode ):
    return ( barcode[:15] )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# 012345678901234567890123456
# TCGA-BF-A1PX-01A-41-A20M-20
# THCA-BJ-A0Z3-TP


def fixTCGAbarcode(barcode, zCancer=""):

    ## print " in fixTCGAbarcode ... <%s> " % barcode

    # make sure that the barcode doesn't start with the tumor type
    # abbreviation instead of TCGA ...
    if (not barcode.startswith("TCGA")):

        if (zCancer != ""):
            tC = zCancer.upper()
            if (barcode.startswith(tC)):
                barcode = "TCGA" + barcode[len(tC):]
        else:
            ii = barcode.find("-")
            if (ii > 0):
                barcode = "TCGA" + barcode[ii:]

        # if it still has TCGA in it, but not at the beginning
        # something more will need to be done ... (not yet implemented)
        if (barcode.find("TCGA") > 0):
            print " FATAL ERROR in fixTCGAbarcode ... <%s> " % barcode
            sys.exit(-1)

    # this first part just makes sure that the delimiter is a '-'
    # rather than a '.' (which had been showing up in other data sources)
    if ( barcode.startswith("TCGA") ):
        if ( barcode[4] != '-' ):
            delim = barcode[4]
            newCode = ''
            for kk in range(len(barcode)):
                if ( barcode[kk] != delim ):
                    newCode += barcode[kk]
                else:
                    newCode += '-'
            ## print barcode, newCode
            barcode = newCode

    # here we want to undo the things that the Broad likes to do where
    # they replace '-01' with '-TP' etc ...
    if (barcode.startswith("TCGA")):
        if (len(barcode) >= 13):
            if (barcode[12:].startswith("-TP")):
                barcode = barcode[:12] + "-01"
            elif (barcode[12:].startswith("-TRBM")):
                barcode = barcode[:12] + "-04"
            elif (barcode[12:].startswith("-TR")):
                barcode = barcode[:12] + "-02"
            elif (barcode[12:].startswith("-TBM")):
                barcode = barcode[:12] + "-09"
            elif (barcode[12:].startswith("-TB")):
                barcode = barcode[:12] + "-03"
            elif (barcode[12:].startswith("-TAP")):
                barcode = barcode[:12] + "-05"
            elif (barcode[12:].startswith("-TM")):
                barcode = barcode[:12] + "-06"
            elif (barcode[12:].startswith("-TAM")):
                barcode = barcode[:12] + "-07"
            elif (barcode[12:].startswith("-THOC")):
                barcode = barcode[:12] + "-08"
            elif (barcode[12:].startswith("-NB")):
                barcode = barcode[:12] + "-10"
            elif (barcode[12:].startswith("-NT")):
                barcode = barcode[:12] + "-11"
            elif (barcode[12:].startswith("-CELLC")):
                barcode = barcode[:12] + "-20"

    ## print "         --> <%s> " % barcode
    return ( barcode )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def parseTCGAbarcode ( barcode ):

    if ( barcode.startswith("TCGA") ):
        if ( barcode[4] != '-' ):
            delim = barcode[4]
            newCode = ''
            for kk in range(len(barcode)):
                if ( barcode[kk] != delim ):
                    newCode += barcode[kk]
                else:
                    newCode += '-'
            print barcode, newCode
            barcode = newCode

    if ( not barcode.startswith("TCGA-") ):
        print " ERROR in parseTCGAbarcode ... not a TCGA barcode !!! ", barcode
        # just return the input barcode in the 'sample' slot ...
        return ( '', '', barcode, '', '', '', '', '' )
        sys.exit(-1)

    bLen = len(barcode)
    if ( bLen < 15 ):
        print " ERROR in parseTCGAbarcode ... too short ??? ", barcode, bLen
        sys.exit(-1)
    if ( bLen > 30 ):
        print " ERROR in parseTCGAbarcode ... too long ??? ", barcode, bLen
        sys.exit(-1)

    # TCGA-A2-A04P-01A-31W-A050-09-1
    # 012345678901234567890123456789

    delim = barcode[4]
    if ( barcode[7] != delim ):
        print " ERROR in parseTCGAbarcode ??? ", barcode
        sys.exit(-1)
    if ( barcode[12] != delim ):
        print " ERROR in parseTCGAbarcode ??? ", barcode
        sys.exit(-1)
    if ( bLen > 17 ):
        if ( barcode[16] != delim ):
            print " ERROR in parseTCGAbarcode ??? ", barcode
            sys.exit(-1)

    site = barcode[5:7]
    patient = barcode[8:12]
    sample = barcode[13:15]

    vial = ''
    portion = ''
    analyte = ''
    plate = ''
    center = ''

    # typical full barcode looks like this:
    #                111111111122222222
    #      0123456789012345678901234567
    #      TCGA-A1-A0SE-01A-11R-A085-13
    # need 12 characters to identify patient
    #      16 characters to identify sample
    #      20 characters to identify aliquot
    #      25 characters to include plate id
    #      28 characters to include cgcc id

    if (bLen > 15):
        vial = barcode[15]  # single character
    if (bLen > 18):
        portion = barcode[17:19]  # two digits
    if (bLen > 19):
        analyte = barcode[19]  # single character
    if (bLen > 24):
        plate = barcode[21:25]  # four char/digit plate id
    if (bLen > 27):
        center = barcode[26:28]  # two digit center id

    return ( site, patient, sample, vial, portion, analyte, plate, center )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def rebuildTCGAbarcode ( barcodeInfo ):

    if ( len(barcodeInfo) != 8 ):
        print " ERROR in rebuildTCGAbarcode ... not enough information "
        sys.exit(-1)

    tmpA = "TCGA-%2s-%4s-%2s%1s-%2s%1s-%4s-%2s" % \
                ( barcodeInfo[0], barcodeInfo[1], barcodeInfo[2],
                  barcodeInfo[3], barcodeInfo[4], barcodeInfo[5],
                  barcodeInfo[6], barcodeInfo[7] )

    tmpB = ""
    for ii in range(len(tmpA)):
        if ( tmpA[ii] == ' ' ):
            tmpB += '0'
        else:
            tmpB += tmpA[ii]

    return ( tmpB )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def lookAtBarcodes ( barcodeList ):

    print " looking at %d barcodes ... " % ( len(barcodeList) )

    typeDict = {}
    for aCode in barcodeList:
        if ( len(aCode) > 14 ):
            iType = int ( aCode[13:15] )
            if ( iType not in typeDict.keys() ):
                typeDict[iType] = 0
            typeDict[iType] += 1

    print " sample types : ", typeDict

    if ( len(typeDict.keys() ) > 1 ):
        sampleDict = {}
        for aCode in barcodeList:
            aSample = aCode[5:12]
            iType = int ( aCode[13:15] )
            if ( aSample not in sampleDict.keys() ):
                sampleDict[aSample] = [ ]
            sampleDict[aSample] += [ iType ]

        sampleList = sampleDict.keys()
        sampleList.sort()
        pairedList = []
        for aSample in sampleList:
            # print "    %7s : " % aSample, sampleDict[aSample]
            sampleDict[aSample].sort()
            if ( sampleDict[aSample][0] < 10 ):
                if ( len(sampleDict[aSample]) > 1 ):
                    if ( sampleDict[aSample][-1] >= 10 ):
                        pairedList += [ aSample ]
        numPairs = len(pairedList)

        # print " "
        print " number of paired samples : ", numPairs
        print " paired list : ", pairedList
        print " "

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

uuid2barcode_dict = {}
barcode2uuid_dict = {}
barcode2disease_dict = {}
patient_dict = {}

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# a typical UUID looks like:
#	012345678901234567890123456789012345
#	6d41d8c9-f2bf-4440-8b8d-907e3b2682f5
def looks_like_uuid ( aString ):
    if ( uuid_re.match(aString) ):
        return ( 1 )
    return ( 0 )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# a typical barcode looks like:
#	0123456789012345678901234567
#	TCGA-33-4579-01A-01R-1443-07
def looks_like_barcode ( aString ):
    if ( barcodes.match(aString) ):
        return ( 1 )
    return ( 0 )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def get_uuid2barcode_dict():

    global uuid2barcode_dict
    global barcode2uuid_dict
    global barcode2disease_dict

    print datetime.now(), " reading metadata file for UUID to barcode mapping "

    fileName = uuidMappingFile

    tNow = time.ctime()
    try:
        tMet = time.ctime(os.path.getmtime(fileName))
        nowTokens = tNow.split()
        metTokens = tMet.split()
        refreshFlag = 0
        if (nowTokens[1] != metTokens[1]):
            refreshFlag = 1
        if (int(nowTokens[2]) > int(metTokens[2])):
            refreshFlag = 1
    except:
        refreshFlag = 1

    if ( refreshFlag ):
        cmdString = uuidMetadataScript
        print " "
        print " UPDATING METADATA !!! "
        print "     current time   : ", tNow
        try:
            print "     last update at : ", tMet
        except:
            print "     no UUID mapping file available ??? "
        ( status, output ) = commands.getstatusoutput ( cmdString )
        print " ... should be done ... "
        print " "


    fh = file ( fileName, 'r' )
    for aLine in fh:

        aLine = aLine.strip()
        tokenList = aLine.split('\t')
        if ( len(tokenList) < 4 ):
            continue

        uuid = tokenList[0]
        barcode = tokenList[1]

        if (not looks_like_uuid(uuid)):
            continue
        if (not looks_like_barcode(barcode)):
            continue

        # columns in this file are:
        #         0 'UUID'                1592cfef-f2b8-48f5-b61d-9c467b608671
        #         1 'BARCODE'                TCGA-01-0628-11A-01D-0356-01
        #         2 'ELEMENT_TYPE'        Aliquot
        #         3 'DISEASE_STUDY'        OV
        # etc ... (many more columns, but we don't need/use them)

        diseaseCode = tokenList[3]

        if ( 0 ):
            uuid2barcode_dict[uuid] = barcode
            barcode2uuid_dict[barcode] = uuid

            if ( len(barcode) > 12 ):
                shortBarcode = barcode[:12]
            else:
                shortBarcode = barcode
            barcode2disease_dict[shortBarcode] = diseaseCode
        else:
            # assume that this check does not need to be done ... it is very slow!
            # modified from 'not in uuid_dict.keys()' to 'not in uuid_dict', speeds it up! 
            # --mm 2012-08-25
            if ( uuid not in uuid2barcode_dict ):
                uuid2barcode_dict[uuid] = barcode
                barcode2uuid_dict[barcode] = uuid
    
                if ( len(barcode) > 12 ):
                    shortBarcode = barcode[:12]
                else:
                    shortBarcode = barcode
                barcode2disease_dict[shortBarcode] = diseaseCode
            else:
                print " FATAL ERROR in get_uuid2barcode_dict ??? "
                print uuid, uuid2barcode_dict[uuid], barcode
                sys.exit(-1)

        patientBarcode = barcode[:12]
        if ( patientBarcode not in patient_dict.keys() ):
            patient_dict[patientBarcode] = []
        patient_dict[patientBarcode] += [ barcode ]

    print datetime.now(), " done reading UUID to barcode mapping file (%d UUIDs and %d patients) " % ( len(uuid2barcode_dict), len(patient_dict) )

    if ( len(uuid2barcode_dict) < 50000 ):
        print " ERROR in get_uuid2barcode_dict ??? it should be much longer than: "
        print len(uuid2barcode_dict)
        sys.exit(-1)

    if ( 0 ):
        patientList = patient_dict.keys()
        patientList.sort()
        print patientList[:5]
        print patientList[-5:]
        print " "
        print " "

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def get_tumor_barcode ( patientBarcode ):

    if ( len(patient_dict) == 0 ):
        get_uuid2barcode_dict()

    patientBarcode = patientBarcode.upper()

    if ( len(patientBarcode) > 12 ):
        if ( len(patientBarcode) >= 15 ):
            if ( patientBarcode[13] == '0' ):
                return ( patientBarcode[:15] )

        print " ERROR ??? barcode is wrong format ??? ", patientBarcode
        sys.exit(-1)

    try:
        barcodeList = patient_dict[patientBarcode]
        barcodeList.sort()
        # print barcodeList
        for aCode in barcodeList:
            if ( len(aCode) >= 15 ):
                if ( aCode[13] == "0" ):
                    return ( aCode[:15] )
    except:
        print " ERROR in get_tumor_barcode ??? no information for patient ", patientBarcode
        if ( len(patientBarcode) == 12 ):
            tmpCode = patientBarcode + "-01"
            print " --> assuming that <%s> is ok " % tmpCode
            return ( tmpCode )
        sys.exit(-1)

    print " ERROR ??? no tumor sample for ", patientBarcode
    if ( len(patientBarcode) == 12 ):
        tmpCode = patientBarcode + "-01"
        print " --> assuming that <%s> is ok " % tmpCode
        return ( tmpCode )
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def uuid_to_barcode ( uuid ):

    try:
        # try to return the barcode associated with this UUID
        return ( uuid2barcode_dict[uuid] )
    except:

        try:
            # if that didn't work, maybe the UUID needs to be shifted
            # to lower case?
            return ( uuid2barcode_dict[uuid.lower()] )
        except:

            # if that didn't work and we have already constructed
            # the UUID dictionary then we have a problem
            if ( len(uuid2barcode_dict) > 0 ):
                print " FATAL ERROR in uuid_to_barcode ??? <%s> <%s> " % ( uuid, uuid.lower() )
                return ( "NA" )
                # sys.exit(-1)
            else:

                # if we have not constructed the UUID dictionary
                # then we need to do that now
                get_uuid2barcode_dict()
                return ( uuid_to_barcode ( uuid ) )

    # we should never fall through to here ...
    print " should never get here ??? "
    print len(uuid2barcode_dict)
    print uuid
    print uuid2barcode_dict[uuid]
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def barcode_to_uuid ( barcode ):

    try:
        # try to return the UUID associated with this barcode
        return ( barcode2uuid_dict[barcode] )
    except:

        try:
            # barcodes should be upper case ...
            return (barcode2uuid_dict[barcode.upper()])
        except:

            # if that didn't work and we have already constructed
            # the dictionary then we have a problem
            if ( len(barcode2uuid_dict) > 0 ):
                print " FATAL ERROR in barcode_to_uuid ??? <%s> <%s> " % ( barcode, barcode.lower() )
                return ( "NA" )
                # sys.exit(-1)
            else:

                # if we have not constructed the UUID dictionary
                # then we need to do that now
                get_uuid2barcode_dict()
                return ( barcode_to_uuid ( barcode ) )

    # we should never fall through to here ...
    print " should never get here ??? "
    print len(barcode2uuid_dict)
    print barcode
    print barcode2uuid_dict[barcode]
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def barcode_to_disease ( barcode ):

    if ( len(barcode) > 12 ):
        shortBarcode = barcode[:12]
    else:
        shortBarcode = barcode

    try:
        # try to return the disease associated with this barcode
        return ( barcode2disease_dict[shortBarcode] )
    except:

        try:
            # barcodes should be upper case
            return (barcode2disease_dict[shortBarcode.upper()])
        except:

            # if that didn't work and we have already constructed
            # the dictionary then we have a problem
            if ( len(barcode2disease_dict) > 0 ):
                print " FATAL ERROR in barcode_to_disease ??? <%s> <%s> " % ( shortBarcode, shortBarcode.lower() )
                return ( "NA" )
                # sys.exit(-1)
            else:

                # if we have not constructed the UUID dictionary
                # then we need to do that now
                get_uuid2barcode_dict()
                return ( barcode_to_disease ( barcode ) )

    # we should never fall through to here ...
    print " should never get here ??? "
    print len(barcode2disease_dict)
    print barcode, shortBarcode
    print barcode2disease_dict[barcode]
    sys.exit(-1)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
