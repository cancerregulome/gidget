#!/bin/bash

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
echo " *" $curDate "* "
echo " ***********"

for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec

    do

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
			g=$tumor.$p.$curDate.NT.tsv
			if [ -f $g ]
			    then
				h=${f/.tsv/.NT.tsv}
				o=${f/.tsv/.NT.log}
				python $TCGAFMP_ROOT_DIR/main/mergeTSV.py $f $g $h >& $o
			    fi
		    done

	    done

    done

echo " "
echo " fmp11_mergeNT script is FINISHED !!! "
date
echo " "

