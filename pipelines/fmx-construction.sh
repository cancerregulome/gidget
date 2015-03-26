#!/bin/bash

# This script is meant to automate and streamline the feature matrix construction pipeline for a particular tumor type.
# See <gidget_root>/commands/feature_matrix_construction/README.md for an in-depth description of how this pipeline works.

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/gidget_util.sh

if [[ $# != 5 && $# != 4 ]]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> <public/private> <fmxSuffix> [snapshotName] "
        echo " Example : `basename $0` 28oct13 brca private TB.tsv dcc-snapshot-28oct13 "
        echo " "
        echo " note: snapshotName is optional. If not specified, will use most current snapshot "
        exit 1
fi

date=$1
tumorType=$2
ppString=$3
fmxSuffix=$4

if [[ $# == 5 ]]
    then
        snapshotName=$5
    else
        snapshotName="dcc-snapshot"
fi

#TODO?: ensure tumor is valid type

# Ensure that maf processing has been completed
processedMutationData="${TCGAFMP_DATA_DIR}/${tumorType}/gnab/${tumorType}.gnab.tmpData4b.tsv"
if [[ ! -s $processedMutationData ]]
then
    echo "Looking for processed mutation data at location ${processedMutationData}"
    echo "Please ensure that maf files have been processed."
    echo "See README under commands/maf_processing."
    echo "This script will now exit."
    exit 1
else
    echo "Using processed mutation data at ${processedMutationData}"
fi

localDcMirror="${TCGAFMP_DCC_REPOSITORIES}/dcc-mirror/public/tumor/${tumorType}/cgcc/jhu-usc.edu/"

if [[ `ls -A1 ${localDcMirror}/humanmethylation450/methylation/*Level_3*.tar.gz | wc -l` -eq 0 ]]
then
    echo "Missing 450k methylation data. The script will now exit"
    exit 1
fi

if [[ `ls -A1 ${localDcMirror}/humanmethylation27/methylation/*Level_3*.tar.gz | wc -l` -eq 0 ]]
then
    echo "Did not find any 27k methylation data for tumor type $tumorType"

    fmxConfig="parse_tcga.all450k.config"
    fmxScript="doAllC_refactor_450_v2.sh"

    newestMethylationData=`ls -t1 ${localDcMirror}/humanmethylation450/methylation/*Level_3*.tar.gz/* | head -n 1`
    prepped450k="${TCGAFMP_DATA_DIR}/${tumorType}/meth450k/${tumorType}.meth_gexp_mirn.plus.annot.tsv"

    if [[ ( ! -f ${prepped450k} ) || ( ${newestMethylationData} -nt ${prepped450k} ) ]]
    then
        echo "processing 450k data"
        needRunFmx=true
        ${TCGAFMP_ROOT_DIR}/shscript/prep450k.sh $tumorType $snapshotName
    else
        echo "450k data already processed and up-to-date"
    fi
else
    echo "Found both 27k and 450k methylation data for tumor type $tumorType"

    fmxConfig="parse_tcga.27_450k.config"
    fmxScript="doAllC_refactor_v2.sh"
fi

fmxCheckDate="${TCGAFMP_DATA_DIR}/${tumorType}/${date}/${tumorType}.seq.${date}.summary" # TODO verify that this file is actually guarenteed to be generated with fmx creation

echo $fmxCheckDate

if [[ ( ! -f ${fmxCheckDate} ) || ( ${processedMutationData} -nt ${fmxCheckDate} ) || ( $needRunFmx = true ) ]]
then
    echo "Running Heterogeneous FMx construction"
    ${TCGAFMP_ROOT_DIR}/shscript/${fmxScript} $date $snapshotName $tumorType $fmxConfig $ppString
    echo "FMx construction completed. Moving on to pairwise processing"
else
    echo "Feature Matrix up-to-date. Skipping to pairwise processing"
fi

#Run pairwise analysis
${TCGAFMP_ROOT_DIR}/shscript/PairProcess-v2.sh $date $tumorType $fmxSuffix


#TODO edit META file and fill in places like "DESCRIPTION_TEXT_HERE"