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

        rm -fr filterFeat.log
        for f in $tumor.seq.$curDate.*tsv
            do

                if [ -f $f ]
                    then

                        echo " --> filtering " $f

	                rm -fr tmpff.tsv 
		        python $TCGAFMP_ROOT_DIR/main/filterTSVbyFeatList.py \
			    $f tmpff.tsv \
	                    ../aux/$tumor.features.blacklist.loose.tsv  black loose \
	                    ../aux/$tumor.features.blacklist.strict.tsv black strict \
	                    ../aux/$tumor.features.whitelist.loose.tsv  white loose \
	                    ../aux/$tumor.features.whitelist.strict.tsv white strict \
	                    >> filterFeat.log
	
	                mv tmpff.tsv $f
	
		        python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			    $f tmpff.tsv \
	                    $tumor.blacklist.samples.tsv black loose \
	                    ../aux/$tumor.blacklist.loose.tsv  black loose \
	                    ../aux/$tumor.blacklist.strict.tsv black strict \
	                    ../aux/$tumor.whitelist.loose.tsv  white loose \
	                    ../aux/$tumor.whitelist.strict.tsv white strict \
	                    >> filterFeat.log
	
                        python $TCGAFMP_ROOT_DIR/main/addIndicators.py tmpff.tsv $f >& final.addI.log
                        rm -fr tmpff.tsv

                    fi

            done

    done


echo " "
echo " fmp16B_finalFilter script is FINISHED !!! "
date
echo " "
echo " "

