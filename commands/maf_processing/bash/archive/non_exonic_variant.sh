#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


# script to output non-exonic variant types in a final MAF
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
echo start counts of non-exonic variant types
echo 1.line counts
echo SPLICING
grep "variant_type=splicing" $maf | wc -l 
echo ncRNA
grep "variant_type=ncRNA" $maf | wc -l 
echo UTR5
grep "variant_type=UTR5" $maf | wc -l 
echo UTR3
grep "variant_type=UTR3" $maf | wc -l 
echo INTRONIC
grep "variant_type=intronic" $maf | wc -l 
echo UPSTREAM
grep "variant_type=upstream" $maf | wc -l 
echo DOWNSTREAM
grep "variant_type=downstream" $maf | wc -l 
echo INTERGENIC
grep "variant_type=intergenic" $maf | wc -l 

echo 2. store in files
echo SPLICING
grep "variant_type=splicing" $maf > splicing
echo ncRNA
grep "variant_type=ncRNA" $maf > ncRNA
echo UTR5
grep "variant_type=UTR5" $maf > UTR5
echo UTR3
grep "variant_type=UTR3" $maf > UTR3 
echo INTRONIC
grep "variant_type=intronic" $maf > intronic
echo UPSTREAM
grep "variant_type=upstream" $maf > upstream
echo DOWNSTREAM
grep "variant_type=downstream" $maf > downstream
echo INTERGENIC
grep "variant_type=intergenic" $maf > intergenic

echo finished output
