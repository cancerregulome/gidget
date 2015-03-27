#!/usr/bin/env python

# TODO make config file a non-optional parameter

"""Gidget Run All

usage: gidget_run_all [options] <maf_manifest> <output_directory>

Options:
    -h, --help                Show this screen
    --version                 Show version
    --processes=<n>           Number of concurrent pipeline runs. Default 4
    --use-date=<date>         Run against existing output for <date>
    --config=<config file>    Use the specified config file
    --stop-at=<pipeline step> If set, will only run the pipeline until <pipeline step>.
                              Set to one of ['annotation', 'binarization', 'cleanup', 'fmx']

"""

from docopt import docopt
from threading import Semaphore, Thread
from subprocess import Popen
from datetime import datetime
from os.path import join as pathjoin
import csv
import os
import sys
from shutil import move

from util.log import Logger, LogPipe, LOGGER_ENV, logToFile
from util.pipeline_util import ensureDir, findBinarizationOutput, expandPath
from util.load_path_config import envFromConfigOrOs

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


class Pipeline(Thread):

    def __init__(self, cmdargs, mafFile, tagString, tumorString, env, date=None):
        super(Pipeline, self).__init__()

        self.interrupted = False
        self.procCur = None

        self.cmdargs = cmdargs
        self.maf = expandPath(mafFile)
        self.tumorString = tumorString
        self.tagString = tagString

        self.tagDir = pathjoin(cmdargs.outputdir, tagString)

        ensureDir(self.tagDir)
        tumorDir = pathjoin(self.tagDir, self.tumorString)
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

        if not os.path.exists(self.maf):
            self.pipelinelog.logger.log("FATAL", "Cannot find MAF file %s." % self.maf)
            self.pipelinelog.logger.log("FATAL", "Aborting pipeline.")
            self.pipelinelog.logger.log("FATAL", "Please check the file path in the manifest file for tumor type %s and tag %s" % (self.tumorString, self.tagString))
            self.pipelinelog.logger.log("FATAL", "Also check your environment variables. See below for current values:")
            self.pipelinelog.logger.log("FATAL", "TCGAMAF_OUTPUTS=%s" % self.env['TCGAMAF_OUTPUTS'])
            self.pipelinelog.logger.log("FATAL", "TCGAFMP_DCC_REPOSITORIES=%s" % self.env['TCGAFMP_DCC_REPOSITORIES'])
            self.maf = None
            return

        # HACK: this is needed for the doAllC code
        ensureDir(pathjoin(self.dateDir, self.tumorString))
        ensureDir(pathjoin(self.dateDir, self.tumorString, self.dateString))
        ensureDir(pathjoin(self.dateDir, self.tumorString, 'gnab'))
        ensureDir(pathjoin(self.dateDir, self.tumorString, 'scratch'))

    def run(self):
        if self.maf is None:
            return

        with _processSemaphore:
            try:
                # this is just where the annotation and binarization scripts put things. Don't ask too many questions...
                outputdir = pathjoin(self.dateDir, self.tumorString)
                annotationOutput = pathjoin(outputdir, os.path.basename(self.maf) + '.ncm.with_uniprot')

                if self._ensurePipelineOutput(ANNOTATE, (self.tumorString, self.maf), annotationOutput): return

                binarizationOutput = findBinarizationOutput(outputdir)
                if self._ensurePipelineOutput(BINARIZATION, (self.tumorString, annotationOutput), binarizationOutput): return
                binarizationOutput = findBinarizationOutput(outputdir)

                if self._ensurePipelineOutput(POST_MAF, (self.tumorString, binarizationOutput), None): return

                ppstring = 'private'  # TODO is it always this way?
                fmxsuffix = 'TB.tsv'  # TODO is it always this way?

                if self._ensurePipelineOutput(FMX, (self.dateString, self.tumorString, ppstring, fmxsuffix), None): return

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
        fmxdirOld = pathjoin(self.dateDir, self.tumorString, self.dateString)
        for outfile in os.listdir(fmxdirOld):
            move(pathjoin(fmxdirOld, outfile), fmxdirNew)

        os.rmdir(fmxdirOld)

        tumordir = pathjoin(self.dateDir, self.tumorString)
        for outfile in os.listdir(tumordir):
            move(pathjoin(tumordir, outfile), self.dateDir)

        os.rmdir(tumordir)


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
                pipes += (run_one(cmdargs, maf[PATH], maf[TAGS], maf[TUMOR_CODE], env),)

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


def run_one(cmdargs, pathToMaf, tags, tumorString, env):
    """
    :param pathToMaf:
    :return the pipeline thread running this maf file
    """
    assert _processSemaphore is not None
    pipeline = Pipeline(cmdargs, pathToMaf, tags, tumorString, env)
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


if __name__ == "__main__":
    cmdargs = Cmdargs(docopt(__doc__, version='Gidget Run All 0.0'))
    run_all(cmdargs, envFromConfigOrOs(cmdargs.configfile))