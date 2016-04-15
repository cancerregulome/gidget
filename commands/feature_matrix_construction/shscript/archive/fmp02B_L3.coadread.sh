#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
curDate=$1
snapshotName=$2

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi
if [ -z "$snapshotName" ]
    then
        echo " this script must be called with a specific snapshot-name, eg dcc-snapshot "
        exit
fi

echo " "
echo " "
echo " *******************"
echo " *" $curDate
echo " *" $snapshotName
echo " *******************"

	cd $TCGAFMP_DATA_DIR/coadread

	echo " "
	echo " "
	date
	echo " Special handling for COAD+READ "
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate

	rm -fr level3.*.*.$curDate.log

	## COPY-NUMBER
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate broad.mit.edu/genome_wide_snp_6/snp coad read $snapshotName  >& level3.broad.snp_6.$curDate.log 


echo " "
echo " fmp02B_L3.coadread script is FINISHED !!! "
date
echo " "

