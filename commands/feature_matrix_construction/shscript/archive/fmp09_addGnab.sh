#!/bin/bash

## NOTE: this script kicks off all 'addGnabFeatures' runs to run in the background,
## and just has a 'sleep' command to try to prevent the machine from getting
## swamped, while also taking advantage of multiple CPUs ...

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

## for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec
for tumor in lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec

    do

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

	for f in $tumor.newMerge.???.$curDate.jctm.*tsv
	    do
		## the output file name will be identical to the input file
		## name with the exception of the extra letter 'g' after 'jctm'
		g=${f/.jctm./.jctmg.}
		h=${g/.tsv/.log}
		python $TCGAFMP_ROOT_DIR/main/addGnabFeatures.py $f $g >& $h &
		sleep 100
	    done

    done

echo " "
echo " fmp09_addGnab script is FINISHED !!! "
date
echo " "

