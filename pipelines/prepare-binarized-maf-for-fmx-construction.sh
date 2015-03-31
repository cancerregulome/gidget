#!/bin/sh

# This script handles the post processing of the maf files, described in step 3 of <gidget_root>/commands/maf_processing/README.md

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh

#TODO this script should probably be incorporated into the maf-processing script

function showHelpAndExit {
    echo "Usage: `basename $0` [-c] [-m MUTATION_THRESHOLD] [TUMOR_TYPE] [BINARIZATION_OUTPUT]"
    echo "    -h                     display this help and exit"
    echo "    -c                     By default this script uses only code-potential mutation features. Use this option to skip the code-potential filtering step"
    echo "    -m MUTATION_THRESHOLD  Filter out features with fewer than MUTATION_THRESHOLD mutations. Default 2."

    exit ${WRONGARGS-1}
}

OPTIND=1

codePotentialOnly=1
mutationThreshold=2

while getopts "h?cm:" opt; do
    case "$opt" in
    h|\?)
        showHelpAndExit
        ;;
    c)  codePotentialOnly=0
        ;;
    m)  mutationThreshold=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

if [[ $# != 2 ]]
    then
        showHelpAndExit
fi

tumorType=$1
binarizationOutput=$2

outDir=${TCGAFMP_DATA_DIR}/${tumorType}/gnab
echo "ouputs are in $outDir"
mkdir -vp ${outDir}

cp -v ${binarizationOutput} "${TCGAFMP_DATA_DIR}/${tumorType}/gnab/latest.gnab.txt"

# first post-processing step (all this currently does is some minor clean-up and/or re-formatting)
cd ${TCGAFMP_ROOT_DIR}/shscript
./fmp03B_gnab_part.sh $tumorType

cleanUp_out="${tumorType}.gnab.tmpData1.tsv"

if [[ ${codePotentialOnly} -ne 0 ]]
then
    # keep only "code_potential" mutation features

    h1=`mktemp`
    g1=`mktemp`

    codePot_out="${tumorType}.gnab.codePot.tsv"
    head -1 ${cleanUp_out} >& ${h1}
    grep "code_potential" ${cleanUp_out} >& ${g1}
    cat ${h1} ${g1} >& ${codePot_out}

    rm ${h1} ${g1}
else
    codePot_out=${cleanUp_out}
fi

# filter out features
filter_out="${tumorType}.gnab.tmpData2.tsv"
cd ${TCGAFMP_DATA_DIR}/${tumorType}/gnab/
echo "python ${TCGAFMP_ROOT_DIR}/main/highVarTSV.py skcm.gnab.tmpData1.tsv skcm.gnab.tmpData2.tsv -${mutationThreshold} NZC" #TODO
python ${TCGAFMP_ROOT_DIR}/main/highVarTSV.py ${codePot_out} ${filter_out} -${mutationThreshold} NZC


#TODO other post-processing steps

# annotate tsv
annotate_out="${tumorType}.gnab.filter.annot.tsv"
cd ${TCGAFMP_DATA_DIR}/${tumorType}/gnab/
python ${TCGAFMP_ROOT_DIR}/main/annotateTSV.py ${filter_out} hg19 ${annotate_out}