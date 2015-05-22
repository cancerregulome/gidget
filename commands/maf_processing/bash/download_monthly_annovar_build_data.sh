#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


echo
echo download UCSC knownGene files
humandbFolder=${TCGAMAF_REFERENCES_DIR}/HumanDB
${TCGAMAF_TOOLS_DIR}/annotate_variation.pl -downdb -buildver hg18 knownGene $humandbFolder
${TCGAMAF_TOOLS_DIR}/annotate_variation.pl -downdb -buildver hg19 knownGene $humandbFolder


