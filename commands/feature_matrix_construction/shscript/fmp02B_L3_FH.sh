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
	date
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate

        ## REMOVING THIS ... will need to figure out if/where the MSI information comes
        ## from in firehose ... perhaps it has been added to the clinical data ???
	## MICRO-SATELLITE INSTABILITY
        #### rm -fr level3.nwc.microsat_i.$curDate.log
	#### python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate nationwidechildrens.org/microsat_i/fragment_analysis $tumor $snapshotName >& level3.nwc.microsat_i.$curDate.log 

    done

echo " "
echo " fmp02B_L3_FH script is FINISHED !!! "
echo `date`
echo " "

