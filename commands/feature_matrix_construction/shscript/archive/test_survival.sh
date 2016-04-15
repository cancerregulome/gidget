#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH
export VT_UTIL=/users/sreynold/git_home/vt_foo

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

        echo " "
        echo " *************************************************************** "
	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $TCGAFMP_DATA_DIR/$tumor/$curDate
        pwd

##      for st in TP TB TR TM allT XX
        for st in 20130502_sampleList
            do

                ## ------------------------------------------------------------------- #
        
                if [ -f $tumor.seq.$curDate.$st.tsv ]
                    then
        
                        echo " "
                        echo " --> running survival analysis on " $tumor.seq.$curDate.$st.tsv
                        rm -fr Survival.CVars.txt
                        cut -f1 $tumor.seq.$curDate.$st.tsv | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
                
                        echo " "
                        head Survival.CVars.txt
                        echo " "
                
                        cd /users/sreynold/git_home/vt_bar/survival
                        rm -fr SurvivalPVal.$st.tsv SurvivalPlot.png
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.$st.log
                        ./SurvivalPVal.sh \
                                -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.seq.$curDate.$st.tsv \
                                -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                                -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                                -o SurvivalPVal.$st.tsv >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.$st.log
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tsv
                        grep -v "	NA" SurvivalPVal.$st.tsv | sort -gk 2 | grep -v "vital" \
                                >& $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.$st.tsv
        
                        head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.$st.tsv
                        echo " "
                        echo " "
        
        	        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
        
                    fi

            done ## loop over st

    done ## loop over tumor

echo " "
date
echo " "

