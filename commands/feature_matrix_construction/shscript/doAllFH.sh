#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'
##      path to Firehose data files
##      name of Firehose subset

WRONGARGS=1
if [ $# != 4 ]
    then
        echo " Usage   : `basename $0`  <curDate>  <tumorType>  <fhDir>  <fhSubset> "
        echo " Example : `basename $0`  28oct13FH  skcm  <path to>/TCGA/firehose/awg_skcm__2013_10_13  All_Samples "
        exit $WRONGARGS
fi

curDate=$1
oneTumor=$2
fhDir=$3
fhSubset=$4

if [ ! -d $TCGAFMP_DATA_DIR/$oneTumor ]
    then
        echo " "
        echo "     --> creating new directory " $TCGAFMP_DATA_DIR/$oneTumor
        echo " "
        mkdir $TCGAFMP_DATA_DIR/$oneTumor
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/aux
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/gnab
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/scratch
fi

rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.FH.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/$curDate/*.*


$TCGAFMP_ROOT_DIR/shscript/fmp01B_FH.sh $curDate $oneTumor $fhDir $fhSubset >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp01B.$curDate.FH.$oneTumor.log
## $TCGAFMP_ROOT_DIR/shscript/fmp02B_L3_FH.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp02B.$curDate.FH.$oneTumor.log

$TCGAFMP_ROOT_DIR/shscript/fmp05B_filter.sh        $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp05B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp06B_merge.sh         $curDate $oneTumor private >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp06B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp07B_misc.sh          $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp07B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp08B_checkMeth.sh     $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp08B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp09B_addGnab.sh       $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp09B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp10B_splitType_FH.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp10B.$curDate.$oneTumor.log
## $TCGAFMP_ROOT_DIR/shscript/fmp11B_mergeNT.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp11B.$curDate.$oneTumor.log

$TCGAFMP_ROOT_DIR/shscript/fmp15B_survival.sh     $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp15B.$curDate.$oneTumor.log

## $TCGAFMP_ROOT_DIR/shscript/fmp16B_finalFilter.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp16B.$curDate.$oneTumor.log

