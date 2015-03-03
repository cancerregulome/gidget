#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


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

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate
	echo `pwd`
	echo " "

	for f in $tumor.newMerge.???.$curDate.jct.*tsv
	    do

		## for some reason it seems to be possible to get here
		## with a filename in $f that does not actually exist!
		if [ -f $f ]
		    then

			## the output file name will be identical to the input file
			## name with the exception of the extra letter 'm' after 'jct'
			g=${f/.jct./.jctm.}
			h=${g/.tsv/.log}
			echo " "
                        date
			echo $f
			echo $g
			echo $h
			python $TCGAFMP_ROOT_DIR/main/checkMethCnvr.py $f $g >& $h 

                        ## and add the summary methylation feature
                        rm -fr sm.tsv
                        python $TCGAFMP_ROOT_DIR/main/summaryMeth.py $g sm.tsv >> $h
                        rm -fr $g
                        mv sm.tsv $g

		fi

	    done

echo " "
echo " fmp08B_checkMeth script is FINISHED !!! "
echo `date`
echo " "

