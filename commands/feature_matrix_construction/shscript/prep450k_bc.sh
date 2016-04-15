#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      one tumor type (eg 'skcm')
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      optionally a 3rd argument that gives the name of a different methylation data file to be used

WRONGARGS=1
if [[ $# != 3 ]] && [[ $# != 2 ]]
    then
        echo " Usage   : `basename $0` <tumorType> <snapshotName> [meth tsv]"
        echo " Example : `basename $0` skcm dcc-snapshot-06jan14"
        echo "           for a non-standard methylation data source, use the 3rd argument to specify a path "
        echo " "
        echo " ******************************************************************************************* "
        echo " ** ALSO PLEASE BE FOREWARNED THAT THIS SCRIPT TYPICALLY TAKES ABOUT 12 HOURS to COMPLETE ** "
        echo " ******************************************************************************************* "
        echo " "
        exit $WRONGARGS
fi

tumor=$1
snapshotName=$2

if (( $# == 3 ))
    then
        specialMethFile=$3
    else
        specialMethFile=NA
fi

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" output directory: $TCGAFMP_DATA_DIR
echo " *" $tumor
echo " *" $snapshotName
echo " *******************"

cd $TCGAFMP_DATA_DIR/$tumor
mkdir meth450k
cd meth450k

## do some clean-up so that we can tell what is new ...
rm -fr *.log
rm -fr *.tsv

CONFIG_FILE=$TCGAFMP_ROOT_DIR/config/parse_tcga.all450k.config

## first we need to get the 450k data and the GEXP and MIRN data ...
## for a typical tumor, this step will take ~45 minutes

echo " "
echo " Step #1: parse the 450k, RNAseq and miRNAseq data "

if [[ $specialMethFile == "NA" ]]
    then
        date
        python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
            $CONFIG_FILE \
            jhu-usc.edu/humanmethylation450/methylation/ \
            $tumor meth450k dcc-snapshot >& level3.meth450.log 
        ## at this point, we should have an output file with ~482k rows
        grep "finished in writeTSV_dataMatrix" level3.meth450.log
        methFilename=$tumor.jhu-usc.edu__humanmethylation450__methylation.meth450k.tsv
    else
        date
        echo " skipping parsing of DCC-MIRROR 450k data "
        methFilename=$specialMethFile
fi
echo " methylation data file : " $methFilename

date
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $CONFIG_FILE \
    bcgsc.ca/illuminahiseq_rnaseq/rnaseq/ \
    $tumor meth450k dcc-snapshot >& level3.rnaseq.log 
# and here we should have an output file with ~20k rows
grep "finished in writeTSV_dataMatrix" level3.rnaseq.log

date
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $CONFIG_FILE \
    bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/ \
    $tumor meth450k dcc-snapshot >& level3.mirn.log 
# and here we should have an output file with ~1200 rows
grep "finished in writeTSV_dataMatrix" level3.mirn.log

## for f in *.tsv
##     do
##         echo $TCGAFMP_ROOT_DIR/shscript/fmp00B_hackBarcodes.sh $f
##     done

## then we annotate the GEXP and MIRN data ... because we need
## to have the genomic coordinates for these features ...
## the size of these matrices should not change
## for a typical tumor, this step will take ~10 minutes

echo " Step #2: annotate the RNAseq and miRNAseq feature names "

date
python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
    $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.meth450k.tsv \
    hg19 $tumor.gexp.annot.tsv NO >& $tumor.gexp.annot.log

date
python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
    $tumor.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.meth450k.tsv \
    hg19 $tumor.mirn.annot.tsv NO >& $tumor.mirn.annot.log

## next we need to merge these 3 matrices ... 
## this can be fairly time-consuming ... for a typical tumor maybe ~3h
date
rm -fr $tumor.meth_gexp_mirn.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $methFilename \
    $tumor.gexp.annot.tsv \
    $tumor.mirn.annot.tsv \
    $tumor.meth_gexp_mirn.tsv >& $tumor.meth_gexp_mirn.log

## and then the filtering ... this is the slowest step in this entire
## process and takes something like 8 hours
##      default parameters: dThresh = 10000 (10kb between GEXP/MIRN and METH feature)
##                          minCount = 30 (require at least 30 data samples)
##                          corrThresh = 0.30 (require |rho| >= 0.30)

echo " Step #3: filter by local correlations and by variability "
date
python $TCGAFMP_ROOT_DIR/main/doMethCorr.py \
    $tumor.meth_gexp_mirn.tsv \
    $tumor.meth_gexp_mirn.filtA.tsv \
    10000 30 0.30 >& filtA.log 
grep "'N:METH': " filtA.log

## another type of filtering ... takes ~2h
date
python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
    $methFilename \
    meth.hv02.tsv 0.02 IDR >& meth.hv02.log 
grep "'N:METH': " meth.hv02.log

## and then merge that in ... this is very quick
echo " Step #4: merge high-variability and other significant features "
date
rm -fr $tumor.meth_gexp_mirn.plus.tsv
python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $tumor.meth_gexp_mirn.filtA.tsv \
    meth.hv02.tsv \
    $tumor.meth_gexp_mirn.plus.tsv >& merge.plus.log
grep "'N:METH': " merge.plus.log


## and finally annotate ... this takes ~15 min
echo " Step #5: annotate final feature matrix "
date
python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
    $tumor.meth_gexp_mirn.plus.tsv hg19 \
    $tumor.meth_gexp_mirn.plus.annot.tsv NO >& annot.log
grep "'N:METH': " annot.log


echo " "
echo " prep450k script is FINISHED !!! "
echo `date`
echo " "

