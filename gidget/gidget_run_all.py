#!/usr/bin/env python

# TODO make config file a non-optional parameter

"""Gidget Run All

usage: gidget_run_all [options] <maf_manifest> <output_directory>

Options:
    -h, --help                Show this screen
    --version                 Show version
    --processes=<n>           Number of concurrent pipeline runs. Default 4
    --use-date=<date>         Run against existing output for <date>. If existing output does not exists, will use the
                              string provided as the name for date-based folders.
    --config=<config file>    Use the specified config file
    --stop-at=<pipeline step> If set, will only run the pipeline until <pipeline step>.
                              Set it to one of ['annotation', 'binarization', 'cleanup', 'fmx']

Output directory will be the root of all outputs. The directory structure of the outputs is as follows:

    <output root>
        <tag>
            <tumor type>
                <date>

The tag and tumor-type directory names come from the lines in the manifest file. The date comes from the current system
date, or the --use-date option if specified. Included under the <date> directory is a LOG.txt file which contains the
captured output from subprocesses spawned by this script as well as log messages from the script itself.

The run_all script requires you to set your gidget-env variables or to specify a config file to import them from. See
the files 'required_env_vars' and 'gidget_config_template.config' for more information.
"""

from docopt import docopt
from threading import Semaphore, Thread
from subprocess import Popen
from datetime import datetime
from os.path import join as pathjoin
import csv
import os
import sys
from shutil import move, rmtree

from util.log import Logger, LogPipe, LOGGER_ENV, logToFile
from util.pipeline_util import ensureDir, findBinarizationOutput, expandPath
from util.load_path_config import envFromConfigOrOs
from util.tumor_type_config import tumorTypeConfig

# tsv parser settings
MAF_MANIFEST_DIALECT = "maf_manifest"
csv.register_dialect(MAF_MANIFEST_DIALECT, delimiter='\t', lineterminator='\n')

# keys to the maf manifest columns
DATE       = 'date'
PERSON     = 'point-person'
TUMOR_CODE = 'tumor-short-code'
TAGS       = 'tag'
PATH       = 'internal-path'

# pipeline names
ANNOTATE     = ('maf-annotation-pipeline.sh', 'annotation')
BINARIZATION = ('binarization-pipeline.sh', 'binarization')
POST_MAF     = ('prepare-binarized-maf-for-fmx-construction.sh', 'cleanup')
FMX          = ('fmx-construction.sh', 'fmx')
UPLOAD       = ('upload-fmx-to-regulome-explorer.sh', None)

_processSemaphore = None

class PipelineError(Exception):
    pass  # TODO

