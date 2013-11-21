#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGA_MM_ROOT_DIR=/users/mmiller/tcga/sreynold_scripts/mm_src
export PYTHONPATH=$TCGA_MM_ROOT_DIR/pyclass:$TCGA_MM_ROOT_DIR/util:$PYTHONPATH

curDate=$1
snapshotName=$2
tumor=$3

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi
if [ -z "$snapshotName" ]
    then
        echo " this script must be called with a specific snapshot-name, eg dcc-snapshot "
        exit
fi
if [ -z "$tumor" ]
    then
        echo " this script must be called with at least one tumor type "
        exit
fi

echo " "
echo " "
echo " *******************"
echo " *" $curDate
echo " *" $snapshotName
echo " *******************"

args=("$@")
for ((i=2; i<$#; i++))
    do
        tumor=${args[$i]}

	## cd /titan/cancerregulome3/TCGA/outputs/$tumor
	cd /titan/cancerregulome14/TCGAfmp_outputs/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate

	rm -fr level3.*.*.$curDate.log

	## COPY-NUMBER
	python $TCGA_MM_ROOT_DIR/parse_tcga.py $TCGA_MM_ROOT_DIR/parse_tcga.config \
                broad.mit.edu/genome_wide_snp_6/snp/ $tumor \
                outSuffix=$curDate \
                out_directory=./ \
                topdir=/titan/cancerregulome11/TCGA/repositories/$snapshotName/%s/tumor/%s/cgcc/%s >& level3.broad.snp_6.$curDate.log 

    done

echo " "
echo " testMM script is FINISHED !!! "
date
echo " "

