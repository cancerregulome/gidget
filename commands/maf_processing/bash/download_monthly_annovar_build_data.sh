#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAFMP_ROOT_DIR}/bash/tcga_maf_util.sh


if [ -z $MAF_REFERENCES_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Reference directory not defined! Aborting."
        exit
fi

if [ -z $MAF_TOOLS_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Tools folder not defined! Aborting."
        exit
fi

referenceFolder="$MAF_REFERENCES_DIR"
toolsFolder="$MAF_TOOLS_DIR"

cd $toolsFolder/annovar
echo
echo download UCSC knownGene files
humandbFolder=$referenceFolder/HumanDB
./annotate_variation.pl -downdb -buildver hg18 knownGene $humandbFolder
./annotate_variation.pl -downdb -buildver hg19 knownGene $humandbFolder


