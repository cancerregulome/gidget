#!/bin/bash

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh


## runs the MAF annotation pipeline

## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      snapshot name, either 'dcc-snapshot' or 'dcc-snapshot-28jun13'
##      one tumor type, eg 'ucec'
##      a config file, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

if [[ $# != 2 && $# != 3 ]]
    then
        echo " Usage   : `basename $0` <tumorType> <fullMafPath> [errorRateThreshold (default 0.1)]"
        echo " Example : `basename $0` brca full-path-to-unannotated-brca-maf 0.1"
        exit $WRONGARGS
fi


tumorType=$1
pathToOriginalMAF=$2

if [[ $# == 3 ]]
    then
        errorThreshold=$3
    else
        errorThreshold=0.1
fi

echo using tumor code: $tumorType and input file: $pathToOriginalMAF

# TODO:FILE_LAYOUT:WORKING_DIR
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
export TCGAMAF_DATA_DIR=`pwd` # TODO:FILE_LAYOUT:WORKING_DIR
${TCGAMAF_SCRIPTS_DIR}/bash/updateMAF.sh 2>&1 | tee updateMAF.log

status=${PIPESTATUS[0]}
if [[ $status -ne 0 ]]
then
    echo "updateMAF.sh exited with status $status. Maf-annotation will now exit."
    exit $status
fi

outputMAF=`ls -1 *.ncm.with_uniprot`
echo MAF annotated: output maf is $outputMAF!
echo



echo `date`
echo running stats
${TCGAMAF_SCRIPTS_DIR}/bash/final_maf_diagnostics.sh $outputMAF
echo

# Perform validation
getLines="wc -l | sed -e 's#\(\w\+\)\W\+.\+#\1#'"
numValid=`eval "cat ./*.ncm.with_uniprot | $getLines"`
numError=`eval "cat ./no_* | $getLines"`

${GIDGET_SOURCE_ROOT}/gidget/util/log.py "DEBUG" "Number of Valid Lines: $numValid"
${GIDGET_SOURCE_ROOT}/gidget/util/log.py "DEBUG" "Number of Error Lines: $numError"

if [[ `bc -l <<< "$numError / $numValid < $errorThreshold"` -eq 0 ]]
then
    ${GIDGET_SOURCE_ROOT}/gidget/util/log.py "FATAL" "Error rate for annotated MAF too high!"
    ${GIDGET_SOURCE_ROOT}/gidget/util/log.py "DEBUG" "Threshold: $errorThreshold"
    exit -1
fi

echo `date`
echo "Done with MAF annotation pipeline"
echo done
echo


cd $thisDir



echo; echo


