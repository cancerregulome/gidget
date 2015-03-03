#!/bin/bash

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh


## runs the binarization pipeline

## this script should be called with the following parameters:
##      tumorType	eg 'brca'
##      fullAnnotatedMafPath


if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <tumorType> <fullAnnotatedMafPath>"
        echo " Example : `basename $0` brca full-path-to-brca-maf.ncm.with_uniprot"
        exit $WRONGARGS
fi


tumorType=$1
pathToAnnotatedMAF=$2

echo using tumor code: $tumorType and input file: $pathToAnnotatedMAF

# TODO:FILE_LAYOUT:WORKING_DIR
thisDir=`pwd`
binarizationDirectory=$thisDir/$tumorType



echo `date`
echo creating binarization directory $binarizationDirectory
mkdir $binarizationDirectory
echo "setting up binarization directory $binarizationDirectory"

cd $binarizationDirectory
echo $tumorType > tumorCode.txt
echo $pathToAnnotatedMAF > annotatedMafFilePath.txt
ln -s $pathToAnnotatedMAF .
annotatedMAFFileName=`basename $pathToAnnotatedMAF`
cd ..
echo



echo `date`
echo processing annotated MAF -- binarization
cd $binarizationDirectory
datecode=`date "+%m.%d.%Y"`
binarizationOutputName="mut_bin_${datecode}.txt"
${GIDGET_SOURCE_ROOT}/commands/binarization/mutation_binarization_annovar.pl $annotatedMAFFileName > ${binarizationOutputName}

echo "done: output filename is ${binarizationOutputName}"
echo



echo `date`
echo processing annotated MAF -- mutation summary
mutationSummaryOutputFilename="mut_summary_${datecode}.txt"
${GIDGET_SOURCE_ROOT}/commands/binarization/genes_and_mutations_annovar.pl $tumorType $annotatedMAFFileName > $mutationSummaryOutputFilename
echo $done
echo



echo `date`
echo "Done with MAF annotation pipeline"
echo done
echo


cd $thisDir



echo; echo
