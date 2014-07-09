'''
Created on May 9, 2013

for the different platforms, run the feature matrix current production script 
and then the developed and compare the results.  read from the configuration
file which cancers to batch together for each platform

@author: michael
'''
import commands
import ConfigParser
from datetime import datetime
import sys
import traceback

import count_tcga

class globalVars():
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        self.tag = config.get('main', 'tag')
        self.out_dir = config.get('main', 'out_dir')
        self.curpath = config.get('main', 'curpath')
        self.curcmd = config.get('main', 'curcmd')
        self.newpath = config.get('main', 'newpath')
        self.newcmd = config.get('main', 'newcmd')
        self.curfilename = config.get('main', 'curfilename')
        self.newfilename = config.get('main', 'newfilename')
        self.diffcmd = config.get('main', 'diffcmd')
        self.extended_all = config.get('main', 'extended_all')
        self.runwhich = config.get('main', 'runwhich') if config.has_option('main', 'runwhich') else 'all'

def getSnapshot(config):
    parseConfigName = config.get('main', 'parse_config')
    parseConfig = ConfigParser.ConfigParser()
    parseConfig.read(parseConfigName)
    return parseConfig.get('technology_type', 'snapshot')

def deleteFile(filename):
    try:
        status, output = commands.getstatusoutput('rm %s' % (filename))
        if 0 == status:
            print '''\t\t\tdeleted %s''' % (filename)
        else:
            print '''\t\t\tdidn't delete %s: %s''' % (filename, output)
    except Exception as e:
        print '''\t\t\tdidn't delete %s: %s''' % (filename, e)

def _runTest(config, platformID, tumor, globalVars):
    print '\t', datetime.now(), 'starting run for %s: %s' % (platformID, tumor)
    try:
        output = '<none>'
        snapshot = getSnapshot(config)
        curSuccess = 0
        reSuccess = 0
        diffSuccess = 0
        if globalVars.runwhich in ['all', 'current']:
            try:
                start_cur = datetime.now()
                print '\t\t', start_cur, 'starting current'
                deleteFile(globalVars.curfilename.format(tumor, platformID[:-1].replace('/', "__"), globalVars.tag))
                oldCmdString = globalVars.curcmd.format(globalVars.out_dir, platformID, tumor, globalVars.tag, platformID.replace('/', "_"), tumor, 
                                                        config.get('main', 'parse_config'), globalVars.curpath)
                status, output = commands.getstatusoutput(oldCmdString)
                end_cur = datetime.now()
                total_cur = end_cur - start_cur
                print '\t\t', end_cur, "result of running current script: %s %s %s\n" % (status, total_cur, oldCmdString)
                if 0 == status:
                    curSuccess += 1
            except Exception as e:
                total_cur = datetime.now() - start_cur
                traceback.print_exc()
                print 'problem executing current %s\n' % (output)
                raise e

        if globalVars.runwhich in ['all', 'develop']:
            try:
                start_new = datetime.now()
                print '\t\t', start_new, 'starting develop'
                deleteFile(globalVars.newfilename.format(tumor, platformID[:-1].replace('/', "__"), globalVars.tag))
                newCmdString = globalVars.newcmd.format(globalVars.out_dir, platformID, tumor, globalVars.tag, platformID.replace('/', "_"), tumor, 
                                                        config.get('main', 'parse_config'), globalVars.newpath)
                status, output = commands.getstatusoutput(newCmdString)
                end_new = datetime.now()
                total_new = end_new - start_new
                print '\t\t', end_new, "result of running developed script: %s %s %s\n" % (status, total_new, newCmdString)
                if 0 == status:
                    reSuccess += 1
            except Exception as e:
                total_new = datetime.now() - start_new
                traceback.print_exc()
                print 'problem executing develop: %s' % (output)
                raise e

        if globalVars.runwhich == 'all':
            try:
                diffCmdString = globalVars.diffcmd.format(globalVars.out_dir, tumor, platformID[:-1].replace('/', "__"), globalVars.tag, tumor)
                status, output = commands.getstatusoutput(diffCmdString)
                print "\t\tresult of running diff: %s %s" % (status, diffCmdString)
                if 0 == status:
                    diffSuccess += 1
            except Exception as e:
                traceback.print_exc()
                print 'problem executing diff: %s' % (diffCmdString)
                raise e
    except:
        traceback.print_exc()
    if globalVars.runwhich == 'all':
        print '\t', '%s: developed code was %.2f times faster (%s secs for develop, %s secs for current)' % \
            (platformID + ':' + tumor, total_cur.total_seconds() / total_new.total_seconds(), total_new.total_seconds(), total_cur.total_seconds())
    print '\t', datetime.now(), 'ending run for %s: %s' % (platformID, tumor)
    return curSuccess, reSuccess, diffSuccess

def _run(argv):
    config = ConfigParser.ConfigParser()
    config.read(argv[1])
    
    # get the static variables
    gVars = globalVars(config)

    # now loop over the runs
    platforms = config.get('main', 'platforms').split(',')
    platform2tumors, _, _ = count_tcga.run([None, config.get('main', 'count_config')])
    total = 0
    totalCurSuccess = 0
    totalReSuccess = 0
    totalDiffSuccess = 0
    for platform, tumors in platform2tumors.iteritems():
        if 0 == len(platforms) or not platforms[0] or platform in platforms: 
            for tumor in tumors:
                curSuccess, reSuccess, diffSuccess = _runTest(config, platform, tumor, gVars)
                total += 1
                totalCurSuccess += curSuccess
                totalReSuccess += reSuccess
                totalDiffSuccess += diffSuccess
    print 'overall results:\n\tcurrent success: %i/%i\n\tdeveloped success: %i/%i\n\tdiff success: %i/%i' % (totalCurSuccess, total, totalReSuccess, total, totalDiffSuccess, total)

if __name__ == '__main__':
# example cmdline: python -u ../<python path>/util/test_parse_tcga.py ../<python path>/config/test_parse_tcga.config
# where the current directory has subdirectories out and diff
    print datetime.now(), 'starting check'
    _run(sys.argv)
    print datetime.now(), 'completed check'
