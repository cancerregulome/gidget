#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export TCGAFMP_DATA_DIR=$TCGAFMP_DATA_DIR
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

curDate=22mar13
snapshotName=dcc-snapshot-22mar13
oneTumor=ucec

rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.$snapshotName.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.$oneTumor.log

## $TCGAFMP_ROOT_DIR/shscript/fmp01B_xml.sh $curDate $snapshotName $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp01B.$curDate.$snapshotName.$oneTumor.log
## $TCGAFMP_ROOT_DIR/shscript/fmp02B_L3.sh  $curDate $snapshotName $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp02B.$curDate.$snapshotName.$oneTumor.log

$TCGAFMP_ROOT_DIR/shscript/fmp05B_filter.sh     $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp05B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp06B_merge.sh      $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp06B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp07B_misc.sh       $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp07B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp08B_checkMeth.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp08B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp09B_addGnab.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp09B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp10B_splitType.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp10B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp11B_mergeNT.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp11B.$curDate.$oneTumor.log


