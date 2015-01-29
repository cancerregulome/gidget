#!/bin/bash

# This script loads the processed feature matrix into Regulome Explorer

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/gidget_util.sh

#TODO ssh?

if [[ $# != 1 ]]
    then
        echo " Usage   : `basename $0` <path to META file> "
        echo " Example : `basename $0` $TCGAFMP_DATA_DIR/thca/08jul13/META/META.thca.TP.pw "
        echo " "
        echo " note: snapshotName is optional. If not specified, will use most current snapshot "
        exit 1
fi

metaFile=$1

#TODO insert data into meta_file

cd /titan/cancerregulome10/regulome-explorer/src/dataimport/python

/tools/bin/python2.7 start_re_dataimport_fixed.py $metaFile  ../config/rfex_sql_breve.config

