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

		fi

	    done

    done

echo " "
echo " fmp08B_checkMeth script is FINISHED !!! "
echo `date`
echo " "

