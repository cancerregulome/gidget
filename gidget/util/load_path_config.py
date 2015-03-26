#!/usr/bin/env python

import os
from os.path import join as pthJoin
from ConfigParser import SafeConfigParser
import sys

from pipeline_util import expandPath as pthExpanded

COMMANDS_DIR = 'commands'

# mini spec that maps from config lines to gidget env var names
# [ (section, [ (option_name, env_name) ] ) ]
optionMap = [
    ('maf', [
        ('TCGAMAF_OUTPUTS', 'TCGAMAF_OUTPUTS'),
        ('TCGAMAF_DATA_DIR', 'TCGAMAF_DATA_DIR'),
        ('TCGAMAF_REFERENCES_DIR', 'TCGAMAF_REFERENCES_DIR'),
    ]),
    ('binarization', [
        ('TCGABINARIZATION_DATABASE_DIR','TCGABINARIZATION_DATABASE_DIR'),
        ('TCGABINARIZATION_REFERENCES_DIR', 'TCGABINARIZATION_REFERENCES_DIR'),
    ]),
    ('fmp', [
        ('TCGAFMP_PYTHON3', 'TCGAFMP_PYTHON3'),
        ('TCGAFMP_BIOINFORMATICS_REFERENCES', 'TCGAFMP_BIOINFORMATICS_REFERENCES'),
        ('TCGAFMP_SCRATCH', 'TCGAFMP_SCRATCH'),
        ('TCGAFMP_DCC_REPOSITORIES', 'TCGAFMP_DCC_REPOSITORIES'),
        ('TCGAFMP_FIREHOSE_MIRROR', 'TCGAFMP_FIREHOSE_MIRROR'),
        ('TCGAFMP_PAIRWISE_ROOT', 'TCGAFMP_PAIRWISE_ROOT'),
        ('TCGAFMP_LOCAL_SCRATCH', 'TCGAFMP_LOCAL_SCRATCH'),
        ('TCGAFMP_CLUSTER_SCRATCH', 'TCGAFMP_CLUSTER_SCRATCH'),
        ('TCGAFMP_CLUSTER_HOME', 'TCGAFMP_CLUSTER_HOME'),
    ]),
    ('python', [
        ('TCGAMAF_PYTHON_BINARY', 'TCGAMAF_PYTHON_BINARY'),
    ]),
    ('tools', [
        ('TCGAMAF_TOOLS_DIR', 'TCGAMAF_TOOLS_DIR'),
        ('LD_LIBRARY_PATH', 'LD_LIBRARY_PATH'),
    ])]

# pth = path
# pthd = path to a directory
# apth = absolute path

def envFromConfigOrOs(pthConfig):
    if pthConfig is None:
        return os.environ
    else:
        return envFromConfig(pthConfig)

def envFromConfig(pthConfig):

    parser = SafeConfigParser()
    parser.read(pthConfig)

    env = os.environ

    pthdGidgetRoot = pthExpanded(parser.get('gidget', 'GIDGET_SOURCE_ROOT'))
    pthdFmpRoot = pthJoin(pthdGidgetRoot, COMMANDS_DIR, 'feature_matrix_construction')
    pthdMafRoot = pthJoin(pthdGidgetRoot, COMMANDS_DIR, 'maf_processing')
    pthdMafScripts = pthdMafRoot

    env['GIDGET_SOURCE_ROOT'] = pthdGidgetRoot
    env['TCGAFMP_ROOT_DIR'] = pthdFmpRoot
    env['TCGAMAF_ROOT_DIR'] = pthdMafRoot
    env['TCGAMAF_SCRIPTS_DIR'] = pthdMafScripts

    rgpthdAddToPypath = (
        pthJoin(pthdGidgetRoot, 'gidget', 'util'),
        pthJoin(pthdMafRoot, 'python'),
        pthJoin(pthdFmpRoot, 'util'))

    sys.path.append(rgpthdAddToPypath)

    # we also need to add these to the PYTHONPATH variable to ensure that they are properly propagated to subprocesses
    env['PYTHONPATH'] = ('%s:' * len(rgpthdAddToPypath)) % rgpthdAddToPypath + os.environ['PYTHONPATH']

    for section in optionMap:
        stSection = section[0]
        options = section[1]
        for option in options:
            stOption = option[0]
            stEnv = option[1]
            pthOption = pthExpanded(parser.get(stSection, stOption))
            env[stEnv] = pthOption
            os.environ[stEnv] = pthOption

    return env