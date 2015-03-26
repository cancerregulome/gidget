#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


# script to run diagnostics on output file after MAF processing 
#
if [ $# -ne 1 ]
then
    echo "Error in $0 - Invalid Argument Count"
    echo "Syntax: $0 MAF"
    exit
fi
maf=$1

export maf

echo
echo start diagnostics
echo 1. line counts
echo NO UNIPROT ID
grep "NO UNIPROT ID" $maf | wc -l 
echo NO UNIPROT MATCH0
grep "NO UNIPROT MATCH," $maf | wc -l
echo NO UNIPROT MATCH1
grep "NO UNIPROT MATCH1" $maf | wc -l
echo NO UNIPROT MATCH2
grep "NO UNIPROT MATCH2" $maf | wc -l
echo NO ISOFORM MATCH
grep "NO ISOFORM MATCH" $maf | wc -l

echo 2. store in files
grep "NO UNIPROT ID" $maf > no_uniprot_id
grep "NO UNIPROT MATCH," $maf > no_uniprot_match0
grep "NO UNIPROT MATCH1" $maf > no_uniprot_match1
grep "NO UNIPROT MATCH2" $maf > no_uniprot_match2
grep "NO ISOFORM MATCH" $maf > no_isoform_match

echo finished diagnostics
