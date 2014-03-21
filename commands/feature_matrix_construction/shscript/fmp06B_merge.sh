#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [ $# != 3 ]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> <public/private> "
        echo " Example : `basename $0` 28oct13  brca  private "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2
ppString=$3

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *******************"


	## cd /titan/cancerregulome3/TCGA/outputs/$tumor
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
        rm -fr $tumor.newMerge*.$curDate.*tsv

        auxFiles=''
        if [ "$ppString" = 'private' ]
            then
                auxFiles=`ls ../aux/*.forTSVmerge.tsv`
            fi

        echo " "
        echo " **** "
        echo " auxFiles : "
        echo $auxFiles
        echo " **** "
        echo " "

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
			$auxFiles \
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
			$auxFiles \
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
			$auxFiles \
			$tumor.newMerge.all.$curDate.tsv >& $tumor.newMerge.all.$curDate.log 


echo " "
echo " fmp06B_merge script is FINISHED !!! "
echo `date`
echo " "

