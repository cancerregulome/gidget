#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


# script to print exonic and non-exonic variant types in a final MAF
#
if [ $# -ne 1 ]
then
    echo "Error in $0 - Invalid Argument Count"
    echo "Syntax: $0 MAF"
    exit
fi
maf=$1."with_uniprot"
exonic=$1."annovar_exonic_variant_function"
nonexonic=$1."annotation_errors"
export maf
export exonic
export nonexonic

echo
echo start counts of exonic variant types
echo TOTAL EXONIC
wc -l $exonic
echo
echo FRAMESHIFT INSERTION
grep -v "nonframeshift insertion" $exonic | grep "frameshift insertion" | wc -l 
echo FRAMESHIFT DELETION
grep -v "nonframeshift deletion" $exonic | grep "frameshift deletion" | wc -l 
echo FRAMESHIFT SUBSTITUTION
grep -v "nonframeshift substitution" $exonic | grep "frameshift substitution" | wc -l 
echo STOPGAIN
grep "stopgain" $exonic | wc -l 
echo STOPLOSS
grep "stoploss" $exonic | wc -l 
echo NONFRAMESHIFT INSERTION
grep "nonframeshift insertion" $exonic | wc -l 
echo NONFRAMESHIFT DELETION
grep "nonframeshift deletion" $exonic | wc -l 
echo NONFRAMESHIFT SUBSTITUTION
grep "nonframeshift substitution" $exonic | wc -l 
echo NONSYNONYMOUS SNV
grep "nonsynonymous SNV" $exonic | wc -l 
echo SYNONYMOUS SNV
grep -v "nonsynonymous SNV" $exonic | grep "synonymous SNV" | wc -l 
echo UNKNOWN
grep "unknown" $exonic | wc -l 
echo

echo start counts of non-exonic variant types
echo TOTAL NON-EXONIC
grep "[[:digit:]]*" $nonexonic
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
echo finished output
