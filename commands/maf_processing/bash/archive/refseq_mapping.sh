#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


referenceFolder="$MAF_REFERENCES_DIR"
#using refseq instead of UCSC known genes
echo
echo map transcipt id to uniprot id
knownGene=$referenceFolder"/HumanDB/hg18_kgXref.txt"
cut -d'	' -f1,3 $knownGene | awk '{if($2 != "") {print $0}}' > $referenceFolder"/knowngene_to_protein"
