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

    done

echo " "
echo " fmp08B_checkMeth script is FINISHED !!! "
echo `date`
echo " "

