#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad thca skcm stad'

if [ $# != 4 ]
    then
        echo " Usage   : `basename $0` <curDateNumeric> <stagingDir> <host> <port>"
        echo " Example : `basename $0` 20140101 /local/staging localhost 27017"
        exit -1
fi

curDateNumeric=$1
stagingDir=$2
host=$3
port=$4

#brca/test_public/brca.all.test_public.tsv
for tumor in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`; do
  tumor_UC=`echo $tumor | tr [:lower:] [:upper:]`
  $TCGAFMP_ROOT_DIR/../database_loading/insert_featurematrix_mongodb.py --fmx-dir $stagingDir/$curDateNumeric/$tumor_UC --host $host --port $port --db $tumor_UC --collection feature_matrix
done
