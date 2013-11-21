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
echo `date`
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

##      for st in XX
        for st in TP TB TR TM allT XX
            do

                ## ------------------------------------------------------------------- #
                echo " "
                echo "     looping over subset " $st
        
                if [ -f $tumor.seq.$curDate.$st.tsv ]
                    then
        
                        echo " --> running survival analysis on " $tumor.seq.$curDate.$st.tsv
                        rm -fr Survival.CVars.txt
                        cut -f1 $tumor.seq.$curDate.$st.tsv | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
                
                        echo " "
                        head Survival.CVars.txt
                        echo " "
                
                        cd /users/sreynold/git_home/vt_cncreg/survival
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tsv
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.$st.log
                        ./SurvivalPVal.sh \
                                -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.seq.$curDate.$st.tsv \
                                -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                                -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                                -o $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.$st.log
                        grep -v "	NA" $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp | sort -gk 2 | grep -v "vital" \
                                >& $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.$st.tsv
        
                        head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.$st.tsv
                        echo " "
                        echo " "
        
        	        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
                        rm -fr SurvivalPVal.$st.tmp

                    fi

            done ## loop over st

        ## also do the non-split matrix ...
        if [ -f $tumor.seq.$curDate.tsv ]
            then

                echo " "
                echo " --> running survival analysis on " $tumor.seq.$curDate.tsv
                rm -fr Survival.CVars.txt
                cut -f1 $tumor.seq.$curDate.tsv | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
        
                echo " "
                head Survival.CVars.txt
                echo " "
        
                cd /users/sreynold/git_home/vt_cncreg/survival
                rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp
                rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tsv 
                rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.log
                ./SurvivalPVal.sh \
                        -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.seq.$curDate.tsv \
                        -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                        -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                        -o $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.seq.log
                grep -v "	NA" $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp | sort -gk 2 | grep -v "vital" \
                        >& $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.tsv

                head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.seq.tsv
                echo " "
                echo " "

	        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
                rm -fr SurvivalPVal.tmp

            fi

                
    done ## loop over tumor

echo " "
echo " fmp15B_survival script is FINISHED !!! "
echo `date`
echo " "

