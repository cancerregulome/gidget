#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../gidget/util/gidget_util.sh


## runs the MAF annotation pipeline

## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      snapshot name, either 'dcc-snapshot' or 'dcc-snapshot-28jun13'
##      one tumor type, eg 'ucec'
##      a config file, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <tumorType> <fullMafPath>"
        echo " Example : `basename $0` brca full-path-to-unannotated-brca-maf"
        exit $WRONGARGS
fi


tumorType=$1
pathToOriginalMAF=$2

echo using tumor code: $tumorType and input file: $pathToOriginalMAF

thisDir=`pwd`

mafDirectory=$thisDir/$tumorType
echo `date`
echo creating maf directory $mafDirectory
mkdir $mafDirectory
echo setting up maf directory $mafDirectory

cd $mafDirectory
echo $tumorType > tumorCode.txt
echo $pathToOriginalMAF > mafFilePath.txt
ln -s $pathToOriginalMAF .
echo `basename $pathToOriginalMAF` > maf_file_list
cd ..
echo




echo `date`
echo annotating MAF
cd $mafDirectory
export TCGAMAF_DATA_DIR=`pwd`
${TCGAMAF_SCRIPTS_DIR}/bash/updateMAF.sh > updateMAF.log 2>&1
outputMAF=`ls -1 *.ncm.with_uniprot`
echo MAF annotated: output maf is $outputMAF!
echo

echo `date`
echo running stats
${TCGAMAF_SCRIPTS_DIR}/bash/final_maf_diagnostics.sh $outputMAF
echo


echo `date`
echo "Done with MAF annotation pipeline"
echo done
echo

cd $thisDir

echo; echo


