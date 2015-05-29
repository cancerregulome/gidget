#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

"""usage: gidget [options] <command> [<args>...]

Options:
    -h, --help    Show this screen
    --version

gidget commands are:
    run

"""

import sys
import os
import shlex
import subprocess
from subprocess import call

from docopt import docopt
from ConfigParser import SafeConfigParser

import gidget_help
#import gidget_list
#import gidget_describe
#import gidget_add
#import gidget_remove
#import gidget_run

from util.env import gidgetConfigVars

if __name__ == '__main__':




    gidgetSubCommandsPath = gidgetConfigVars['GIDGET_SOURCE_ROOT'] + '/gidget'
    gidgetPythonExecutable = sys.executable

    # environment for subprocesses:
    # parent environment plus info from config file to environment
    # TODO: uncomment for config file processing
    #subEnv = os.environ
    # configParserDefaults = {}
    # config = SafeConfigParser(defaults = {
    #     'gidget_commands_dir':gidgetCommandsPath,
    #     'gidget_python_executable':gidgetPythonExecutable})

    # TODO: make config file location an optional command-line flag
    # TODO: error checking on file existence
    # TODO: error checking on sucessful config parsing
    # TODO: check file permissions and warn or error if not private
    
    # TODO: uncomment for config file processing
    # config.read('.gidgetconfig')
    # gidgetConfigDefaults = {}
    # gidgetConfigSections = config.sections()
    # for section in gidgetConfigSections:
    #     sectionOptions = config.options(section)
    #     for option in sectionOptions:
    #         # TODO: for now, sections are disregarded and everything is thrown
    #         # into one dictionary object; break this out per section?
    #         gidgetConfigDefaults[option] = config.get(section, option)
    #         if section == 'MAF_PROCESSING':
    #             # TODO: warn if this overwrites some existing envvars
    #             # export env vars as uppercase, per convention;
    #             # ConfigParser converts to lower.
    #             subEnv[('gidget_'+option).upper()] = gidgetConfigDefaults[option]


    # print "== gidget options =="
    # for key,val in gidgetConfigDefaults.items():
    #     print key + ": " + val


    # test env settings
    # command = '/usr/bin/env'
    # args = shlex.split(command)
    # print "running ", args
    # p = subprocess.Popen(args, env=subEnv)

    # print detailed help by default
    if len(sys.argv) < 2:
        sys.argv.append("--help")

    # for "-h" or "--help", docopt prints usage and exits cleanly
    mainArgs = docopt(__doc__,
                      version = 'gidget version 1.2.2-pre',
                      options_first = True)


    #TODO: take action on any top-level options

    #parse the remaining subcommand and its options
    subCommandName = mainArgs['<command>']
    subCommandArgs = mainArgs['<args>']

    # subcommands are:

    # run

    # TODO
    # help
    # list
    # describe
    # add
    # remove


    # contruct an 'args' for the subcommand
    subCommandArgs = [subCommandName] + subCommandArgs

    if subCommandName == 'help':
        gidget_help.parse(subCommandArgs)
    # elif subCommandName == 'list':
    #     print docopt(gidget_list.__doc__, argv = subCommandArgs)
    # elif subCommandName == 'describe':
    #     print docopt(gidget_describe.__doc__, argv = subCommandArgs)
    # elif subCommandName == 'add':
    #     print docopt(gidget_add.__doc__, argv = subCommandArgs)
    # elif subCommandName == 'remove':
    #     print docopt(gidget_remove.__doc__, argv = subCommandArgs)
    elif subCommandName == 'run':
        exit(call(['python', gidgetSubCommandsPath+'/gidget_run.py'] + subCommandArgs))# + ' '.join(subCommandArgs)]))
    else:
        print "command " + subCommandName + " not recognized."
        print __doc__
        #sys.exit(-1)


 
    sys.exit(0)
