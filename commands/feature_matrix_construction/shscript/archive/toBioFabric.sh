#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH


## this script should be called with the following parameters:
##	date, eg '29jan13'
##	snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##	one or more tumor types, eg: 'prad thca skcm stad'
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
        pwd

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate
        pwd

        ls -alt finalClin.$tumor.$curDate.pwpv.forRE

        rm -fr t1 t1? t2 t3 t4 t5
        grep -v ":I(" finalClin.$tumor.$curDate.pwpv.forRE | \
                grep -v "Arm_r" | grep -v "ROI_r" | grep -v "_sv:" >& t1
        cut -f1 t1 >& t11
        cut -f2 t1 >& t12
        cut -f4 t1 >& t14
        cut -f5 t1 >& t15

        paste t11 t15 t12 | grep -v "	2\." | \
                grep -v "	1\." | \
                grep -v "	0\." | \
                grep -v "	-0\.0	" | \
                sed -e '1,$s/::::://g' >& t2
	
        grep -v "Gistic" t2 >& t3
        grep    "Gistic" t2 | grep -v "	3\." | grep -v "	4\." | grep -v "	5\." >& t4

        grep "^C:CNVR:" t4 | grep "	C:CNVR:" | grep -v "GisticArm" >& t5

        rm -fr ~/scratch/BioFabric/$tumor.$curDate.*.sif
        mv t3 ~/scratch/BioFabric/$tumor.$curDate.noGistic.sif
        mv t4 ~/scratch/BioFabric/$tumor.$curDate.Gistic.sif
        mv t5 ~/scratch/BioFabric/$tumor.$curDate.onlyROI.sif
        wc -l ~/scratch/BioFabric/$tumor.$curDate.*.sif

    done

echo " "
echo " toBioFabric script is FINISHED !!! "
date
echo " "

