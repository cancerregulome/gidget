#!/usr/bin/env python

import os

def ensureDir(absPath):
    if not os.path.exists(absPath):
        os.mkdir(absPath)