#!/bin/bash

## NOTE: only the "ary" (array-based gene expression feature matrix) merge is sent 
## to run in the background ... the more common "seq" merge's are done one at a
## time ...

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
echo `date`
echo " *" $curDate "* "
echo " ***********"

## for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec
for tumor in skcm stad thca ucec

    do

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## NOTE: within data types (eg mRNA expression, methylation, microRNA),
	## if there are duplicate samples/values between separate input data
	## matrices, the first value will take precedence ... so these files
	## are listed in order of most-recent-platform first

	## using the finalClin.$tumor.$curDate.tsv file instead of
	##       the vitalStats.$tumor.$curDate.tsv file ...

	rm -fr $tumor.newMerge.???.$curDate.log
	rm -fr $tumor.newMerge.???.$curDate.tsv

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
			../gnab/$tumor.gnab.filter.annot.tsv \
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
			../gnab/$tumor.gnab.filter.annot.tsv \
			$tumor.newMerge.ary.$curDate.tsv >& $tumor.newMerge.ary.$curDate.log &
	fi

    done

echo " "
echo " fmp06_merge script is FINISHED !!! "
echo `date`
echo " "

