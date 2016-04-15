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

	s=$(<../aux/splitType.txt)
	if [ -z "$s" ]
	    then
	        echo " no splitType specified "
	    else
		echo " splitType is $s"
	fi

	## for all jctmg tsv files ...
	for f in $tumor.newMerge.???.$curDate.jctmg.*tsv
	    do

		## remove the 'jctmg' and the 'newMerge' from the name and rename
		g=${f/.jctmg./.}
		k=${g/.newMerge./.}

		echo " "
		echo "mv $f $k"
		mv $f $k


	    done

	## now, for all tumor-only files
	for f in $tumor.???.$curDate.T?.tsv
	    do

		h=${f/.tsv/.split.log}

		if [ -z "$s" ]
		    then
			echo " "
		    else
			echo " "
			echo "python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py $f $s >& $h &"
			python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py $f $s >& $h &
			sleep 600
		fi


	    done

    done

echo " "
echo " fmp10_splitType script is FINISHED !!! "
date
echo " "

