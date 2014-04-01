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


        for p in seq ary
            do

                for st in TP TM TB allT
                    do

                        if [ -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.$p.$curDate.$st.tsv ]
                            then

                                echo " "
                                echo " "
                                echo " ******************************************************************* "
                                date
                                echo $tumor $p $st
                                nohup python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --all --forRE \
                                        --tsvFile $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.$p.$curDate.$st.tsv &
                                sleep 2000

                            fi
                    done
            done
    done


