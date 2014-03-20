#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

##  
##  ## brca.BASAL + ov
##  
##  python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
##          /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
##          /titan/cancerregulome14/TCGAfmp_outputs/ov/29mar13/ov.pc4.seq.29mar13.TP.tsv \
##          /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.ov.seq.29mar13.TP.tsv
##  
##  python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
##          --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.ov.seq.29mar13.TP.tsv
##  


## brca.BASAL + gbm (all)

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/gbm/29mar13/gbm.pc4.seq.29mar13.TP.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbm.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbm.seq.29mar13.TP.tsv



## brca.BASAL + gbm.CLASSICAL

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/gbm/29mar13/gbm.pc4.seq.29mar13.TP.CLASSICAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmCLASSICAL.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmCLASSICAL.seq.29mar13.TP.tsv



## brca.BASAL + gbm.MESENCHYMAL

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/gbm/29mar13/gbm.pc4.seq.29mar13.TP.MESENCHYMAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmMESENCHYMAL.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmMESENCHYMAL.seq.29mar13.TP.tsv



## brca.BASAL + gbm.NEURAL

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/gbm/29mar13/gbm.pc4.seq.29mar13.TP.NEURAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmNEURAL.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmNEURAL.seq.29mar13.TP.tsv



## brca.BASAL + gbm.PRONEURAL

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/gbm/29mar13/gbm.pc4.seq.29mar13.TP.PRONEURAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmPRONEURAL.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.gbmPRONEURAL.seq.29mar13.TP.tsv



## brca.BASAL + brca.LUMA

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.LUMA.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.brcaLUMA.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.brcaLUMA.seq.29mar13.TP.tsv



## brca.BASAL + laml

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/laml/29mar13/laml.pc4.seq.29mar13.TB.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.laml.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.laml.seq.29mar13.TP.tsv



## brca.BASAL + lusc

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/lusc/29mar13/lusc.pc4.seq.29mar13.TB.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.lusc.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.lusc.seq.29mar13.TP.tsv


