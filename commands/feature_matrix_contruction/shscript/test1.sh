#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## BRCA.basal + OV

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
        /titan/cancerregulome14/TCGAfmp_outputs/brca/29mar13/brca.pc4.seq.29mar13.TP.BASAL.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/ov/29mar13/ov.pc4.seq.29mar13.TP.tsv \
        /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.ov.seq.29mar13.TP.tsv

python $TCGAFMP_ROOT_DIR/main/run_pwRK2.py --pvalue 1.e-06 --forLisa \
        --tsvFile /titan/cancerregulome14/TCGAfmp_outputs/pancan/29mar13/brcaBASAL.ov.seq.29mar13.TP.tsv

