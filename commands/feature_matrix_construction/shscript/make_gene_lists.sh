#!/bin/bash

if [ $# -ne 1 ]
then
  echo "Usage:   `basename $0` TCGA-fmp-output-directory"
  echo "         TCGA-fmp-output-directory must contain subdirectories named as the tumor types"
  echo "example: for disk structure as"
  echo "           <path to TCGA outputs>/TCGAfmp_outputs"
  echo "           etc,"
  echo "         use"
  echo "           `basename $0` <path to TCGA outputs>/TCGAfmp_outputs"
  exit -1
fi

TCGA_FMP_OUTPUT_DIR=$1


echo " "
date
echo " "

curDate=$1

cd $TCGA_FMP_OUTPUT_DIR/

for f in */$curDate/*.gexp.???.tmpData2.tsv
    do
	echo " "
	rm -fr t?
	g=${f/tmpData2.tsv/list}
	echo $f
	echo $g
	grep "^N:GEXP:" $f | cut -f1 >& t1
	sed -e '1,$s/:/	/g' t1 | cut -f3 | sort >& t2
	wc -l t2
	rm -fr $g
	mv t2 $g
	rm -fr t?
    done
