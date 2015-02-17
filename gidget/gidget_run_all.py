#!/usr/bin/env python

"""Gidget Run All

usage: gidget_run_all [options] <maf_manifest> <output_directory>

Options:
    -h, --help       Show this screen
    --version        Show version
    --processes=<n>  Number of concurrent pipeline runs. Default 4

"""

from gidget_util import gidgetConfigVars

from docopt import docopt
from threading import Semaphore, Thread
from subprocess import Popen
from datetime import datetime
from fnmatch import fnmatch
from os.path import join as pathjoin
import csv
import os
import sys

from log import Logger, LogPipe, LOGGER_ENV

# tsv parser settings
MAF_MANIFEST_DIALECT = "maf_manifest"
csv.register_dialect(MAF_MANIFEST_DIALECT, delimiter='\t', lineterminator='\n')

# keys to the maf manifest columns
DATE       = 'date'
PERSON     = 'point-person'
TUMOR_CODE = 'tumor-short-code'
TAGS       = 'tags'
PATH       = 'internal-path'

_processSemaphore = None


class PipelineError(Exception):
    pass  # TODO


class Pipeline(Thread):

    def __init__(self, mafFile, outputDirRoot, tagString, tumorString):
        super(Pipeline, self).__init__()

        self.maf = os.path.expandvars(mafFile)
        self.tumorString = tumorString

        self.outputDir = pathjoin(outputDirRoot, tagString)

        _ensureDir(self.outputDir)
        tumorDir = pathjoin(self.outputDir, self.tumorString)
        _ensureDir(tumorDir)

        self.dateString = datetime.now().strftime('%Y_%m_%d')
        self.dateDir = pathjoin(tumorDir, self.dateString)

        if os.path.exists(self.dateDir):
            self.dateString = datetime.now().strftime('%Y_%m_%d-%H:%M')
            self.dateDir = pathjoin(tumorDir, self.dateString)

        _ensureDir(self.dateDir)

        self.env = os.environ.copy()
        self.env["TCGAFMP_DATA_DIR"] = self.outputDir

        # Logging stuff
        logpath = pathjoin(outputDirRoot, 'LOG')
        self.pipelinelog = PipelineLog(logpath)
        self.env[LOGGER_ENV] = logpath

    def run(self):
        with _processSemaphore:
            self.executeGidgetPipeline('annotate-maf.sh', (self.maf, ))

            # this is just where the annotation and binarization scripts put things. Don't ask too many questions...
            outputdir = pathjoin(self.dateDir, self.tumorString)
            annotationOutput = pathjoin(outputdir, os.path.basename(self.maf) + '.ncm.with_uniprot')

            self.executeGidgetPipeline('binarization.sh', (self.tumorString, annotationOutput))

            binarizationOutput = None
            for outfile in os.listdir(os.curdir):
                if fnmatch(outfile, 'mut_bin_*.txt'):
                    binarizationOutput = outfile
                    break
            if (binarizationOutput is None):
                raise PipelineError()  # TODO do something useful

            self.executeGidgetPipeline('post_maf.sh', (self.tumorString, binarizationOutput))

            ppstring = 'private'  # TODO is it always this way?

            self.executeGidgetPipeline('fmx.sh', (self.dateString, self.tumorString, ppstring))

            # TODO load into re


    def executeGidgetPipeline(self, pipeline, args):
        subProc = Popen((pathjoin(gidgetConfigVars['GIDGET_SOURCE_ROOT'], 'pipelines', pipeline),) + args,
                        cwd=self.dateDir,
                        stdout=self.pipelinelog.logpipeout,
                        stderr=self.pipelinelog.logpipeerr)
        if subProc.wait() != 0:
            # TODO log error message
            raise PipelineError()  # TODO just exit?

    def close(self):
        self.pipelinelog.close()
        self.join()


class PipelineLog:
    def __init__(self, logpath):
        self.logger = Logger(logpath)
        self.logpipeout = LogPipe.createAndStart('OUT', self.logger)
        self.logpipeerr = LogPipe.createAndStart('ERROR', self.logger)

    def close(self):
        self.logpipeout.close()
        self.logpipeerr.cloose()
        self.logger.close()


def run_all(pathToMafManifest, numProcesses, outputDir):
    global _processSemaphore
    _processSemaphore = Semaphore(numProcesses)  # TODO there is probably a better way than using a global semaphore. Or is there...?
    pipes = ()
    with open(pathToMafManifest) as tsv:
        for maf in csv.DictReader(tsv, dialect=MAF_MANIFEST_DIALECT):
            print maf
            pipes += (run_one(maf[PATH], outputDir, maf[TAGS], maf[TUMOR_CODE]),)

    # join all
    for pipe in pipes:
        pipe.close()


def run_one(pathToMaf, outputDir, tags, tumorString):
    """
    :param pathToMaf:
    :return the pipeline thread running this maf file
    """
    assert _processSemaphore is not None
    pipeline = Pipeline(pathToMaf, outputDir, tags, tumorString)
    pipeline.start()
    return pipeline


def _ensureDir(absPath):
    if not os.path.exists(absPath):
        os.mkdir(absPath)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='Gidget Run All 0.0')

    mafManifest = arguments.get('<maf_manifest>')
    outputDir = arguments.get('<output_directory>')

    if not os.path.exists(mafManifest):
        sys.stderr.write("No manifest file at %s\n" % mafManifest)
        exit(1)

    if not os.path.exists(outputDir):
        sys.stderr.write("Output directory at %s does not exist\n" % outputDir)
        exit(1)

    run_all(mafManifest, arguments.get('--processes') or 4, outputDir)

