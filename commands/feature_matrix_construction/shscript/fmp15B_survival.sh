#!/bin/bash

: ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}
: ${VT_UTILS:?" environment variable must be set and non-empty"}
: ${VT_SURVIVAL:?" environment variable must be set and non-empty"}

if [[ "$PYTHONPATH" != *"gidget"* ]]; then
    echo " "
    echo " your PYTHONPATH should include paths to gidget/commands/... directories "
    echo " "
    exit 99
fi

## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> "
        echo " Example : `basename $0` 28oct13  brca "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2

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
        
                if [ -f $tumor.all.$curDate.$st.tsv ]
                    then
        
                        echo " --> running survival analysis on " $tumor.all.$curDate.$st.tsv
                        rm -fr Survival.CVars.txt
                        cut -f1 $tumor.all.$curDate.$st.tsv | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
                
                        echo " "
                        head Survival.CVars.txt
                        echo " "
                
                        cd $VT_SURVIVAL
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tsv
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.all.$st.log
                        ./SurvivalPVal.sh \
                                -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.all.$curDate.$st.tsv \
                                -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                                -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                                -o $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.all.$st.log
                        grep -v "	NA" $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp | sort -gk 2 | grep -v "vital" \
                                >& $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.all.$st.tsv
        
                        head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.all.$st.tsv
                        echo " "
                        echo " "
        
        	        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
                        rm -fr SurvivalPVal.$st.tmp

                    fi

            done ## loop over st

        ## also do the non-split matrix ...
        if [ -f $tumor.all.$curDate.tsv ]
            then

                echo " "
                echo " --> running survival analysis on " $tumor.all.$curDate.tsv
                rm -fr Survival.CVars.txt
                cut -f1 $tumor.all.$curDate.tsv | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
        
                echo " "
                head Survival.CVars.txt
                echo " "
        
                cd $VT_SURVIVAL
                rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp
                rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tsv 
                rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.all.log
                ./SurvivalPVal.sh \
                        -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.all.$curDate.tsv \
                        -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                        -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                        -o $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.all.log
                grep -v "	NA" $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.tmp | sort -gk 2 | grep -v "vital" \
                        >& $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.all.tsv

                head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.all.tsv
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

