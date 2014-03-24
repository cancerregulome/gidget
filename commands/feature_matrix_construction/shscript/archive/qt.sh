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
echo " *" $curDate
echo " *******************"

args=("$@")
for ((i=1; i<$#; i++))
    do
        tumor=${args[$i]}

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	cd $curDate

	if [[ -f $tumor.gexp.seq.tmpA.tsv || -f $tumor.gexp.seq.tmpB.tsv || -f $tumor.gexp.seq.tmpC.tsv ]]
	    then
		echo "         merging seq A B C "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpA.tsv \
			$tumor.gexp.seq.tmpB.tsv \
			$tumor.gexp.seq.tmpC.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    else
		echo "         merging seq D E "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpD.tsv \
			$tumor.gexp.seq.tmpE.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    fi

    done

echo " "
echo " fmp05B_filter script is FINISHED !!! "
date

