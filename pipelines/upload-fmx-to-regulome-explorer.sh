#!/bin/bash

# This script loads the processed feature matrix into Regulome Explorer

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh

#TODO ssh?

if [[ $# != 3 ]]
    then
        echo " Usage   : `basename $0` <path to META file> <comment> <description>"
        echo " Example : `basename $0` $TCGAFMP_DATA_DIR/thca/08jul13/META/META.thca.TP.pw \"A dataset\" \"This is some data\""
        echo " "
        echo " note: snapshotName is optional. If not specified, will use most current snapshot "
        exit 1
fi

metaFile=$1
comment=$2
description=$3

tmp=`mktemp`

sed -e "s/COMMENT_TEXT_HERE/$comment/" \
    -e "s/DESCRIPTION_TEXT_HERE/$description/" \
    -e "s/DATA_SET_DATE_HERE/`date +%d-%b-%Y`/" \
    ${metaFile} > ${tmp}

cd /titan/cancerregulome10/regulome-explorer/src/dataimport/python

/tools/bin/python2.7 start_re_dataimport_fixed.py ${tmp}  ../config/rfex_sql_breve.config

rm ${tmp}

