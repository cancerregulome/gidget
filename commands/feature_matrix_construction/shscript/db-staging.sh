#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad thca skcm stad'

if [ $# != 3 ]
    then
        echo " Usage   : `basename $0` <fmxRunName> <curDateNumeric> <stagingDir>"
        echo " Example : `basename $0` private-run 20140101 /local/staging"
        exit -1
fi

fmxRunName=$1
curDateNumeric=$2
stagingDir=$3

#brca/test_public/brca.all.test_public.tsv
for tumor in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`; do 
  tumor_UC=`echo $tumor | tr [:lower:] [:upper:]`

  for fmx in `ls -1 $TCGAFMP_DATA_DIR/$tumor/$fmxRunName/$tumor.all.$fmxRunName.tsv`; do
    echo found $fmx
    newFMXDir=$stagingDir/$curDateNumeric/$tumor_UC
    mkdir -p $newFMXDir
    cp $fmx $newFMXDir
    #orignalFMXName=$fmx # $tumor.all.$fmxRunName.tsv
    #newFMXName=$fmx
    #mv $t/20131223/$lc.all.23dec13.tsv $t/20131223/$tumor.20131223.tsv;
    echo "Original file provided by sreynolds at $fmx" > $newFMXDir/provenance.fmx
  done
done
