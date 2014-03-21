#!/bin/bash

## NOTE: only the final 'split' by sampleType is sent to run in the background

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with a current date string such as 14jan13 (ie ddmmmyy)
curDate=$1

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi

echo " "
echo " "
echo " ***********"
echo " *" $curDate "* "
echo " ***********"

for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec
	
    do

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## these next two blocks do the same thing for the array ("ary")
	## and RNAseq ("seq") based feature matrices:
	##	a) add jitter 
	##	b) copy clinical information to all samples for a given patient
	##	c) add the sampleType feature
	##	d) split the feature matrix according to sampleType

	if [ -f $tumor.newMerge.ary.$curDate.tsv ]
	    then

		rm -fr $tumor.ary.j.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/jitterTSV.py \
			$tumor.newMerge.ary.$curDate.tsv \
			$tumor.newMerge.ary.$curDate.j.tsv >& $tumor.ary.$curDate.j.log
	
		rm -fr $tumor.ary.jc.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/copyClinInfo.py \
			$tumor.newMerge.ary.$curDate.j.tsv \
			$tumor.newMerge.ary.$curDate.jc.tsv >& $tumor.ary.$curDate.jc.log
	
		rm -fr $tumor.ary.jct.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
			$tumor.newMerge.ary.$curDate.jc.tsv \
			$tumor.newMerge.ary.$curDate.jct.tsv >& $tumor.ary.$curDate.jct.log
	
		rm -fr $tumor.ary.split.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
			$tumor.newMerge.ary.$curDate.jct.tsv sampleType >& $tumor.ary.split.$curDate.log &

	fi

	if [ -f $tumor.newMerge.seq.$curDate.tsv ]
	    then

		rm -fr $tumor.seq.j.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/jitterTSV.py \
			$tumor.newMerge.seq.$curDate.tsv \
			$tumor.newMerge.seq.$curDate.j.tsv >& $tumor.seq.$curDate.j.log
	
		rm -fr $tumor.seq.jc.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/copyClinInfo.py \
			$tumor.newMerge.seq.$curDate.j.tsv \
			$tumor.newMerge.seq.$curDate.jc.tsv >& $tumor.seq.$curDate.jc.log
	
		rm -fr $tumor.seq.jct.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
			$tumor.newMerge.seq.$curDate.jc.tsv \
			$tumor.newMerge.seq.$curDate.jct.tsv >& $tumor.seq.$curDate.jct.log
	
		rm -fr $tumor.seq.split.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
			$tumor.newMerge.seq.$curDate.jct.tsv sampleType >& $tumor.seq.split.$curDate.log &

	fi

    done

echo " "
echo " fmp07_misc script is FINISHED !!! "
date
echo " "

