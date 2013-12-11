#!/bin/bash

: ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}

if [[ "$PYTHONPATH" != *"gidget"* ]]; then
    echo " "
    echo " your PYTHONPATH should include paths to gidget/commands/... directories "
    echo " "
    exit 99
fi

## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> "
        echo " Example : `basename $0` 28oct13  brca "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *******************"

args=("$@")
for ((i=1; i<$#; i++))
    do
        tumor=${args[$i]}

	## cd /titan/cancerregulome3/TCGA/outputs/$tumor
	cd /titan/cancerregulome14/TCGAfmp_outputs/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## these next two blocks do the same thing for the array ("ary")
	## and RNAseq ("seq") based feature matrices:
	##	a) add jitter 
	##	b) copy clinical information to all samples for a given patient
        ##      *) add custom features (new 13may13)
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
	
		rm -fr $tumor.ary.jct.$curDate.log tmp1.tsv
		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
			$tumor.newMerge.ary.$curDate.jc.tsv \
			tmp1.tsv >& $tumor.ary.$curDate.jct.log

                rm -fr tmp2.tsv $tumor.ary.$curDate.customFeat.log
                python $TCGAFMP_ROOT_DIR/main/addCustomFeat2.py \
			tmp1.tsv \
                        tmp2.tsv >> $tumor.ary.$curDate.customFeat.log

                ## python $TCGAFMP_ROOT_DIR/main/addCustomFeat3.py \
		##	tmp2.tsv \
                ##      $tumor.newMerge.ary.$curDate.jct.tsv >> $tumor.ary.$curDate.customFeat.log
                cp tmp2.tsv $tumor.newMerge.ary.$curDate.jct.tsv

		#### rm -fr $tumor.ary.split.$curDate.log
		#### python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
		####	$tumor.newMerge.ary.$curDate.jct.tsv sampleType >& $tumor.ary.split.$curDate.log 

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
	
		rm -fr $tumor.seq.jct.$curDate.log tmp1.tsv
		python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
			$tumor.newMerge.seq.$curDate.jc.tsv \
			tmp1.tsv >& $tumor.seq.$curDate.jct.log
	
                rm -fr tmp2.tsv $tumor.seq.$curDate.customFeat.log
                python $TCGAFMP_ROOT_DIR/main/addCustomFeat2.py \
			tmp1.tsv \
                        tmp2.tsv >> $tumor.seq.$curDate.customFeat.log
                python $TCGAFMP_ROOT_DIR/main/addCustomFeat3.py \
			tmp2.tsv \
                        $tumor.newMerge.seq.$curDate.jct.tsv >> $tumor.seq.$curDate.customFeat.log
                ## cp tmp2.tsv $tumor.newMerge.seq.$curDate.jct.tsv

		#### rm -fr $tumor.seq.split.$curDate.log
		#### python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
		#### 	$tumor.newMerge.seq.$curDate.jct.tsv sampleType >& $tumor.seq.split.$curDate.log 

	fi

    done

echo " "
echo " fmp07B_misc script is FINISHED !!! "
echo `date`
echo " "

