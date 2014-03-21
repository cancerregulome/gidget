#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script can be run anytime after fmp05 ...

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

	## this code is for Lisa's pancan analysis, so we start with the
	## gexp tmpData2 data files because they have not been filtered,
	## and we do the following:
	##	a) merge with clinical information
	##	b) add jitter
	##	c) copy clinical information as needed
	##	d) add sampleType feature
	##	e) split by sampleType

	if [ -f $tumor.gexp.seq.tmpData2.tsv ]
	    then
		rm -fr $tumor.pc?.seq.$curDate.tsv
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			finalClin.$tumor.$curDate.tsv \
			$tumor.gexp.seq.tmpData2.tsv \
			$tumor.pc1.seq.$curDate.tsv

		python $TCGAFMP_ROOT_DIR/main/jitterTSV.py \
			$tumor.pc1.seq.$curDate.tsv \
			$tumor.pc2.seq.$curDate.tsv

		python $TCGAFMP_ROOT_DIR/main/copyClinInfo.py \
			$tumor.pc2.seq.$curDate.tsv \
			$tumor.pc3.seq.$curDate.tsv
	
		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
			$tumor.pc3.seq.$curDate.tsv \
			$tumor.pc4.seq.$curDate.tsv
	
		python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
			$tumor.pc4.seq.$curDate.tsv sampleType

	fi

####  	if [ -f $tumor.gexp.ary.tmpData2.tsv ]
####  	    then
####  		rm -fr $tumor.pc?.ary.$curDate.tsv
####  		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
####  			finalClin.$tumor.$curDate.tsv \
####  			$tumor.gexp.ary.tmpData2.tsv \
####  			$tumor.pc1.ary.$curDate.tsv
####  
####  ##		python $TCGAFMP_ROOT_DIR/main/jitterTSV.py \
####  ##			$tumor.pc1.ary.$curDate.tsv \
####  ##			$tumor.pc2.ary.$curDate.tsv
####  		## note that array data does not need to be jitter'd 
####  		cp $tumor.pc1.ary.$curDate.tsv $tumor.pc2.ary.$curDate.tsv
####  
####  		python $TCGAFMP_ROOT_DIR/main/copyClinInfo.py \
####  			$tumor.pc2.ary.$curDate.tsv \
####  			$tumor.pc3.ary.$curDate.tsv
####  	
####  		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
####  			$tumor.pc3.ary.$curDate.tsv \
####  			$tumor.pc4.ary.$curDate.tsv
####  	
####  		python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
####  			$tumor.pc4.ary.$curDate.tsv sampleType
####  
####  	fi

    done

echo " "
echo " fmp12B_pancan script is FINISHED !!! "
date
echo " "

