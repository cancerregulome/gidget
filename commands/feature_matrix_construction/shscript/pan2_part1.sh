#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      snapshot name, either 'dcc-snapshot' or 'dcc-snapshot-28jun13'
##      one tumor type, eg 'ucec'
##      a config file, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [ $# != 7 ]
    then
        echo " "
        echo " This script generates a 'pancan' matrix with two tumor types "
        echo " "
        echo " Usage   : `basename $0` <curDate> <snapshotName> <config> <public/private> <tumorA> <tumorB> <outName>"
        echo " Example : `basename $0` 28oct13  dcc-snapshot-28oct13  parse_tcga.27_450k.config  public  coad  read  crc"
        exit $WRONGARGS
fi

curDate=$1
snapshotName=$2
config=$3
ppString=$4
tumorA=$5
tumorB=$6
oneTumor=$7

if [ ! -d $TCGAFMP_DATA_DIR/$oneTumor ]
    then
        echo " "
        echo "     --> creating new directory " $TCGAFMP_DATA_DIR/$oneTumor
        echo " "
        mkdir $TCGAFMP_DATA_DIR/$oneTumor
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/aux
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/gnab
        mkdir $TCGAFMP_DATA_DIR/$oneTumor/scratch

fi

cd $TCGAFMP_DATA_DIR/$oneTumor
if [ ! -d $curDate ]
    then
        mkdir $curDate
fi
cd $curDate

rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/*.$curDate.$snapshotName.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/scratch/*.$curDate.$oneTumor.log
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/$curDate/*.*

##
## NOTE: this script assumes that the "doAll" script has been run for each 
##       individual tumor types with the same $curDate and $snapshotName 
##       and $ppString *first* before starting out the multi-tumor run 
##

## -----------------------
## STEP #1 : CLINICAL DATA

rm -fr $TCGAFMP_DATA_DIR/$oneTumor/$curDate/finalClin.$oneTumor.$curDate.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/finalClin.$tumorA.$curDate.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/finalClin.$tumorB.$curDate.tsv \
    $TCGAFMP_DATA_DIR/$oneTumor/$curDate/finalClin.$oneTumor.$curDate.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.finalClin.$curDate.$oneTumor.log

## and run pairwise on it
    nohup python $TCGAFMP_ROOT_DIR/main/run-pairwise-v2.py \
        --pvalue 2. --all --forRE \
        --tsvFile $TCGAFMP_DATA_DIR/$oneTumor/$curDate/finalClin.$oneTumor.$curDate.tsv &

## --------------------------
## STEP #2 : COPY-NUMBER DATA

## do a joint re-segmentation
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $TCGAFMP_ROOT_DIR/config/$config broad.mit.edu/genome_wide_snp_6/snp/ \
    $tumorA,$tumorB $curDate $snapshotName \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/JOINT.level3.broad.snp_6.$curDate.$snapshotName.$oneTumor.log

## the output file name is a concatenation of the input tumors with
## underscores in between ... get that name here
cnvrf=`ls *.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv`

## next do the black and white-list filtering ...
    if [ -f $cnvrf ]
        then
            rm -fr filterSamp.cnvr.log
            python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
                    $cnvrf \
                    $oneTumor.cnvr.tmpData1.tsv \
                    ../../$tumorA/aux/$tumorA.blacklist.loose.tsv black loose \
                    ../../$tumorA/aux/$tumorA.whitelist.loose.tsv white loose \
                    ../../$tumorA/aux/$tumorA.whitelist.strict.tsv white strict \
                    ../../$tumorB/aux/$tumorB.blacklist.loose.tsv black loose \
                    ../../$tumorB/aux/$tumorB.whitelist.loose.tsv white loose \
                    ../../$tumorB/aux/$tumorB.whitelist.strict.tsv white strict \
                    ../../$tumorA/$curDate/$tumorA.blacklist.loose.tsv black loose \
                    ../../$tumorA/$curDate/$tumorA.whitelist.loose.tsv white loose \
                    ../../$tumorA/$curDate/$tumorA.whitelist.strict.tsv white strict \
                    ../../$tumorB/$curDate/$tumorB.blacklist.loose.tsv black loose \
                    ../../$tumorB/$curDate/$tumorB.whitelist.loose.tsv white loose \
                    ../../$tumorB/$curDate/$tumorB.whitelist.strict.tsv white strict \
                    >& filterSamp.cnvr.log
    fi

## and then annotate ...
    if [ -f $oneTumor.cnvr.tmpData1.tsv ]
        then
            rm -fr annotate.cnvr.$curDate.log
            python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
                    $oneTumor.cnvr.tmpData1.tsv hg19 \
                    $oneTumor.cnvr.tmpData3.tsv NO >& annotate.cnvr.$curDate.log
    fi



## ---------------------------------------
## STEP #3 : GENE EXPRESSION (RNAseq) DATA

## first merge ...
rm -fr $oneTumor.gexp.seq.tmpData2.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/$tumorA.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/$tumorB.gexp.seq.tmpData2.tsv \
    $oneTumor.gexp.seq.tmpData2.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.gexp.seq.tmpData2.log

## then run through a highVar filter ...
rm -fr highVar.gexp.seq.$curDate.log
python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
   $oneTumor.gexp.seq.tmpData2.tsv \
   $oneTumor.gexp.seq.tmpData3.tsv \
   0.75 IDR >& highVar.gexp.seq.$curDate.log

## ---------------------------------------
## STEP #4 : DNA METHYLATION DATA

## first merge ...
rm -fr $oneTumor.meth.tmpData2.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/$tumorA.meth.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/$tumorB.meth.tmpData2.tsv \
    $oneTumor.meth.tmpData2.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.meth.tmpData2.log

## then run through a highVar filter ...
rm -fr highVar.meth.$curDate.log
python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
   $oneTumor.meth.tmpData2.tsv \
   $oneTumor.meth.tmpData3.tsv \
   0.75 IDR >& highVar.meth.$curDate.log

## ---------------------------------------
## STEP #5 : MICRORNA (miRNAseq) DATA

## first merge ...
rm -fr $oneTumor.mirn.tmpData2.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/$tumorA.mirn.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/$tumorB.mirn.tmpData2.tsv \
    $oneTumor.mirn.tmpData2.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.mirn.tmpData2.log

## then run through two highVar filters ...
rm -fr highVar.mirn.$curDate.log
python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
   $oneTumor.mirn.tmpData2.tsv \
   $oneTumor.mirn.tmpData2b.tsv \
   0.75 NZC >& highVar.mirn1.$curDate.log
python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
   $oneTumor.mirn.tmpData2b.tsv \
   $oneTumor.mirn.tmpData3.tsv \
   0.75 IDR >& highVar.mirn2.$curDate.log

## ---------------------------------------
## STEP #5 : RPPA DATA

## all we do is merge ...
rm -fr $oneTumor.rppa.tmpData3.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/$tumorA.rppa.tmpData3.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/$tumorB.rppa.tmpData3.tsv \
    $oneTumor.rppa.tmpData3.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.rppa.tmpData3.log

## ---------------------------------------
## STEP #6 : MSI calls (if we have them)

## all we do is merge ...
rm -fr $oneTumor.msat.tmpData3.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/$curDate/$tumorA.nationwidechildrens.org__microsat_i__fragment_analysis.$curDate.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/$curDate/$tumorB.nationwidechildrens.org__microsat_i__fragment_analysis.$curDate.tsv \
    $oneTumor.msat.tmpData3.tsv \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.msat.tmpData3.log

## ---------------------------------------
## STEP #7 : GNAB (mutation) DATA

## all we do is merge ...
## AND filter so that we only keep mutations that are seen in all tumor types
rm -fr $TCGAFMP_DATA_DIR/$oneTumor/gnab/$oneTumor.gnab.filter.annot.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/$tumorA/gnab/$tumorA.gnab.filter.annot.tsv \
    $TCGAFMP_DATA_DIR/$tumorB/gnab/$tumorB.gnab.filter.annot.tsv \
    $TCGAFMP_DATA_DIR/$oneTumor/gnab/$oneTumor.gnab.filter.annot.tsv \
    rc 0.99 0.05 \
    >& $TCGAFMP_DATA_DIR/$oneTumor/scratch/MERGE.$oneTumor.gnab.filter.annot.log

## at this point we should be able to revert to the "normal" pipeline starting at step fmp06B ...


