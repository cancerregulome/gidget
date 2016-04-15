#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


# Generate table of Items to exclude from analysis
#
# Items includes Patient, Sample, Aliquot, ..
# For details see
# https://wiki.nci.nih.gov/display/TCGA/TCGA+Annotations+Web+Service+User
#
# Input: Cancer Type, e.g. GBM
#        File of annotations terms to be excluded
# Output: Items to be excluded from Analysis 
# 
# File of annotation terms to be excluded: Each line contains single Annotation "Classification" or a ("Classification","Category") pair to be excluded. A pair needs to be tab-separated
#
# Example file (do not include hashes)
#Redaction
#CenterNotification\tItem flagged DNU

WRONGARGS=1
if [ $# != 2 ]
then
  echo "Usage: `basename $0` <Cancer Type> <Blacklisted Annotations Terms>" >&2
  exit $WRONGARGS
fi

tt=$1
uu=`echo $tt | tr '[:lower:]' '[:upper:]'`
bfile=$2

echo " "
echo " "
echo "---Retrieving "$uu" Annotations from TCGA---" 
wget https://tcga-data.nci.nih.gov/annotations/resources/searchannotations/json?disease=${uu} -O ${tt}_Annotations.json

echo "---Converting JSON to TSV---"
python $TCGAFMP_ROOT_DIR/util/json_AnnotationsManagerTCGA_to_tsv.py ${tt}_Annotations.json ${tt}_Annotations.tsv

echo " "
echo " "
echo "---Generating list of excluded items for "$tt" ---"
python $TCGAFMP_ROOT_DIR/util/ExcludedItems.py ${tt}_Annotations.tsv  $2  > ${tt}_excluded_items.tsv 
## rm -f ${tt}_Annotations.json ${tt}_Annotations.tsv
cut -f4 ${tt}_excluded_items.tsv | sort | uniq | sed -e '1,$s/"//g' | grep -v "Barcode" >& ${tt}.blacklist.samples.tsv
echo "    --> number of blacklisted samples : " `wc -l ${tt}.blacklist.samples.tsv`

