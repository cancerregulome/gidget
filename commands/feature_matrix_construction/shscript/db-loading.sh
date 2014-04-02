#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


if [ $# != 5 ]
    then
        echo " Usage   : `basename $0` <curDate> <stagingDir> <host> <port>"
        echo " Example : `basename $0` 28oct13 /local/staging"
        exit -1
fi

curDate=$1
stagingDir=$2
host=$3
port=$4

for tumor in `cat $TCGAFMP_SCRIPT_DIR /tumor-types.txt`; do
  $TCGAFMP_ROOT_DIR/../database_loading/insert_featurematrix_mongodb.py --fmx-dir $stagingDir/$numDate/$tumor.tsv --host $host --port $port --db $tumor-curdate --collection feature_matrix
done