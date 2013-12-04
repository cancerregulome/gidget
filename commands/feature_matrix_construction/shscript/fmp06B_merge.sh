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

        ## 06nov13 NEW: if the file $tumor.meth.filt.annot.forTSVmerge.tsv
        ## exists in the $tumor/aux/ directory, then we will NOT use
        ## the methylation file created by the pipeline as is ...
        if [ -f ../aux/$tumor.meth.filt.annot.forTSVmerge.tsv ]
            then
                mv $tumor.meth.tmpData3.tsv $tumor.meth.tmpData3.tsv_obsolete
        fi

	## NOTE: within data types (eg mRNA expression, methylation, microRNA),
	## if there are duplicate samples/values between separate input data
	## matrices, the first value will take precedence ... so these files
	## are listed in order of most-recent-platform first

	## using the finalClin.$tumor.$curDate.tsv file instead of
	##       the vitalStats.$tumor.$curDate.tsv file ...

	rm -fr $tumor.newMerge.???.$curDate.log
	rm -fr $tumor.newMerge.???.$curDate.tsv
        rm -fr $tumor.newMerge*.$curDate.*tsv

        ## here we build the merged matrix using only sequencing-based data (if it exists)
	if [ -f $tumor.gexp.seq.tmpData3.tsv ]
	    then
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			finalClin.$tumor.$curDate.tsv \
			$tumor.mirn.tmpData3.tsv \
			$tumor.cnvr.tmpData3.tsv \
			$tumor.meth.tmpData3.tsv \
			$tumor.rppa.tmpData3.tsv \
			$tumor.msat.tmpData3.tsv \
			$tumor.gexp.seq.tmpData3.tsv \
			../gnab/$tumor.gnab.tmpData4b.tsv \
			`ls ../aux/*.forTSVmerge.tsv` \
			$tumor.newMerge.seq.$curDate.tsv >& $tumor.newMerge.seq.$curDate.log 
	fi

        ## here we build the merged matrix using only array-based data (if it exists)
	if [ -f $tumor.gexp.ary.tmpData3.tsv ]
	    then
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			finalClin.$tumor.$curDate.tsv \
			$tumor.mirn.tmpData3.tsv \
			$tumor.cnvr.tmpData3.tsv \
			$tumor.meth.tmpData3.tsv \
			$tumor.rppa.tmpData3.tsv \
			$tumor.msat.tmpData3.tsv \
			$tumor.gexp.ary.tmpData3.tsv \
			../gnab/$tumor.gnab.tmpData4b.tsv \
			`ls ../aux/*.forTSVmerge.tsv` \
			$tumor.newMerge.ary.$curDate.tsv >& $tumor.newMerge.ary.$curDate.log 
	fi

        ## here we build the merged matrix using both types of data (whatever exists)
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			finalClin.$tumor.$curDate.tsv \
			$tumor.mirn.tmpData3.tsv \
			$tumor.cnvr.tmpData3.tsv \
			$tumor.meth.tmpData3.tsv \
			$tumor.rppa.tmpData3.tsv \
			$tumor.msat.tmpData3.tsv \
			$tumor.gexp.ary.tmpData3.tsv \
			$tumor.gexp.seq.tmpData3.tsv \
			../gnab/$tumor.gnab.tmpData4b.tsv \
			`ls ../aux/*.forTSVmerge.tsv` \
			$tumor.newMerge.all.$curDate.tsv >& $tumor.newMerge.all.$curDate.log 

    done

echo " "
echo " fmp06B_merge script is FINISHED !!! "
echo `date`
echo " "

