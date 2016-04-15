#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      snapshot name, either 'dcc-snapshot' or 'dcc-snapshot-28jun13'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [[ $# != 4 ]] && [[ $# != 5 ]]
    then
        echo " Usage   : `basename $0` <curDate> <snapshotName> <tumorType> <public/private> [auxName]"
        echo " Example : `basename $0` testX     dcc-snapshot   coadreadX   public"
        echo " "
        echo " Note that the new auxName option at the end is optional and will default to simply aux "
        exit $WRONGARGS
fi

curDate=$1
snapshotName=$2
oneTumor=$3
ppString=$4

if (( $# == 5 ))
    then
        auxName=$5
    else
        auxName=aux
fi

$TCGAFMP_ROOT_DIR/shscript/fmp06B_merge.sh      $curDate $oneTumor $ppString $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp06B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp07B_misc.sh       $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp07B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp08B_checkMeth.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp08B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp09B_addGnab.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp09B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp10B_splitType_v2.sh  $curDate $oneTumor $ppString $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp10B.$curDate.$oneTumor.log

$TCGAFMP_ROOT_DIR/shscript/fmp15B_survival.sh     $curDate $oneTumor $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp15B.$curDate.$oneTumor.log

