# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

"""
usage: gidget run <pipelinename> [<pipelineargs>...]

"""
from util.env import gidgetConfigVars

from docopt import docopt

import subprocess
from subprocess import call
import os

if __name__ == '__main__':
    mainArgs = docopt(__doc__)


    pipelineName = mainArgs['<pipelinename>']
    pipelineArgs = mainArgs['<pipelineargs>']

    gidgetRootPath = gidgetConfigVars['GIDGET_SOURCE_ROOT']
    pipelineFilePath = gidgetRootPath + '/pipelines/' + pipelineName + ".sh"
    if os.path.isfile(pipelineFilePath):
        print "calling %s pipeline!" % pipelineName
        exit(call(['bash', pipelineFilePath] + pipelineArgs))
    else:
        print "%s pipeline not found (expected file %s)" % (pipelineName, pipelineFilePath)
        exit(-1)


