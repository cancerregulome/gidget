#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      one or more tumor types, eg: 'prad thca skcm stad'
curDate=$1
tumor=$2

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
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
echo " *******************"

args=("$@")
for ((i=1; i<$#; i++))
    do
        tumor=${args[$i]}

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

	rm -fr $tumor.rawMerge.$curDate.log
	rm -fr $tumor.rawMerge.$curDate.tsv

	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		finalClin.$tumor.$curDate.tsv \
		$tumor.mirn.tmpData2.tsv \
		$tumor.cnvr.tmpData3.tsv \
		$tumor.meth.tmpData2.tsv \
		$tumor.rppa.tmpData3.tsv \
		$tumor.msat.tmpData3.tsv \
		$tumor.gexp.seq.tmpData2.tsv \
		$tumor.gexp.ary.tmpData2.tsv \
		../gnab/$tumor.gnab.tmpData1.tsv \
		$tumor.rawMerge.$curDate.tsv >& $tumor.rawMerge.$curDate.log 

	## HERE... add in annotation step ??? 

    done

echo " "
echo " fmp04B_rawMerge script is FINISHED !!! "
date
echo " "

