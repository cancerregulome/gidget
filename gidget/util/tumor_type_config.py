#!/usr/bin/env python

import os.path as path
import sys
import csv

TUMOR_CONFIG_DIALECT = "tumor-type-config"
csv.register_dialect(TUMOR_CONFIG_DIALECT, delimiter=',', lineterminator='\n', skipinitialspace=True)

_relpath_configfile = path.join('config', 'tumorTypesConfig.csv')

_configfile = path.expandvars(path.join('${GIDGET_SOURCE_ROOT}', _relpath_configfile))

if not path.exists(_configfile):
    # KLUDGE
    _configfile = path.join(path.dirname(path.dirname(path.dirname(path.abspath(sys.modules[__name__].__file__)))), _relpath_configfile)

if not path.exists(_configfile):
    print("cannot find tumor-type configuration file")
    sys.exit(1)

tumorTypeConfig = { }

with open(_configfile) as tsv:
    for tumorType in csv.DictReader(tsv, dialect=TUMOR_CONFIG_DIALECT):
        tumorTypeConfig[tumorType['name']] = tumorType
