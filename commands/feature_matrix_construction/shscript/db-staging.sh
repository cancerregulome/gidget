#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


## this script should be called with the following parameters:
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad thca skcm stad'

if [ $# != 3 ]
    then
        echo " Usage   : `basename $0` <curDate> <stagingDir>"
        echo " Example : `basename $0` 28oct13 /local/staging"
        exit -1
fi

curDate=$1
stagingDir=$2

for tumor in `cat $TCGAFMP_SCRIPT_DIR /tumor-types.txt`; do 
  tumor_UC=`echo $tumor | tr [:lower:] [:upper:]`
  for fmx in `ls -1 $TCGAFMP_DATA_DIR/$tumor/$tumor.all.tsv`; do
    echo found $fmx
    mkdir -p $curDate/$tumor
    cp $fmx $curDate/$tumor
    orignalFMXName=$fmx
    newFMXName=$fmx
    mv $t/20131223/$lc.all.23dec13.tsv $t/20131223/$t.20131223.tsv; 
    echo "Original file provided by sreynolds at $originalFMXName, copied as $newFMXName" > $newFMXName.provenance
  done
done
