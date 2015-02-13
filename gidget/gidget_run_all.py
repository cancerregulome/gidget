#!/usr/bin/env python

"""Gidget Run All

usage: gidget_run_all [options] <maf_manifest> <output_directory>

Options:
    -h, --help       Show this screen
    --version        Show version
    --processes=<n>  Number of concurrent pipeline runs. Default 4

"""

from docopt import docopt
from threading import Semaphore, Thread
from subprocess import Popen
from datetime import datetime
from fnmatch import fnmatch
import csv
import os

# tsv parser settings
MAF_MANIFEST_DIALECT = "maf_manifest"
csv.register_dialect(MAF_MANIFEST_DIALECT, delimiter='\t', lineterminator='\n')

# keys to the maf manifest columns
DATE       = 'date'
PERSON     = 'point-person'
TUMOR_CODE = 'tumor_short_code'
TAGS       = 'tags'
PATH       = 'internal-path'

_processSemaphore = None

class PipelineError(Exception):
    pass

class Pipeline(Thread):

    def __init__(self, mafFile, outputDirRoot, tagString, tumorString):
        self.maf = os.path.expandvars(mafFile)
        self.tumorString = tumorString

        self.outputDir = os.path.join(outputDirRoot, tagString)

        _ensureDir(self.outputDir)
        tumorDir = os.path.join(self.outputDir, self.tumorString)
        _ensureDir(tumorDir)

        self.dateString = datetime.now().strftime('%Y_%m_%d')
        self.dateDir = os.path.join(tumorDir, self.dateString)

        if os.path.exists(self.dateDir):
            self.dateString = datetime.now().strftime('%Y_%m_%d-%H:%M')
            self.dateDir = os.path.join(tumorDir, self.dateString)

        _ensureDir(self.dateDir)

        self.env = os.environ.copy()
        self.env["TCGAFMP_DATA_DIR"] = self.outputDir

        super(Pipeline, self).__init__()

    def run(self):
        with _processSemaphore:
            self.executeGidgetPipeline('annotate-maf.sh', (self.maf, ))

            # this is just where the annotation and binarization scripts put things. Don't ask too many questions...
            outputdir = os.path.join(self.dateDir, self.tumorString)
            annotationOutput = os.path.join(outputdir, os.path.basename(self.maf) + '.ncm.with_uniprot')

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
        subProc = Popen((os.path.join(os.environ['GIDGET_SOURCE_ROOT'], 'pipelines', pipeline),) + args, cwd=self.dateDir)
        if subProc.wait() != 0:
            # TODO log error message
            raise PipelineError()  # TODO just exit?

def run_all(pathToMafManifest, numProcesses, outputDir):
    global _processSemaphore
    _processSemaphore = Semaphore(numProcesses)  # TODO there is probably a better way than using a global semaphore. Or is there...?
    with open(pathToMafManifest) as tsv:
        for maf in csv.DictReader(tsv, dialect=MAF_MANIFEST_DIALECT):
            print maf
            run_one(maf[PATH], outputDir, maf[TAGS], maf[TUMOR_CODE])


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
    print(arguments)
    run_all(arguments.get('<maf_manifest>'), arguments.get('--processes') or 4, arguments.get('<output_directory>'))

