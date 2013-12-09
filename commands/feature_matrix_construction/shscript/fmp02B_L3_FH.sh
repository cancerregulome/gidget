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
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad thca skcm stad'

WRONGARGS=1
if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <curDate>  <tumorType> "
        echo " Example : `basename $0` 28oct13  brca "
        exit $WRONGARGS
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

