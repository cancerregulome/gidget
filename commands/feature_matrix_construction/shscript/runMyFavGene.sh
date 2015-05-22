#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##	date, eg '29jan13'
##	snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##	one or more tumor types, eg: 'prad,thca,skcm,stad'
##	config, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [[ $# != 6 ]] && [[ $# != 6 ]]
    then
        echo " Usage   : `basename $0` <gene> <chrName> <start> <stop> <runID> <cancer1,cancer2,...> "
        echo " Example : `basename $0` KRAS chr12 25357723 25403870 20140818_public  brca,kirc,luad,ov,lusc,ucec,gbm "
        echo " "
        exit $WRONGARGS
fi

## these parameters identify the 'favorite' gene and it's genomic coordinates
geneSymbol=$1
chrName=$2
startPos=$3
stopPos=$4

## these paramters identify the TSV files that will be looked at
runID=$5
tumors=$(echo $6 | tr "," "\n")

echo " "
echo " "
echo " *******************"
echo `date`
echo " * gene symbol ...... " $geneSymbol
echo " * coordinates ...... " $chrName $startPos $stopPos
echo " * run id ........... " $runID
echo " * tumor ............ " $tumors
echo " *******************"

cd /local/sreynold/scratch/myFavGene

args=("$@")
for tumor in $tumors
    do 

        echo " TUMOR " $tumor
        rm -fr $geneSymbol.$tumor.t*
        rm -fr $geneSymbol.$tumor.log

        python $TCGAFMP_ROOT_DIR/main/findFeatList.py \
            $TCGAFMP_DATA_DIR/$tumor/$runID/$tumor.all.$runID.tsv \
            $geneSymbol $chrName $startPos $stopPos >& $geneSymbol.$tumor.t1

        featNames=`grep -v "^##" $geneSymbol.$tumor.t1`
        ii=0
        for aName in $featNames
            do
                echo "     RUNNING PAIRWISE "$ii $aName
                python $TCGAFMP_ROOT_DIR/main/run-pairwise-v2.py \
                    --pvalue 2. --one $aName \
                    --tsvFile $TCGAFMP_DATA_DIR/$tumor/$runID/$tumor.all.$runID.tsv \
                    --outFile /local/sreynold/scratch/myFavGene/$geneSymbol.$tumor.scratch.$ii >> $geneSymbol.$tumor.log
                ((ii++))
            done

        cat $geneSymbol.$tumor.scratch.* | sort | uniq | sort -grk 5 >& $geneSymbol.$tumor.pw.all.sort
        rm -fr $geneSymbol.$tumor.scratch.*

    done

echo " "
echo " runMyFavGene script is FINISHED !!! "
echo `date`
echo " "

