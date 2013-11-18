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

    done

echo " "
echo " fmp06B_merge script is FINISHED !!! "
echo `date`
echo " "