"""
Represents a run of one of the MAFs in the maf-manifest file. The _processSemaphore is used to ensure that a limited
number of MAFs are being processed at any one time.
"""
class Pipeline(Thread):

    def __init__(self, cmdargs, mafargs, env, date=None):
        super(Pipeline, self).__init__()

        self.interrupted = False
        self.procCur = None

        self.cmdargs = cmdargs
        self.mafargs = mafargs

        self.tagDir = pathjoin(cmdargs.outputdir, self.mafargs.tags)

        ensureDir(self.tagDir)
        tumorDir = pathjoin(self.tagDir, self.mafargs.tumorcode)
        ensureDir(tumorDir)

        if (date is None):
            self.dateString = datetime.now().strftime('%Y_%m_%d')
            self.dateDir = pathjoin(tumorDir, self.dateString)
            if os.path.exists(self.dateDir):
                self.dateString = datetime.now().strftime('%Y_%m_%d-%H%M')
                self.dateDir = pathjoin(tumorDir, self.dateString)
        else:
            self.dateString = date
            self.dateDir = pathjoin(tumorDir, date)
            # TODO fail if date does not exist?

        ensureDir(self.dateDir)

        self.env = env.copy()
        # self.env['TCGAFMP_DATA_DIR'] = self.outputDir
        self.env['TCGAFMP_DATA_DIR'] = self.dateDir
        self.env['WRONGARGS'] = '1'

        # Logging stuff
        logpath = pathjoin(self.dateDir, 'LOG.txt')
        self.pipelinelog = PipelineLog(logpath)
        self.env[LOGGER_ENV] = logpath

        if not os.path.exists(self.mafargs.path):
            self.pipelinelog.logger.log("FATAL", "Cannot find MAF file %s." % self.mafargs.path)
            self.pipelinelog.logger.log("FATAL", "Aborting pipeline.")
            self.pipelinelog.logger.log("FATAL", "Please check the file path in the manifest file for tumor type %s and tag %s" % (self.mafargs.tumorcode, self.mafargs.tags))
            self.pipelinelog.logger.log("FATAL", "Also check your environment variables. See below for current values:")
            self.pipelinelog.logger.log("FATAL", "TCGAMAF_OUTPUTS=%s" % self.env['TCGAMAF_OUTPUTS'])
            self.pipelinelog.logger.log("FATAL", "TCGAFMP_DCC_REPOSITORIES=%s" % self.env['TCGAFMP_DCC_REPOSITORIES'])
            self.mafargs.path = None
            return

        # HACK: this is needed for the doAllC code
        ensureDir(pathjoin(self.dateDir, self.mafargs.tumorcode))
        ensureDir(pathjoin(self.dateDir, self.mafargs.tumorcode, self.dateString))
        ensureDir(pathjoin(self.dateDir, self.mafargs.tumorcode, 'gnab'))
        ensureDir(pathjoin(self.dateDir, self.mafargs.tumorcode, 'scratch'))

    def run(self):
        if self.mafargs.path is None:
            return

        with _processSemaphore:
            try:
                # this is just where the annotation and binarization scripts put things. Don't ask too many questions...
                outputdir = pathjoin(self.dateDir, self.mafargs.tumorcode)
                annotationOutput = pathjoin(outputdir, os.path.basename(self.mafargs.path) + '.ncm.with_uniprot')

                if self._ensurePipelineOutput(ANNOTATE, (self.mafargs.tumorcode, self.mafargs.path), annotationOutput): return

                binarizationOutput = findBinarizationOutput(outputdir)
                if self._ensurePipelineOutput(BINARIZATION, (self.mafargs.tumorcode, annotationOutput), binarizationOutput): return
                binarizationOutput = findBinarizationOutput(outputdir)

                if self._ensurePipelineOutput(POST_MAF, (self.mafargs.tumorcode, binarizationOutput), None): return

                ppstring = 'private'  # TODO is it always this way?
                fmxsuffix = tumorTypeConfig[self.mafargs.tumorcode]['fmx_suffix'] + ".tsv"

                if self._ensurePipelineOutput(FMX, (self.dateString, self.mafargs.tumorcode, ppstring, fmxsuffix), None): return

                # TODO load into re
            except KeyboardInterrupt:
                logToFile(self.env[LOGGER_ENV], 'FATAL', "Keyboard interrupt")
            except PipelineError as perror:
                logToFile(self.env[LOGGER_ENV], 'FATAL', perror.message)
            finally:
                self._cleanupOutputFolder()


    '''
    return true if we're done at this point
    '''
    def _ensurePipelineOutput(self, pipeline, args, outputfile):
        if outputfile is None or not os.path.exists(outputfile):
            self.executeGidgetPipeline(pipeline[0], args)
        return self._stophere(pipeline[1])

    def executeGidgetPipeline(self, pipeline, args):
        if self.interrupted:
            raise KeyboardInterrupt()
        Pipeline._logPipelineStart(pipeline, self.env[LOGGER_ENV], args)
        self.procCur = Popen((pathjoin(self.env['GIDGET_SOURCE_ROOT'], 'pipelines', pipeline),) + args,
                        env=self.env,
                        cwd=self.dateDir,
                        stdout=self.pipelinelog.logpipeout,
                        stderr=self.pipelinelog.logpipeerr)
        if self.procCur.wait() != 0:
            if self.interrupted:
                raise KeyboardInterrupt()
            # TODO log error message
            raise PipelineError('Pipeline %s exited with non-zero status' % pipeline)  # TODO just exit?
        self.procCur = None

    @staticmethod
    def _logPipelineStart(pipelineName, logfile, args):
        logToFile(logfile, 'PIPELINE-START', '%s %s' % (pipelineName, ' '.join(str(arg) for arg in args)))

    def _stophere(self, pipelinename):
        return self.cmdargs.stopat is not None and self.cmdargs.stopat == pipelinename

    # Execute on main thread
    def forceClose(self):
        self.interrupted = True
        if self.procCur is not None:
            try:
                self.procCur.terminate()
            finally:
                self.procCur = None

    def close(self):
        self.pipelinelog.close()
        self.join()

    # TODO a better thing would be to modify the scripts to put things in the right place to begin with...
    def _cleanupOutputFolder(self):

        fmxdirNew = pathjoin(self.dateDir, 'fmx')
        os.mkdir(fmxdirNew)
        fmxdirOld = pathjoin(self.dateDir, self.mafargs.tumorcode, self.dateString)
        for outfile in _listdirNonHidden(fmxdirOld):
            move(pathjoin(fmxdirOld, outfile), fmxdirNew)

        rmtree(fmxdirOld)

        tumordir = pathjoin(self.dateDir, self.mafargs.tumorcode)
        for outfile in _listdirNonHidden(tumordir):
            move(pathjoin(tumordir, outfile), self.dateDir)

        rmtree(tumordir)

