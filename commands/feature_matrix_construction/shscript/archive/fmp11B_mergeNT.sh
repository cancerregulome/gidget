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
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## loop over the 'ary' and 'seq' possibilities ...
	for p in ary seq
	    do

		## for all tumor-only subtype files
		for f in $tumor.$p.$curDate.T?.*.tsv
		    do

			if [ -f $f ]
			    then
				if [[ "$f" == *.NT.* ]]
				    then
				        echo " skipping " $f
				    else

					g=$tumor.$p.$curDate.NT.tsv
					if [ -f $g ]
					    then
						h=${f/.tsv/.NT.tsv}
						o=${f/.tsv/.NT.log}
						python $TCGAFMP_ROOT_DIR/main/mergeTSV.py $f $g $h >& $o
					    fi

				    fi

			fi
		    done

	    done

	## these files are being created somewhat accidentally ...
	rm -fr $tumor.$p.$curDate.*.NT.NT.tsv
	rm -fr $tumor.$p.$curDate.*.NT.NT.log

    done

echo " "
echo " fmp11B_mergeNT script is FINISHED !!! "
date
echo " "

