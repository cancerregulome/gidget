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
	echo " "

	cd $curDate

        ## first we merge all of the 'all_data_by_genes' files
        rm -fr t1.tsv t2.tsv
        rm -fr merge.gs1.log
        echo "     --> merging all_data_by_genes files "
        echo `ls gdac.broad*all_data_by_genes.txt`
        python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
            `ls gdac.broad*all_data_by_genes.txt` t1.tsv >> merge.gs1.log

        ## and then we annotate the merged file ...
        rm -fr annot.gs.log
        echo "     --> annotating with gene coordinates " 
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py t1.tsv hg19 t2.tsv >> annot.gs.log
        rm -fr t1.tsv

        ## and now we swap out the CNVR features in the "all" feature matrices
        rm -fr merge.gs2.log
        for f in $tumor.???.$curDate.tsv
            do
                if [ -f $f ]
                    then

                        date
                        echo " --> swapping out CNVR features " $f
                        rm -fr u1 u2 u3.tsv
                        grep -v ":CNVR:" $f > u1
                        grep "Gistic" $f > u2
                        cat u1 u2 > u3.tsv
                        rm -fr u1 u2

                        g=${f/.tsv/.genespot.tsv}

                        rm -fr $g
                        python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
                            u3.tsv t2.tsv $g >> merge.gs2.log

                        rm -fr u3.tsv 

                    fi

            done
        rm -fr t2.tsv

    done


echo " "
echo " fmp17B_genespot script is FINISHED !!! "
date
echo " "
echo " "

