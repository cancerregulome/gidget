#!/usr/bin/env python

"""Gidget Run All

usage: gidget_run_all [options] <maf_manifest>

Options:
    -h, --help       Show this screen
    --version        Show version
    --processes=<n>  Number of concurrent pipeline runs. Default 4

"""

from docopt import docopt
from threading import Semaphore, Thread
from subprocess import Popen
import csv

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


class Pipeline(Thread):

    def __init__(self, mafFile):
        self.maf = mafFile
        super(Pipeline, self).__init__()

    def run(self):
        with _processSemaphore:
            # TODO
            sub = Popen(("echo", self.maf))
            sub.wait()


def run_all(pathToMafManifest, numProcesses):
    global _processSemaphore
    _processSemaphore = Semaphore(numProcesses)
    with open(pathToMafManifest) as tsv:
        for maf in csv.DictReader(tsv, dialect=MAF_MANIFEST_DIALECT):
            run_one(maf[PATH])


def run_one(pathToMaf):
    """
    :param pathToMaf:
    :return the pipeline thread running this maf file
    """
    assert _processSemaphore is not None
    pipeline = Pipeline(pathToMaf)
    pipeline.start()
    return pipeline


if __name__ == "__main__":
    arguments = docopt(__doc__, version='Gidget Run All 0.0')
    print(arguments)
    run_all(arguments.get('<maf_manifest>'), arguments.get('--processes') or 4)

