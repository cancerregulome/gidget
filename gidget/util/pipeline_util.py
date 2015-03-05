#!/usr/bin/env python

import os
from fnmatch import fnmatch
from os.path import join as pathjoin

def ensureDir(absPath):
    if not os.path.exists(absPath):
        os.mkdir(absPath)

def findBinarizationOutput(outputdir):
    binarizationOutput = None
    for outfile in os.listdir(outputdir):
        if fnmatch(outfile, 'mut_bin_*.txt'):
            binarizationOutput = pathjoin(outputdir, outfile)
            break
    return binarizationOutput

def expandPath(path):
    if path is None: return path
    return os.path.expanduser(os.path.expandvars(path))
