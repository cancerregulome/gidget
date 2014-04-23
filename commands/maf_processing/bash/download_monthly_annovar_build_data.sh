#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/bash/tcga_maf_util.sh


cd ${TCGAMAF_TOOLS_DIR}/annovar
echo
echo download UCSC knownGene files
humandbFolder=${TCGAMAF_REFERENCES_DIR}/HumanDB
./annotate_variation.pl -downdb -buildver hg18 knownGene $humandbFolder
./annotate_variation.pl -downdb -buildver hg19 knownGene $humandbFolder


