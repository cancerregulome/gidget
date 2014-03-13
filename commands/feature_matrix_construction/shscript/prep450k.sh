#!/bin/bash

: ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}

if [[ "$PYTHONPATH" != *"gidget"* ]]; then
    echo " "
    echo " your PYTHONPATH should include paths to gidget/commands/... directories "
    echo " "
    exit 99
fi

## this script should be called with the following parameters:
##      one tumor type (eg 'skcm')
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      (if the snapshotName is not provided, it will default to the most recent)

WRONGARGS=1
if [[ $# != 3 ]] && [[ $# != 2 ]]
    then
        echo " Usage   : `basename $0` <tgca FMP output directory> <tumorType> <snapshotName> "
        echo " Example : `basename $0` <path-to-tgca-fmp> skcm dcc-snapshot-06jan14 "
        echo "           the snapshotName is optional and defaults to dcc-snapshot "
        echo "           <path-to-tgca-fmp> should contain a subdir named as the given tumorType"
        exit $WRONGARGS
fi

TCGA_FMP_OUTPUT_DIR=$1
tumor=$2
if [ $# == 2 ]
    then
        snapshotName=dcc-snapshot
    else
        snapshotName=$3
fi

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" output directory: $TCGA_FMP_OUTPUT_DIR
echo " *" $tumor
echo " *" $snapshotName
echo " *******************"

cd $TCGA_FMP_OUTPUT_DIR/$tumor
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

date
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $CONFIG_FILE \
    jhu-usc.edu/humanmethylation450/methylation/ \
    $tumor meth450k dcc-snapshot >& level3.meth450.log 
## at this point, we should have an output file with ~482k rows
grep "finished in writeTSV_dataMatrix" level3.meth450.log

date
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $CONFIG_FILE \
    unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/ \
    $tumor meth450k dcc-snapshot >& level3.rnaseqv2.log 
# and here we should have an output file with ~20k rows
grep "finished in writeTSV_dataMatrix" level3.rnaseqv2.log

date
python $TCGAFMP_ROOT_DIR/main/parse_tcga.py \
    $CONFIG_FILE \
    bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/ \
    $tumor meth450k dcc-snapshot >& level3.mirn.log 
# and here we should have an output file with ~1200 rows
grep "finished in writeTSV_dataMatrix" level3.mirn.log

for f in *.tsv
    do
        echo $TCGAFMP_ROOT_DIR/shscript/fmp00B_hackBarcodes.sh $f
    done

## then we annotate the GEXP and MIRN data ... because we need
## to have the genomic coordinates for these features ...
## the size of these matrices should not change
## for a typical tumor, this step will take ~10 minutes

echo " Step #2: annotate the RNAseq and miRNAseq feature names "

date
python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
    $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.meth450k.tsv \
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
    $tumor.jhu-usc.edu__humanmethylation450__methylation.meth450k.tsv \
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
    $tumor.jhu-usc.edu__humanmethylation450__methylation.meth450k.tsv \
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

