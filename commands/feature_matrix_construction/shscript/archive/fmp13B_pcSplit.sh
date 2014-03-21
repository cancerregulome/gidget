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

        s=$(<../aux/splitType.txt)
        if [ -z "$s" ]
            then
                echo " no splitType specified "
            else
                echo " splitType is $s"
        fi


	## this code is for Lisa's pancan analysis ... here we are making
	## the subtype files ...

	for f in $tumor.pc4.???.$curDate.T?.tsv
	    do

		if [ -f $f ]
		    then

			if [ -z "$s" ]
			    then
			        echo " "
			    else
			        echo " splitting " $f $s
				python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py $f $s
			fi
		fi
	    done

    done

echo " "
echo " fmp13B_pcSplit script is FINISHED !!! "
date
echo " "

