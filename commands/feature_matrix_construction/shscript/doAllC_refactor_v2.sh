#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      snapshot name, either 'dcc-snapshot' or 'dcc-snapshot-28jun13'
##      one tumor type, eg 'ucec'
##      a config file, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [[ $# != 5 ]] && [[ $# != 7 ]]
    then
        echo " Usage   : `basename $0` <curDate> <snapshotName> <tumorType> <config> <public/private> [auxName] [ignoreAM=yes/no]"
        echo " Example : `basename $0` 28oct13  dcc-snapshot-28oct13  brca  parse_tcga.27_450k.config  public  aux  no"
        echo " "
        echo " Note that the new auxName option at the end is optional and will default to simply aux "
        echo " Note that the ignoreAM (ignore annotations-manager) option is also optional and will default to no "
        echo " However, if you want to use either of these two optional command-line arguments, you MUST use BOTH "
        exit $WRONGARGS
fi

curDate=$1
snapshotName=$2
oneTumor=$3
config=$4
ppString=$5

if (( $# == 7 ))
    then
        auxName=$6
        ignoreAM=$7
    else
        auxName=aux
        ignoreAM=no
fi

if [ ! -d $TCGAFMP_DATA_DIR/$oneTumor ]
    then
        echo " "
        echo "     --> creating new directory " $TCGAFMP_DATA_DIR/$oneTumor
        echo " "
        mkdir $TCGAFMP_DATA_DIR/$oneTumor
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/$auxName
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/gnab
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/scratch
fi

rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.$snapshotName.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp*.$curDate.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/$curDate/*.*


$TCGAFMP_ROOT_DIR/shscript/fmp01B_xml_refactor.sh $curDate $snapshotName $oneTumor $config $ppString $auxName $ignoreAM >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp01B.$curDate.$snapshotName.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp02B_L3_refactor.sh  $curDate $snapshotName $oneTumor $config >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp02B.$curDate.$snapshotName.$oneTumor.log

$TCGAFMP_ROOT_DIR/shscript/fmp05B_filter.sh     $curDate $oneTumor $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp05B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp06B_merge.sh      $curDate $oneTumor $ppString $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp06B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp07B_misc.sh       $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp07B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp08B_checkMeth.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp08B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp09B_addGnab.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp09B.$curDate.$oneTumor.log
$TCGAFMP_ROOT_DIR/shscript/fmp10B_splitType_v2.sh  $curDate $oneTumor $ppString $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp10B.$curDate.$oneTumor.log
## $TCGAFMP_ROOT_DIR/shscript/fmp11B_mergeNT.sh    $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp11B.$curDate.$oneTumor.log

if [ "$ppString" = 'private' ]
    then
        $TCGAFMP_ROOT_DIR/shscript/fmp15B_survival.sh     $curDate $oneTumor $auxName >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp15B.$curDate.$oneTumor.log
fi

## $TCGAFMP_ROOT_DIR/shscript/fmp16B_finalFilter.sh  $curDate $oneTumor >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/fmp16B.$curDate.$oneTumor.log