def _listdirNonHidden(dir):
    return [file for file in os.listdir(dir) if not file.startswith('.')]


class PipelineLog:
    def __init__(self, logpath):
        self.logger = Logger(logpath)
        self.logpipeout = LogPipe.createAndStart('OUT', self.logger)
        self.logpipeerr = LogPipe.createAndStart('ERROR', self.logger)

    def close(self):
        self.logpipeout.close()
        self.logpipeerr.close()
        self.logger.close()


def interruptAll(pipes):
    print ("Terminating all subproccesses and exiting...")
    for pipe in pipes:
        pipe.forceClose()


def run_all(cmdargs, env):
    global _processSemaphore
    pipes = ()
    try:
        _processSemaphore = Semaphore(cmdargs.numprocesses)  # TODO there is probably a better way than using a global semaphore. Or is there...?
        with open(cmdargs.manifestfile) as tsv:
            for maf in csv.DictReader(tsv, dialect=MAF_MANIFEST_DIALECT):
                pipes += (run_one(cmdargs, Mafargs(maf), env),)

        # TODO Kludge
        # Python will only send interrupts to the main thread and the main thread will not respond if it is
        # blocked/waiting. So we need to make sure the main thread wakes up occasionally to handle interrupts
        # (terminating subprocesses and cleaning up open resources).
        allPipesDone = False  # done = not alive
        while not allPipesDone:
            allPipesDone = True
            for pipe in pipes:
                pipe.join(1.0)  # Think of this as just a wait(1.0). The 1.0 is mostly arbitrary
                allPipesDone = allPipesDone and not pipe.isAlive()
    except KeyboardInterrupt:
        interruptAll(pipes)
    finally:
        for pipe in pipes:
            pipe.join()
            pipe.close()


def run_one(cmdargs, mafargs, env):
    """
    :param pathToMaf:
    :return the pipeline thread running this maf file
    """
    assert _processSemaphore is not None
    pipeline = Pipeline(cmdargs, mafargs, env)
    pipeline.start()
    return pipeline


class Cmdargs:

    def __init__(self, arguments):

        mafmanifest = arguments.get('<maf_manifest>')
        outputdir = arguments.get('<output_directory>')
        configfile = expandPath(arguments.get('--config'))

        if not os.path.exists(mafmanifest):
            sys.stderr.write("No manifest file at %s\n" % mafmanifest)
            exit(1)

        if not os.path.exists(outputdir):
            sys.stderr.write("Output directory at %s does not exist\n" % outputdir)
            exit(1)

        if configfile is not None and not os.path.exists(configfile):
            sys.stderr.write("Cannot find config file %s\n" % configfile)
            exit(1)

        self.numprocesses = arguments.get('--processes') or 4
        self.usedate = arguments.get('--use-date')
        self.manifestfile = mafmanifest
        self.outputdir = outputdir
        self.configfile = configfile
        self.stopat = arguments.get('--stop-at')

        if not (self.stopat is None or self.stopat == ANNOTATE[1] or self.stopat == BINARIZATION[1]
                or self.stopat == POST_MAF[1] or self.stopat == FMX[1]):
            sys.stderr.write("Invalid stop-at parameter\n")
            exit(1)


class Mafargs:

    def __init__(self, manifestLineDict):
        self.path = expandPath(manifestLineDict[PATH])
        self.tags = manifestLineDict[TAGS]
        self.tumorcode = manifestLineDict[TUMOR_CODE]


if __name__ == "__main__":
    cmdargs = Cmdargs(docopt(__doc__, version='Gidget Run All 0.0'))
    run_all(cmdargs, envFromConfigOrOs(cmdargs.configfile))
