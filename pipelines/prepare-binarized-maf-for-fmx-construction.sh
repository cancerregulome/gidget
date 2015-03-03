#!/bin/sh

# This script handles the post processing of the maf files, described in step 3 of <gidget_root>/commands/maf_processing/README.md

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh

#TODO this script should probably be incorporated into the maf-processing script

if [[ $# != 2 ]] && [[ $# != 3 ]]
    then
        echo " Usage   : `basename $0` <tumorType> <binarizationOutput> [mutationThreshold]"
        echo " Example : `basename $0` laml laml/mut_bin_01.14.2015.txt"
        echo ""
        echo "NOTE: Features that have fewer than mutationThreshold mutations will be filtered out. Defaults to 2."
        exit 1
fi

tumorType=$1
binarizationOutput=$2

#TODO instead of providing this as a parameter, get from a config file per tumor type?
if [[ $# == 3 ]]
then
    mutationThreshold=$3
else
    mutationThreshold=2
fi

outDir=${TCGAFMP_DATA_DIR}/${tumorType}/gnab
echo "ouputs are in $outDir"
mkdir -vp ${outDir}

cp -v ${binarizationOutput} "${TCGAFMP_DATA_DIR}/${tumorType}/gnab/latest.gnab.txt"

# first post-processing step (all this currently does is some minor clean-up and/or re-formatting)
cd ${TCGAFMP_ROOT_DIR}/shscript
./fmp03B_gnab_part.sh $tumorType

cleanUp_out="${tumorType}.gnab.tmpData1.tsv"

# filter out features
filter_out="${tumorType}.gnab.tmpData2.tsv"
cd ${TCGAFMP_DATA_DIR}/${tumorType}/gnab/
echo "python ${TCGAFMP_ROOT_DIR}/main/highVarTSV.py skcm.gnab.tmpData1.tsv skcm.gnab.tmpData2.tsv -${mutationThreshold} NZC" #TODO
python ${TCGAFMP_ROOT_DIR}/main/highVarTSV.py ${cleanUp_out} ${filter_out} -${mutationThreshold} NZC

#TODO other post-processing steps

# annotate tsv
annotate_out="${tumorType}.gnab.filter.annot.tsv"
cd ${TCGAFMP_DATA_DIR}/${tumorType}/gnab/
python ${TCGAFMP_ROOT_DIR}/main/annotateTSV.py ${filter_out} hg19 ${annotate_out}