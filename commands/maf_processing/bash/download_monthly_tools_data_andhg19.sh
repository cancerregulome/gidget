#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


echo
echo update ANNOVAR 
cd ${TCGA_MAF_TOOLS_DIR}
curl -O http://bioinform.usc.edu/annovar/xmpVO9ISYx/annovar.tar.gz
tar -zxvf annovar.tar.gz
cd ${TCGA_MAF_TOOLS_DIR}/annovar
chmod 777 ${TCGA_MAF_TOOLS_DIR}/annovar

echo
echo download UCSC knownGene files
humandbFolder=${TCGAMAF_REFERENCES_DIR}/HumanDB
perl annotate_variation.pl -downdb -buildver hg18 knownGene $humandbFolder
perl annotate_variation.pl -downdb -buildver hg19 knownGene $humandbFolder


