# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from gidget_util import gidgetConfigVars
import miscMath
import miscTCGA
from technology_type_factory import technology_type_factory

import commands
from datetime import datetime
import json
import numpy
import path
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

name_map_dict = {}
haveNameMapDict = 0

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getDate(dName):

    dateString = dName[-10:]
    iDate = int(dateString[0:4]) * 10000 + \
        int(dateString[5:7]) * 100 + int(dateString[8:10])
    return (iDate)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMostRecentDir(topDir, cancerList):

    print " in getMostRecentDir ... "
    print topDir
    print cancerList

    d1 = path.path(topDir)
    iDates = []
    for d1Name in d1.dirs():

        if (d1Name.find("stddata") >= 0):
            iDates += [getDate(d1Name)]

        if (0):
            if (len(cancerList) == 1):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        iDates += [getDate(d1Name)]

    iDates.sort()
    print iDates

    lastDate = str(iDates[-1])
    lastDate = lastDate[0:4] + "_" + lastDate[4:6] + "_" + lastDate[6:8]
    print lastDate

    lastDir = "NA"
    for d1Name in d1.dirs():

        if (0):
            # give first priority to awg specific run ...
            if (len(cancerList) == 1):
                if (d1Name.find("awg_") >= 0):
                    if (d1Name.find(cancerList[0]) >= 0):
                        if (d1Name.find(lastDate) >= 0):
                            lastDir = d1Name

    if (lastDir == "NA"):
        for d1Name in d1.dirs():
            if (d1Name.find("stddata") >= 0):
                if (d1Name.find(lastDate) >= 0):
                    lastDir = d1Name

    print " using firehose outputs from: ", lastDir

    return (lastDir)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getCancerDir(topDir, zCancer):

    nextDir = topDir + "/" + zCancer.upper()
    dateString = topDir[-10:]
    nextDir += "/" + dateString[0:4] + dateString[5:7] + dateString[8:10]

    return (nextDir)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def parseDataFiles(platform, config):
    platformConfig = config['platforms'][platform]
    platformConfig['zCancer'] = config['zCancer']
    platformConfig['suffixString'] = config['suffixString']
    if not platformConfig['execute']:
        print '\t', datetime.now(), "skipping parse of platform %s ... " % (platform)
        return
    
    print " "
    print '\t', datetime.now(), "starting parse of platform %s ... " % (platform)
    print "\t\tlastDir = <%s> " % config['lastDir']
    print "\t\toutDir = <%s> " % config['outDir']
    
    techType = technology_type_factory.getFirehoseTechnologyType(platform + '_firehose')

    gotone = False
    d2 = path.path(config['lastDir'])
    for d2Name in d2.dirs():
        d2substring_accept = platformConfig['d2substring_accept']
        cont = False
        for accept in d2substring_accept:
            if not accept in d2Name:
                cont = True
                continue
        if cont:
            continue

        # TODO: this is a little awkward in both the original and here in that we do
        # fall through for directories we don't care about, those directories just don't
        # have files that match d3substring_ending
        if platformConfig.has_key('d2substring_cont'):
            cont = False
            d2substring_cont = platformConfig['d2substring_cont']
            for conts in d2substring_cont:
                if conts[0] in d2Name and not conts[1] in d2Name:
                    cont = True
                    break
            if cont:
                continue

        d3 = path.path(d2Name)
        d3substring_accept = platformConfig['d3substring_accept']
        d3substring_ending = platformConfig['d3substring_ending']
        if platformConfig['d3add_subsetName']:
            d3substring_ending = d3substring_ending % (platformConfig['subsetName'] if platformConfig.has_key('subsetName') else '.')
        for fName in d3.files():
            if (config.has_key('subsetName') and not config['subsetName'] in fName):
                continue
            if (not d3substring_accept or d3substring_accept in fName) and fName.endswith(d3substring_ending):
                print "\t\t>>> got one !!! ", fName
                gotone = True
                techType.parseDataFiles(platformConfig, fName, config['outDir'])

    print '\t', datetime.now(), "finished parse of platform %s ... %s\n" % (platform, '' if gotone else '(no file found)')


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def init(config, args):
    # list of cancer directory names
    cancerDirNames = config['cancerDirNames']
    if (len(args) < 4):
        print " Usage: %s <config> <tumorType> <suffix-string> [path-to-stddata] [subset-name] " % args[0]
        sys.exit(-1)
    else:
        tumorType = args[2].lower()
        if (tumorType == "all"):
            print " this option is no longer allowed "
            sys.exit(-1)
        elif (tumorType in cancerDirNames):
            print " --> processing a single tumor type: ", tumorType
            config['tumorType'] = tumorType
        else:
            print " ERROR ??? tumorType <%s> not in list of known tumors? " % tumorType
            print cancerDirNames
            sys.exit(-1)
        config['suffixString'] = args[3]

        if (len(args) >= 5):
            path_to_stddata = args[4]
            topDir = path_to_stddata
        else:
            firehoseTopDir = gidgetConfigVars['TCGAFMP_FIREHOSE_MIRROR'] + "/"
            topDir = getMostRecentDir(firehoseTopDir, cancerDirNames) # if we are not told where to get the stddata, then get the
            # most recent ...
        config['topDir'] = topDir
        if (len(args) == 6):
            subsetName = args[5]
            if (subsetName == "NA"):
                subsetName = ""
            elif (not subsetName.endswith(".")):
                subsetName += "."
        else:
            subsetName = ""
        config['subsetName'] = subsetName
        
        if not config.has_key('outDir'):
            config[outDir] = './'
        elif not config['outDir'].endswith('/'):
            config['outDir'] += '/'
            
        print '\ttumor type: %s\n\tsuffix: %s\n\ttopDir: %s\n\tsubsetName: %s\n' % \
            (tumorType, config['suffixString'], topDir if topDir else "(not set)", subsetName if subsetName else "(not set)")

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def main(args):
    print datetime.now(), 'starting parse of firehose data'
    config = json.load(open(args[1]))
    init(config, args)
    # outer loop over tumor types
    for zCancer in [config['tumorType']]:
        print ' '
        print ' PROCESSING FIREHOSE STDDATA FOR CANCER TYPE ', zCancer
        config['zCancer'] = zCancer
        config['lastDir'] = getCancerDir(config['topDir'], zCancer)

        platforms = config['platforms'].keys()
        for platform in platforms:
            parseDataFiles(platform, config)

    print datetime.now(), 'finished parse of firehose data'

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#
# this program goes through the Firehose outputs and creates TSV files
# that are ready for our pipeline ...
#

if __name__ == "__main__":
    main(sys.argv)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
