#!/bin/bash

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/gidget_util.sh


## runs the binarization pipeline

## this script should be called with the following parameters:
##      tumorType	eg 'brca'
##      fullAnnotatedMafPath


if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <tumorType> <fullAnnotatedMafPath>"
        echo " Example : `basename $0` brca full-path-to-annotated-brca-maf"
        exit $WRONGARGS
fi


tumorType=$1
pathToAnnotatedMAF=$2

echo using tumor code: $tumorType and input file: $pathToAnnotatedMAF

thisDir=`pwd`
binarizationDirectory=$thisDir/$tumorType



echo `date`
echo creating binarization directory $binarizationDirectory
mkdir $binarizationDirectory
echo setting up maf directory $binarizationDirectory

cd $binarizationDirectory
echo $tumorType > tumorCode.txt
echo $pathToAnnotatedMAF > annotatedMafFilePath.txt
ln -s $pathToAnnotatedMAF .
cd ..
echo



echo `date`
echo processing annotated MAF
cd $binarizationDirectory
echo



echo `date`
echo "Done with MAF annotation pipeline"
echo done
echo


cd $thisDir



echo; echo
