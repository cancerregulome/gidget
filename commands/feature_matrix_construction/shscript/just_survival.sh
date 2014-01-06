#!/bin/bash

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      tumor type, eg 'gbm'
##      tsvFile name, eg 'gbm.ary.29jan13.tsv'
curDate=$1
tumor=$2
tsvFile=$3

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi
if [ -z "$tumor" ]
    then
        echo " this script must be called with one tumor type "
        exit
fi
if [ -z "$tsvFile" ]
    then
        echo " this script must be called with TSV file specified "
        exit
fi

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *******************"



        echo " "
        echo " *************************************************************** "
	echo " "
	echo " Tumor Type " $tumor
	echo " "
	date
        echo " "

	cd $TCGAFMP_DATA_DIR/$tumor/$curDate
        pwd

        for st in XX
            do

                ## ------------------------------------------------------------------- #
                echo " "
        
                if [ -f $tsvFile ]
                    then
        
                        echo " --> running survival analysis on " $tsvFile
                        rm -fr Survival.CVars.txt
                        cut -f1 $tsvFile | grep -v "^N:" | grep -v "^M:" | grep -v "vital_status" | sort >& Survival.CVars.txt
                
                        echo " "
                        head Survival.CVars.txt
                        echo " "

                        g=${tsvFile/.tsv/.SurvivalPVal.tsv}
                
                        cd $VT_SURVIVAL
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp
                        rm -fr $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.$st.log

                        echo " "
                        echo " ready to invoke SurvivalPVal.sh ... "
                        echo $tsvFile
                        wc -l $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt
                        cat $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt

                        ./SurvivalPVal.sh \
                                -f $TCGAFMP_DATA_DIR/$tumor/$curDate/$tsvFile \
                                -c $TCGAFMP_DATA_DIR/$tumor/$curDate/Survival.CVars.txt \
                                -m $TCGAFMP_DATA_DIR/$tumor/aux/survival.feat.txt \
                                -o $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp >& $TCGAFMP_DATA_DIR/$tumor/scratch/SurvivalPVal.$st.log

                        rm -fr $TCGAFMP_DATA_DIR/$tumor/$curDate/$g
                        grep -v "	NA" $TCGAFMP_DATA_DIR/$tumor/$curDate/SurvivalPVal.$st.tmp | sort -gk 2 | grep -v "vital" \
                                >& $TCGAFMP_DATA_DIR/$tumor/$curDate/$g
        
                        head -5 $TCGAFMP_DATA_DIR/$tumor/$curDate/$g
                        echo " "
                        echo " "
        
        	        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
                        rm -fr SurvivalPVal.$st.tmp

                    fi

            done ## loop over st (not really)



echo " "
echo " just_survival script is FINISHED !!! "
echo `date`
echo " "

